#!/usr/bin/env python3
"""
finance-enrich.py — Saves agent-enriched transactions to MongoDB.

The agent reads pending-review.json, classifies each transaction by adding a
"category" field (plus optional "tags", "items", "classificationSource"), then
runs this script to persist everything.

Usage:
  python3 finance-enrich.py [--dry-run]

Output (stdout — always valid JSON, parse this):
  {
    "status":          "ok" | "partial" | "error",
    "saved":           N,          -- new transactions written to DB
    "backwardUpdates": N,          -- old unclassified records auto-inherited
    "skipped":         N,          -- items that failed validation (kept in queue)
    "queueCleared":    true|false,  -- false means conflicted items were written back to queue
    "conflicts": [                 -- category mismatches (item NOT saved, returned to queue)
      {
        "type":            "merchant_history" | "backward_match",
        "emailMessageId":  "...",
        "occurredAt":      "...",
        "counterparty":    "...",
        "amount":          {"value": N, "currency": "COP"},
        "existingCategory":"...",
        "proposedCategory":"...",
        "instruction":     "..."   -- tell the agent exactly what to ask the user
      }
    ],
    "errors": [                    -- validation failures the agent can fix
      {
        "emailMessageId": "...",
        "field":          "...",
        "message":        "..."
      }
    ]
  }

Exit codes:
  0  All enriched items saved, no conflicts, no errors
  1  Partial — conflicts or validation errors present (check output)
  2  Fatal — DB unreachable or file unreadable/unwritable (check output.error)

Enrichment fields the agent adds to each item in pending-review.json:

  category   (required) — must be a valid id from categories.json.
                          e.g. "groceries", "dining", "transport", "health",
                          "utilities", "subscriptions", "clothing", "grooming",
                          "electronics", "entertainment", "car", "rent", "home",
                          "cleaning", "education", "travel", "savings", "income",
                          "other"

  tags       (optional) — array of strings, e.g. ["social", "treat", "smokes"]

  items      (optional) — line-item breakdown:
               [{"name": "...", "quantity": N, "unitPrice": N_or_null}]
               unitPrice is optional — use null when the per-item price is
               unknown or irrelevant. No integrity check is performed against
               amount.value; items are for reporting and search only.

  classificationSource  (optional) — defaults to "manual":
               "auto-matched"  — agent inferred from a prior identical tx
               "merchant-rule" — a merchant rule was applied
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

MONGO_URI       = 'mongodb://172.28.228.83:27017/'
DB_NAME         = 'personal'
COLLECTION      = 'finance.outgoing'
FINANCE_DIR     = '/home/danox/.openclaw/workspace/finance'
PENDING_FILE    = os.path.join(FINANCE_DIR, 'pending-review.json')
CATEGORIES_FILE = os.path.join(FINANCE_DIR, 'categories.json')

VALID_SOURCES = {'manual', 'auto-matched', 'merchant-rule'}


def load_valid_categories() -> set[str]:
    """Load category ids from categories.json. Falls back to empty set (no restriction)."""
    try:
        with open(CATEGORIES_FILE, encoding='utf-8') as f:
            data = json.load(f)
        return {c['id'] for c in data.get('categories', [])}
    except Exception as exc:
        print(f'[WARN] Could not load {CATEGORIES_FILE}: {exc} — skipping category validation',
              file=sys.stderr)
        return set()


VALID_CATEGORIES = load_valid_categories()


# ── helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    print(f'[{ts}] {msg}', file=sys.stderr)


def fatal(message: str) -> None:
    """Print a fatal JSON error to stdout and exit 2."""
    print(json.dumps({'status': 'error', 'error': message}, indent=2))
    sys.exit(2)


def load_json(path: str, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default


def save_json(path: str, data) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def validate_items(items: list, amount_value: int) -> tuple[bool, str]:
    known = [item['unitPrice'] * item['quantity']
             for item in items if item.get('unitPrice') is not None]
    if not known:
        return True, ''   # all prices unknown — nothing to validate
    total = sum(known)
    if total != amount_value:
        return False, f'items sum {total:,} != amount {amount_value:,}'
    return True, ''


def match_key(doc: dict) -> tuple | None:
    """
    Returns a hashable signature used to find related transactions.
    Returns None for types where backward matching doesn't apply.
    """
    tx   = doc.get('transactionType')
    amt  = doc.get('amount', {}).get('value')

    if tx == 'purchase':
        merchant = doc.get('merchant')
        if merchant:
            return ('purchase', merchant, amt)

    elif tx == 'transfer':
        recp = doc.get('recipient') or {}
        name = recp.get('name') or recp.get('llave')
        if name:
            return ('transfer', name, amt)

    elif tx == 'income':
        sndr = doc.get('sender') or {}
        name = sndr.get('name')
        if name:
            return ('income', name, amt)

    return None  # withdrawals and unknown types — skip backward matching


# ── merchant history check ───────────────────────────────────────────────────

def check_merchant_history(col, merchant: str, proposed_category: str, exclude_mid: str) -> dict | None:
    """
    Returns a conflict dict if the merchant has an established category that
    differs from the proposed one, or None if everything looks consistent.

    Rule: if ≥3 existing classified records exist for this merchant and the
    proposed category accounts for fewer than 20% of them, flag it.
    The agent must ask the user before the item is saved.
    """
    if not merchant:
        return None

    docs = list(col.find(
        {'merchant': merchant,
         'classificationSource': {'$nin': ['unclassified', 'merchant-rule']},
         'emailMessageId': {'$ne': exclude_mid}},
        {'category': 1, 'occurredAt': 1, 'amount': 1, '_id': 0}
    ))

    if len(docs) < 3:
        return None   # not enough history to flag

    from collections import Counter
    counts = Counter(d['category'] for d in docs if d.get('category'))
    total  = sum(counts.values())
    top_category, top_count = counts.most_common(1)[0]

    if top_category == proposed_category:
        return None   # matches dominant category — fine

    proposed_count = counts.get(proposed_category, 0)
    if proposed_count / total >= 0.20:
        return None   # proposed category already accounts for ≥20% — plausible

    sample = docs[-1]   # most recently classified record for context
    return {
        'type':             'merchant_history',
        'existingCategory': top_category,
        'proposedCategory': proposed_category,
        'existingCount':    top_count,
        'totalRecords':     total,
        'instruction': (
            f'Merchant history conflict. Ask the user: '
            f'{merchant} has {top_count}/{total} existing records classified as '
            f'"{top_category}", but this transaction was given "{proposed_category}". '
            f'Is "{proposed_category}" correct for {merchant} on '
            f'{sample["occurredAt"][:10]}? Or should it be "{top_category}"?'
        ),
    }


# ── backward matching ─────────────────────────────────────────────────────────

def find_backward_candidates(col, key: tuple, exclude_mid: str) -> list[dict]:
    """
    Find all DB documents sharing the same match_key, excluding the just-saved one.
    Returns only fields needed for conflict detection and inheritance.
    """
    tx_type, counterparty, amount_value = key

    if tx_type == 'purchase':
        query = {'transactionType': 'purchase',
                 'merchant': counterparty,
                 'amount.value': amount_value,
                 'emailMessageId': {'$ne': exclude_mid}}

    elif tx_type == 'transfer':
        query = {'transactionType': 'transfer',
                 'amount.value': amount_value,
                 'emailMessageId': {'$ne': exclude_mid},
                 '$or': [{'recipient.name': counterparty},
                         {'recipient.llave': counterparty}]}

    elif tx_type == 'income':
        query = {'transactionType': 'income',
                 'sender.name': counterparty,
                 'amount.value': amount_value,
                 'emailMessageId': {'$ne': exclude_mid}}
    else:
        return []

    return list(col.find(
        query,
        {'emailMessageId': 1, 'occurredAt': 1, 'classificationSource': 1,
         'category': 1, 'merchant': 1, 'recipient': 1, 'sender': 1,
         'amount': 1, '_id': 0}
    ))


def counterparty_label(doc: dict) -> str:
    return (
        doc.get('merchant')
        or (doc.get('recipient') or {}).get('name')
        or (doc.get('sender') or {}).get('name')
        or '?'
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Save agent-enriched transactions from pending-review.json to MongoDB.'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate without writing to DB or file')
    args = parser.parse_args()

    # ── 1. Load pending queue ─────────────────────────────────────────────────
    try:
        pending: list[dict] = load_json(PENDING_FILE, [])
    except Exception as exc:
        fatal(f'Cannot read {PENDING_FILE}: {exc}')

    enriched  = [item for item in pending if item.get('category')]
    remaining = [item for item in pending if not item.get('category')]

    if not enriched:
        result = {
            'status': 'ok',
            'saved': 0, 'backwardUpdates': 0, 'skipped': 0,
            'queueCleared': False,
            'conflicts': [], 'errors': [],
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)

    # ── 2. Connect to DB ──────────────────────────────────────────────────────
    col = None
    if not args.dry_run:
        try:
            import pymongo
            col = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)[DB_NAME][COLLECTION]
            col.find_one({}, {'_id': 1})
        except Exception as exc:
            fatal(f'Cannot connect to MongoDB at {MONGO_URI}: {exc}')

    # ── 3. Validate + save each enriched item ─────────────────────────────────
    now_utc         = datetime.now(timezone.utc).isoformat()
    saved           = 0
    backward_total  = 0
    errors          = []
    conflicts       = []

    for item in enriched:
        mid      = item['emailMessageId']
        category = item.get('category', '').strip()
        tags     = item.get('tags') or []
        items    = item.get('items') or []
        src      = item.get('classificationSource', 'manual')

        # ── validation ────────────────────────────────────────────────────────
        if not category:
            errors.append({'emailMessageId': mid, 'field': 'category',
                           'message': 'category is required and cannot be empty'})
            remaining.append(item)
            continue

        if VALID_CATEGORIES and category not in VALID_CATEGORIES:
            errors.append({'emailMessageId': mid, 'field': 'category',
                           'message': (
                               f'"{category}" is not a valid category. '
                               f'Valid options: {sorted(VALID_CATEGORIES)}. '
                               f'To add a new category edit '
                               f'/home/danox/.openclaw/workspace/finance/categories.json'
                           )})
            remaining.append(item)
            continue

        if src not in VALID_SOURCES:
            errors.append({'emailMessageId': mid, 'field': 'classificationSource',
                           'message': f'"{src}" is not valid — must be one of: {sorted(VALID_SOURCES)}'})
            remaining.append(item)
            continue

        # ── merchant history check (pre-save) ────────────────────────────────
        if not args.dry_run:
            merchant = item.get('counterparty') or item.get('merchant')
            history_conflict = check_merchant_history(col, merchant, category, mid)
            if history_conflict:
                conflict_entry = {
                    **history_conflict,
                    'emailMessageId':  mid,
                    'occurredAt':      item['occurredAt'],
                    'counterparty':    item.get('counterparty', '?'),
                    'amount':          item['amount'],
                }
                conflicts.append(conflict_entry)
                # Return item to queue without its category so agent re-asks
                stripped = {k: v for k, v in item.items()
                            if k not in ('category', 'tags', 'items', 'classificationSource')}
                remaining.append(stripped)
                log(f'  CONFLICT (merchant history) {mid}  {item["occurredAt"][:10]}  '
                    f'{merchant}  proposed={category}  dominant={history_conflict["existingCategory"]}')
                continue

        # ── save to DB ────────────────────────────────────────────────────────
        set_payload = {
            'category':             category,
            'tags':                 tags,
            'classificationSource': src,
            'enrichedAt':           now_utc,
        }
        if items:
            set_payload['items'] = items

        if args.dry_run:
            log(f'[DRY-RUN] save {mid}  {item["occurredAt"][:10]}  '
                f'{item.get("counterparty","?"):<30}  cat={category}  src={src}')
        else:
            result = col.update_one({'emailMessageId': mid}, {'$set': set_payload})
            if result.matched_count == 0:
                errors.append({'emailMessageId': mid, 'field': 'emailMessageId',
                               'message': 'not found in DB — may not be imported yet; keep in queue'})
                remaining.append(item)
                continue

        saved += 1

        # ── backward inheritance ───────────────────────────────────────────────
        key = match_key({**item,
                         'transactionType': item.get('transactionType'),
                         'merchant':        item.get('counterparty'),   # pending items use counterparty
                         'amount':          item.get('amount')})

        if key and not args.dry_run:
            candidates = find_backward_candidates(col, key, mid)

            for cand in candidates:
                cand_src  = cand.get('classificationSource', 'unclassified')
                cand_cat  = cand.get('category', 'unclassified')
                cand_mid  = cand['emailMessageId']
                cand_date = cand['occurredAt'][:10]
                cand_cp   = counterparty_label(cand)

                if cand_src == 'unclassified':
                    # Safe to inherit
                    inherit_payload = {
                        'category':             category,
                        'tags':                 tags,
                        'classificationSource': 'auto-matched',
                        'enrichedAt':           now_utc,
                    }
                    if items:
                        inherit_payload['items'] = items
                    col.update_one({'emailMessageId': cand_mid}, {'$set': inherit_payload})
                    backward_total += 1
                    log(f'  ↳ inherited → {cand_mid}  {cand_date}  {cand_cp}  cat={category}')

                elif cand_cat != category:
                    # Already classified but different category — conflict
                    conflicts.append({
                        'emailMessageId':   cand_mid,
                        'occurredAt':       cand['occurredAt'],
                        'counterparty':     cand_cp,
                        'amount':           cand['amount'],
                        'existingCategory': cand_cat,
                        'proposedCategory': category,
                        'instruction': (
                            f'Backward match found a conflict. '
                            f'Ask the user: the existing record ({cand_date} · {cand_cp} · '
                            f'{cand["amount"]["value"]:,} COP) is already classified as '
                            f'"{cand_cat}", but the new enrichment suggests "{category}". '
                            f'Which category is correct for this transaction?'
                        ),
                    })
                # else: already classified with the same category — nothing to do

        elif key and args.dry_run:
            log(f'  ↳ [DRY-RUN] would search backward matches for key={key}')

    # ── 4. Write back conflicted/errored items, clear everything else ────────
    # Items that hit a merchant-history conflict are returned to the file
    # (category stripped) so the agent can re-ask the user immediately without
    # waiting for the next sync cycle. Everything else is cleared — sync
    # will repopulate from the DB on its next run.
    if not args.dry_run:
        try:
            save_json(PENDING_FILE, remaining)
        except Exception as exc:
            fatal(f'Cannot write {PENDING_FILE}: {exc}')

    # ── 5. Output result JSON ─────────────────────────────────────────────────
    has_issues = bool(errors) or bool(conflicts)
    status = 'partial' if has_issues else 'ok'

    output = {
        'status':          status,
        'saved':           saved,
        'backwardUpdates': backward_total,
        'skipped':         len(errors),
        'queueCleared':    not args.dry_run and len(remaining) == 0,
        'conflicts':       conflicts,
        'errors':          errors,
    }
    print(json.dumps(output, indent=2))
    sys.exit(1 if has_issues else 0)


if __name__ == '__main__':
    main()
