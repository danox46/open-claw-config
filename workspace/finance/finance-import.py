#!/usr/bin/env python3
"""
finance-import.py — Parse Bancolombia notification records and import into MongoDB.

Reads raw notification records from a JSON file (default: samples-raw.json),
parses each one, applies enrichment (merchant rules → auto-match → unclassified),
validates item integrity, and inserts into MongoDB.

Designed for unattended / low-tier-model use: skips unparseable records with a
clear error message rather than crashing, and never double-inserts.

Usage:
  python3 finance-import.py [--input FILE] [--since YYYY-MM-DD] [--until YYYY-MM-DD]
                             [--dry-run] [--debug]

Options:
  --input FILE      Raw JSON file (default: samples-raw.json next to this script)
  --since DATE      Only process records with email date >= DATE (UTC, YYYY-MM-DD)
  --until DATE      Only process records with email date <= DATE (UTC, YYYY-MM-DD)
  --dry-run         Print plan without writing anything to DB
  --debug           Print detailed parse info for every record

Exit codes:
  0  Completed; check output for per-record SKIP / INSERT / ERROR lines
  1  One or more records had unrecoverable parse errors (skipped, rest continue)
  2  Fatal startup error (no DB connection, missing input file, etc.)
"""

import sys
import re
import json
import argparse
import os
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# MongoDB config
# ---------------------------------------------------------------------------
MONGO_URI  = "mongodb://172.28.228.83:27017/"
DB_NAME    = "personal"
COLLECTION = "finance.outgoing"

# ---------------------------------------------------------------------------
# Non-transaction notification types — skip entirely
# Matched against the SECOND word of the notification text.
# ---------------------------------------------------------------------------
NON_TRANSACTION_SECOND_WORD = {
    "Listo,",    # settings change (comma variant)
    "Listo.",    # settings change (period variant)
    "actualizaste",
    "Genial.",   # tope/limit update
}

# ---------------------------------------------------------------------------
# MERCHANT_RULES — per-merchant enrichment overrides (case-sensitive exact match).
# Items are templates: unitPrice is filled at import time from the transaction amount.
# Add new merchants here to have them auto-classified regardless of amount.
# ---------------------------------------------------------------------------
MERCHANT_RULES = {
    "UBER RIDES": {
        "category": "transport",
        "tags":     ["ride"],
        "items":    [{"name": "ride", "quantity": 1}],
    },
    "NETFLIX.COM": {
        "category": "entertainment",
        "tags":     ["subscription"],
        "items":    [{"name": "netflix subscription", "quantity": 1}],
    },
    "Audible": {
        "category": "entertainment",
        "tags":     ["subscription"],
        "items":    [{"name": "audible subscription", "quantity": 1}],
    },
    "GOOGLE PLAY": {
        "category": "entertainment",
        "tags":     ["subscription"],
        "items":    [{"name": "google play", "quantity": 1}],
    },
    "DL GOOGLE PLAY": {
        "category": "entertainment",
        "tags":     ["subscription"],
        "items":    [{"name": "google play", "quantity": 1}],
    },
}

# ---------------------------------------------------------------------------
# Amount parsing
# Bancolombia uses two formats:
#   European  $28.800,00  → dots=thousands, comma=decimal  (Compraste, Retiraste)
#   US        $120,000.00 → commas=thousands, dot=decimal  (transfers, income)
#   Integer   $297        → no separator                   (Recibiras)
# Heuristic: if string ends with ,\d\d it's European; otherwise US/integer.
# ---------------------------------------------------------------------------
def parse_amount(raw: str) -> int:
    """Parse a dollar-sign-prefixed amount string to integer COP value."""
    s = raw.lstrip("$").strip()
    if re.search(r",\d{2}$", s):          # European: e.g. 28.800,00
        s = s.replace(".", "").replace(",", ".")
    else:                                  # US / integer: e.g. 120,000.00 or 297
        s = s.replace(",", "")
    return int(float(s))


# ---------------------------------------------------------------------------
# Date / time parsing  →  occurredAt ISO string in Bogotá time (-05:00)
# ---------------------------------------------------------------------------
def _make_occurred_at(date_str: str, time_str: str) -> str:
    """
    Build an occurredAt string given separate date and time components.
    Accepted date formats: DD/MM/YYYY  |  DD/MM/YY  |  YYYY/MM/DD
    Accepted time format:  HH:MM
    Returns ISO string with fixed -05:00 offset.
    """
    # Normalise date
    parts = date_str.split("/")
    if len(parts) != 3:
        raise ValueError(f"Unrecognised date format: {date_str!r}")

    p0, p1, p2 = parts
    if len(p0) == 4:           # YYYY/MM/DD  (QR transfers)
        year, month, day = int(p0), int(p1), int(p2)
    elif len(p2) == 2:         # DD/MM/YY    (Bre-B transfers)
        day, month, year = int(p0), int(p1), 2000 + int(p2)
    else:                      # DD/MM/YYYY  (most types)
        day, month, year = int(p0), int(p1), int(p2)

    hh, mm = map(int, time_str.split(":"))
    return f"{year:04d}-{month:02d}-{day:02d}T{hh:02d}:{mm:02d}:00-05:00"


# ---------------------------------------------------------------------------
# Per-type notification parsers
# Each returns a dict with parsed fields, or raises ValueError with a message.
# ---------------------------------------------------------------------------

def _parse_compraste(text: str) -> dict:
    """
    Bancolombia: Compraste $AMT en MERCHANT con tu T.Deb *LAST4, el DD/MM/YYYY a las HH:MM
    """
    m = re.search(
        r"Compraste (\$[\d.,]+) en (.+?) con tu T\.Deb \*(\d+),\s*el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if not m:
        raise ValueError("Compraste: pattern did not match")
    return {
        "transactionType": "purchase",
        "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
        "merchant":        m.group(2).strip(),
        "ref":             {"value": f"*{m.group(3)}", "type": "card"},
        "recipient":       None,
        "sender":          None,
        "occurredAt":      _make_occurred_at(m.group(4), m.group(5)),
    }


def _parse_retiraste(text: str) -> dict:
    """
    Bancolombia: Retiraste $AMT en LOCATION de tu T.Deb **LAST4 el DD/MM/YYYY a las HH:MM
    Note: double-star (**) before card digits.
    """
    m = re.search(
        r"Retiraste (\$[\d.,]+) en (.+?) de tu T\.Deb \*+(\d+)\s+el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if not m:
        raise ValueError("Retiraste: pattern did not match")
    return {
        "transactionType": "withdrawal",
        "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
        "merchant":        m.group(2).strip(),
        "ref":             {"value": f"*{m.group(3)}", "type": "card"},
        "recipient":       None,
        "sender":          None,
        "occurredAt":      _make_occurred_at(m.group(4), m.group(5)),
    }


def _parse_breb_transfer(text: str) -> dict:
    """
    Bancolombia: DANIEL, transferiste $AMT a la llave LLAVE desde tu cuenta *ACCT a NAME el DD/MM/YY a las HH:MM.
    """
    m = re.search(
        r"transferiste (\$[\d.,]+) a la llave (\S+) desde tu cuenta \*?(\S+) a (.+?) el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if not m:
        raise ValueError("DANIEL,transferiste: pattern did not match")
    # Recipient name may be followed by extra text ("Con Bre-b…"); strip at period
    name = m.group(4).strip()
    name = re.split(r"\.", name)[0].strip()
    return {
        "transactionType": "transfer",
        "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
        "merchant":        None,
        "ref":             {"value": f"*{m.group(3)}", "type": "account"},
        "recipient": {
            "name":  name,
            "llave": m.group(2),
            "type":  "llave",
        },
        "sender":     None,
        "occurredAt": _make_occurred_at(m.group(5), m.group(6)),
    }


def _parse_transferiste(text: str) -> dict:
    """
    Regular transfer (two sub-patterns):
      Standard: Transferiste $AMT desde tu cuenta *?ACCT a la cuenta *?ACCT2 el DD/MM/YYYY a las HH:MM.
      QR:       Transferiste $AMT por QR desde tu cuenta ACCT a la cuenta ACCT2, el YYYY/MM/DD HH:MM.
    """
    # QR pattern (different date format, no "a las")
    qr = re.search(
        r"Transferiste (\$[\d.,]+) por QR desde tu cuenta \*?(\S+?) a la cuenta \*?(\S+?)[,\s]+"
        r"el (\d{4}/\d{2}/\d{2}) (\d{2}:\d{2})",
        text,
    )
    if qr:
        return {
            "transactionType": "transfer",
            "amount":          {"value": parse_amount(qr.group(1)), "currency": "COP"},
            "merchant":        None,
            "ref":             {"value": qr.group(2).rstrip("."), "type": "account"},
            "recipient": {
                "name":    None,
                "account": "*" + qr.group(3).lstrip("*").rstrip("."),
                "type":    "account",
            },
            "sender":     None,
            "occurredAt": _make_occurred_at(qr.group(4), qr.group(5)),
        }

    # Standard pattern
    m = re.search(
        r"Transferiste (\$[\d.,]+) desde tu cuenta \*?(\S+?) a la cuenta \*?(\S+?)\s+el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if not m:
        raise ValueError("Transferiste: pattern did not match")
    return {
        "transactionType": "transfer",
        "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
        "merchant":        None,
        "ref":             {"value": m.group(2).rstrip("."), "type": "account"},
        "recipient": {
            "name":    None,
            "account": "*" + m.group(3).lstrip("*").rstrip("."),
            "type":    "account",
        },
        "sender":     None,
        "occurredAt": _make_occurred_at(m.group(4), m.group(5)),
    }


def _parse_recibiste(text: str) -> dict:
    """
    Two observed formats:
      A) Recibiste un pago por $AMT de SENDER a tu cuenta ACCT, el HH:MM a las DD/MM/YYYY
         (time and date are SWAPPED)
      B) Recibiste una transferencia por $AMT de SENDER en tu cuenta **ACCT, el DD/MM/YYYY a las HH:MM
         (normal order)
    """
    # Format A: "un pago … a tu cuenta … el HH:MM a las DD/MM/YYYY"  (swapped)
    m = re.search(
        r"Recibiste un pago por (\$[\d.,]+) de (.+?) a tu cuenta \S+,\s*el (\d{2}:\d{2}) a las (\d{1,2}/\d{1,2}/\d{2,4})",
        text,
    )
    if m:
        return {
            "transactionType": "income",
            "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
            "merchant":        None,
            "ref":             None,
            "recipient":       None,
            "sender":          {"name": m.group(2).strip()},
            "occurredAt":      _make_occurred_at(m.group(4), m.group(3)),  # date/time swapped
        }

    # Format B: "una transferencia … en tu cuenta … el DD/MM/YYYY a las HH:MM"  (normal order)
    m = re.search(
        r"Recibiste una transferencia por (\$[\d.,]+) de (.+?) en tu cuenta \S+,\s*el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if m:
        return {
            "transactionType": "income",
            "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
            "merchant":        None,
            "ref":             None,
            "recipient":       None,
            "sender":          {"name": m.group(2).strip()},
            "occurredAt":      _make_occurred_at(m.group(3), m.group(4)),
        }

    raise ValueError("Recibiste: no pattern matched")


def _parse_recibiras(text: str) -> dict:
    """
    Bancolombia: Recibiras $AMT en N dias habiles en tu tarjeta debito *LAST4 por parte de SENDER. HH:MM DD/MM/YYYY
    """
    m = re.search(
        r"Recibiras (\$[\d.,]+) en .+? por parte de (.+?)[.\s]+(\d{2}:\d{2})\s+(\d{1,2}/\d{1,2}/\d{4})",
        text,
    )
    if not m:
        raise ValueError("Recibiras: pattern did not match")
    return {
        "transactionType": "income",
        "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
        "merchant":        None,
        "ref":             None,
        "recipient":       None,
        "sender":          {"name": m.group(2).strip()},
        "occurredAt":      _make_occurred_at(m.group(4), m.group(3)),
    }


def _parse_breb_received(text: str) -> dict:
    """
    Bre-B incoming transfer:
    Bancolombia: DANIEL, recibiste una transferencia de SENDER por $AMT
                 en tu cuenta *ACCT conectada a la llave LLAVE el DD/MM/YY a las HH:MM.
    """
    m = re.search(
        r"recibiste una transferencia de (.+?) por (\$[\d.,]+)"
        r" en tu cuenta \*?(\S+?) conectada a la llave (\S+?)\s+el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if not m:
        raise ValueError("DANIEL,recibiste: pattern did not match")
    return {
        "transactionType": "income",
        "amount":          {"value": parse_amount(m.group(2)), "currency": "COP"},
        "merchant":        None,
        "ref":             {"value": f"*{m.group(3)}", "type": "account"},
        "recipient":       None,
        "sender":          {"name": m.group(1).strip()},
        "occurredAt":      _make_occurred_at(m.group(5), m.group(6)),
    }


def _parse_qr_pagaste(text: str) -> dict:
    """
    Bre-B QR outgoing payment (full account-holder name, no comma):
    Bancolombia: DANIEL AUGUSTO... pagaste $AMT por codigo QR
                 desde tu cuenta *ACCT a la llave LLAVE el DD/MM/YYYY a las HH:MM.
    """
    m = re.search(
        r"pagaste (\$[\d.,]+) por codigo QR desde tu cuenta \*?(\S+?)"
        r" a la llave (\S+?)\s+el (\d{1,2}/\d{1,2}/\d{2,4}) a las (\d{2}:\d{2})",
        text,
    )
    if not m:
        raise ValueError("pagaste QR: pattern did not match")
    return {
        "transactionType": "transfer",
        "amount":          {"value": parse_amount(m.group(1)), "currency": "COP"},
        "merchant":        None,
        "ref":             {"value": f"*{m.group(2)}", "type": "account"},
        "recipient": {
            "name":  None,
            "llave": m.group(3),
            "type":  "llave",
        },
        "sender":     None,
        "occurredAt": _make_occurred_at(m.group(4), m.group(5)),
    }


def parse_notification(text: str) -> dict:
    """
    Dispatch to the right parser based on the second word of the notification.
    Returns a parsed-fields dict or raises ValueError with a descriptive message.
    """
    words = text.split()
    if len(words) < 2:
        raise ValueError("Notification too short to identify type")

    second = words[1]
    third  = words[2] if len(words) > 2 else ""

    if second == "Compraste":
        return _parse_compraste(text)
    if second == "Retiraste":
        return _parse_retiraste(text)
    if second == "DANIEL,":
        if third == "transferiste":
            return _parse_breb_transfer(text)
        if third == "recibiste":
            return _parse_breb_received(text)
        raise ValueError(f"DANIEL, followed by unknown keyword: {third!r}")
    if second == "Transferiste":
        return _parse_transferiste(text)
    if second == "Recibiste":
        return _parse_recibiste(text)
    if second == "Recibiras":
        return _parse_recibiras(text)
    # Bre-B QR payment: full account-holder name before "pagaste"
    if "pagaste" in text and "por codigo QR" in text:
        return _parse_qr_pagaste(text)

    raise ValueError(f"Unknown notification type (second word: {second!r})")


# ---------------------------------------------------------------------------
# Item integrity check
# ---------------------------------------------------------------------------
def validate_items(items: list, amount_value: int) -> bool:
    """
    True iff sum(unitPrice * quantity for known-price items) == amount_value.
    Items where all unitPrices are None are considered valid (partial itemisation
    with no price data — skip the check rather than failing).
    """
    known = [
        item["unitPrice"] * item["quantity"]
        for item in items
        if item.get("unitPrice") is not None
    ]
    if not known:
        return True   # all-null — nothing to check
    return sum(known) == amount_value


# ---------------------------------------------------------------------------
# Enrichment pipeline
# ---------------------------------------------------------------------------
def _apply_merchant_rule(merchant: str, amount_value: int) -> dict | None:
    """Return enrichment dict if merchant is in MERCHANT_RULES, else None."""
    rule = MERCHANT_RULES.get(merchant)
    if rule is None:
        return None

    # Build items with unitPrice filled in from amount
    template_items = rule["items"]
    total_qty = sum(it["quantity"] for it in template_items)

    # Distribute amount across items (last item absorbs any rounding remainder)
    items = []
    remaining = amount_value
    for idx, it in enumerate(template_items):
        is_last = (idx == len(template_items) - 1)
        if is_last:
            price = remaining
        else:
            price = round(amount_value * it["quantity"] / total_qty)
            remaining -= price * it["quantity"]
        items.append({
            "name":      it["name"],
            "quantity":  it["quantity"],
            "unitPrice": price,
        })

    return {
        "category": rule["category"],
        "tags":     list(rule["tags"]),
        "items":    items,
        "classificationSource": "merchant-rule",
    }


def _auto_match(col, merchant: str | None, amount_value: int) -> dict | None:
    """
    Query DB for a prior record with the same merchant and amount.
    Returns enrichment dict if found, else None.
    Auto-match is only attempted for purchases (merchant is not None).
    """
    if merchant is None:
        return None

    existing = col.find_one(
        {
            "merchant":    merchant,
            "amount.value": amount_value,
            "classificationSource": {"$ne": "unclassified"},
        },
        {"category": 1, "tags": 1, "items": 1},
        sort=[("occurredAt", -1)],  # most recent match
    )
    if existing is None:
        return None

    # Copy item names and quantities but drop unit prices — the same items
    # (e.g. coke + smokes) can have different price splits on each visit,
    # so inheriting exact prices would be false precision and breaks integrity
    # checks when amounts drift. Names are enough for reporting.
    items = [
        {"name": it["name"], "quantity": it.get("quantity", 1), "unitPrice": None}
        for it in existing["items"]
    ]
    return {
        "category": existing["category"],
        "tags":     list(existing.get("tags", [])),
        "items":    items,
        "classificationSource": "auto-matched",
    }


def _unclassified_enrichment(amount_value: int) -> dict:
    """Fallback: unclassified category, single unclassified item for full amount."""
    return {
        "category": "unclassified",
        "tags":     [],
        "items":    [{"name": "unclassified", "quantity": 1, "unitPrice": amount_value}],
        "classificationSource": "unclassified",
    }


def enrich(col, parsed: dict) -> dict:
    """
    Apply enrichment in priority order:
      1. MERCHANT_RULES  (exact merchant name match, any amount)
      2. Auto-match      (same merchant + same amount already in DB)
      3. Unclassified    (fallback)
    Returns the enrichment dict {category, tags, items, classificationSource}.
    """
    merchant = parsed.get("merchant")
    amount   = parsed["amount"]["value"]

    # 1. Merchant rule
    if merchant:
        rule_enrich = _apply_merchant_rule(merchant, amount)
        if rule_enrich:
            return rule_enrich

    # 2. Auto-match from DB — only use if items are self-consistent
    matched = _auto_match(col, merchant, amount)
    if matched and validate_items(matched["items"], amount):
        return matched

    # 3. Unclassified fallback (also covers bad auto-match items)
    return _unclassified_enrichment(amount)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Import Bancolombia notifications into MongoDB finance.outgoing."
    )
    parser.add_argument(
        "--input",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples-raw.json"),
        help="Path to raw JSON file (default: samples-raw.json next to this script)",
    )
    parser.add_argument("--since", help="Only import records with email date >= YYYY-MM-DD (UTC)")
    parser.add_argument("--until", help="Only import records with email date <= YYYY-MM-DD (UTC)")
    parser.add_argument("--dry-run",  action="store_true", help="Print plan without writing to DB")
    parser.add_argument("--debug",    action="store_true", help="Print detailed parse info per record")
    args = parser.parse_args()

    # ── Load input file ──────────────────────────────────────────────────────
    if not os.path.exists(args.input):
        print(f"FATAL: Input file not found: {args.input}")
        sys.exit(2)

    try:
        with open(args.input) as f:
            raw_records = json.load(f)
    except Exception as exc:
        print(f"FATAL: Could not read {args.input}: {exc}")
        sys.exit(2)

    # ── Connect to MongoDB ───────────────────────────────────────────────────
    try:
        import pymongo
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        col = client[DB_NAME][COLLECTION]
    except Exception as exc:
        print(f"FATAL: Cannot connect to MongoDB at {MONGO_URI}: {exc}")
        sys.exit(2)

    # ── Date filter helpers ──────────────────────────────────────────────────
    since_prefix = (args.since + " ") if args.since else None
    until_prefix = (args.until + " ") if args.until else None  # date is "YYYY-MM-DD HH:MM UTC"

    def in_date_range(date_str: str) -> bool:
        # date_str is like "2026-05-13 23:17 UTC"
        if since_prefix and date_str < since_prefix:
            return False
        if until_prefix:
            # Compare up to the date part only (first 10 chars)
            if date_str[:10] > args.until:
                return False
        return True

    # ── Sort records oldest-first so intra-batch auto-matches work ───────────
    sorted_records = sorted(raw_records, key=lambda r: r["date"])

    # ── Process ──────────────────────────────────────────────────────────────
    now_utc = datetime.now(timezone.utc).isoformat()

    counts = {"inserted": 0, "skipped_dedup": 0, "skipped_non_tx": 0,
              "skipped_date": 0, "errors": 0}

    for raw in sorted_records:
        mid          = raw["messageId"]
        thread_id    = raw["threadId"]
        email_date   = raw["date"]
        notification = raw["notification"]

        # ── Date filter ──────────────────────────────────────────────────────
        if not in_date_range(email_date):
            counts["skipped_date"] += 1
            if args.debug:
                print(f"[DATE-SKIP] {mid}  {email_date}")
            continue

        # ── Non-transaction filter ───────────────────────────────────────────
        words = notification.split()
        second_word = words[1] if len(words) > 1 else ""
        if second_word in NON_TRANSACTION_SECOND_WORD:
            counts["skipped_non_tx"] += 1
            if args.debug:
                print(f"[NON-TX]   {mid}  {email_date}  ({second_word})")
            continue

        # ── Deduplication ────────────────────────────────────────────────────
        if col.find_one({"emailMessageId": mid}, {"_id": 1}):
            counts["skipped_dedup"] += 1
            if args.debug:
                print(f"[DEDUP]    {mid}  already in DB")
            continue

        # ── Parse ────────────────────────────────────────────────────────────
        try:
            parsed = parse_notification(notification)
        except ValueError as exc:
            print(f"[ERROR]    {mid}  {email_date}  PARSE FAILED: {exc}")
            print(f"           notification: {notification[:120]}")
            counts["errors"] += 1
            continue

        if args.debug:
            print(f"[PARSED]   {mid}  type={parsed['transactionType']}  "
                  f"amount={parsed['amount']['value']}  merchant={parsed.get('merchant')!r}  "
                  f"occurredAt={parsed['occurredAt']}")

        # ── Exact duplicate detection ────────────────────────────────────────
        # Same rawNotification text already in DB = Bancolombia resent the same
        # email (different messageId, identical content). Mark but still insert
        # so the record exists for audit; balance calculations exclude these.
        existing_notif = col.find_one(
            {"rawNotification": notification, "isTemplate": {"$exists": False}},
            {"emailMessageId": 1, "_id": 0},
        )
        is_exact_dup = existing_notif is not None

        # ── Enrich ───────────────────────────────────────────────────────────
        enrichment = enrich(col, parsed)

        # ── Build document ───────────────────────────────────────────────────
        tx_type   = parsed["transactionType"]
        direction = "in" if tx_type == "income" else "out"

        doc = {
            "emailMessageId":  mid,
            "threadId":        thread_id,
            "occurredAt":      parsed["occurredAt"],
            "rawNotification": notification,
            "transactionType": tx_type,
            "direction":       direction,
            "amount":          parsed["amount"],
            "merchant":        parsed.get("merchant"),
            "ref":             parsed.get("ref"),
            "recipient":       parsed.get("recipient"),
            "sender":          parsed.get("sender"),
            "category":        enrichment["category"],
            "tags":            enrichment["tags"],
            "items":           enrichment["items"],
            "classificationSource": enrichment["classificationSource"],
            "importedAt":      now_utc,
            # Duplicate fields — set only when relevant
            **({"duplicateStatus": "exact",
                "duplicateOf": existing_notif["emailMessageId"]}
               if is_exact_dup else {}),
        }

        merchant_label = (
            parsed.get("merchant")
            or (parsed.get("recipient") or {}).get("name")
            or (parsed.get("sender") or {}).get("name")
            or "?"
        )

        # ── Insert or dry-run ────────────────────────────────────────────────
        if args.dry_run:
            print(f"[DRY-RUN]  {mid}  {parsed['occurredAt']}  "
                  f"{merchant_label}  {parsed['amount']['value']} COP  "
                  f"src={enrichment['classificationSource']}  cat={enrichment['category']}")
        else:
            try:
                col.insert_one(doc)
                print(f"[INSERT]   {mid}  {parsed['occurredAt']}  "
                      f"{merchant_label}  {parsed['amount']['value']} COP  "
                      f"src={enrichment['classificationSource']}  cat={enrichment['category']}")
            except Exception as exc:
                print(f"[ERROR]    {mid}  DB INSERT FAILED: {exc}")
                counts["errors"] += 1
                continue

        counts["inserted"] += 1

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"{'DRY-RUN ' if args.dry_run else ''}Import complete")
    print(f"  {'Would insert' if args.dry_run else 'Inserted'} : {counts['inserted']}")
    print(f"  Skipped (dedup)   : {counts['skipped_dedup']}")
    print(f"  Skipped (non-tx)  : {counts['skipped_non_tx']}")
    print(f"  Skipped (date)    : {counts['skipped_date']}")
    print(f"  Errors (skipped)  : {counts['errors']}")
    print("=" * 60)

    sys.exit(1 if counts["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
