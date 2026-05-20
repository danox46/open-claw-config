#!/usr/bin/env python3
"""
finance-sync.py — Agent entry point. Run every 30 minutes.

No arguments needed. Does three things:
  1. Fetches new Bancolombia email threads (last 8 days, thread-growth aware)
  2. Imports any new transactions (auto-enriches via merchant rules + history)
  3. Updates pending-review.json with unclassified transactions that need
     the agent to ask the user about

Output file: pending-review.json
  Array of unclassified transactions. Empty array means nothing to review.
  Items are removed from the file once script 2 (finance-enrich.py) saves
  their enrichment to the DB. Items persist across runs until enriched.

Exit codes:
  0  Completed — pending-review.json is up to date
  1  Non-fatal issues (some fetch/import errors) — output still written
  2  Fatal — could not connect to DB or write output
"""

import json, os, subprocess, sys
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONGO_URI  = 'mongodb://172.28.228.83:27017/'
DB_NAME    = 'personal'
COLLECTION = 'finance.outgoing'

FETCH_SCRIPT  = os.path.join(SCRIPT_DIR, 'fetch-year.py')
IMPORT_SCRIPT = os.path.join(SCRIPT_DIR, 'finance-import.py')
PENDING_FILE  = os.path.join(SCRIPT_DIR, 'pending-review.json')
STATE_FILE    = os.path.join(SCRIPT_DIR, 'sync-state.json')

# How far back to search on each run (overlap prevents missing emails at day
# boundaries; thread-meta dedup keeps it fast after the first run)
FETCH_WINDOW_DAYS = 8   # how far back to search Gmail (overlap prevents missing emails)
QUEUE_WINDOW_DAYS = 1   # only surface transactions from this many days ago to the agent

ENV = {
    **os.environ,
    'HOME': '/home/danox',
    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
            ':/home/danox/.local/bin:/home/danox/go/bin',
}


# ── helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    print(f'[{ts}] {msg}', file=sys.stderr)


def run_step(label: str, cmd: list[str]) -> int:
    """Run a subprocess step, stream its stderr, return exit code."""
    log(f'→ {label}')
    result = subprocess.run(cmd, env=ENV, stderr=sys.stderr)
    if result.returncode not in (0, 1):   # 0=ok, 1=partial (both acceptable)
        log(f'  {label} exited {result.returncode} — continuing anyway')
    return result.returncode


def load_json(path: str, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path: str, data) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    now_utc    = datetime.now(timezone.utc)
    since_dt   = now_utc - timedelta(days=FETCH_WINDOW_DAYS)
    since_gog  = since_dt.strftime('%Y/%m/%d')   # fetch-year format
    since_imp  = since_dt.strftime('%Y-%m-%d')   # finance-import format
    since_queue = (now_utc - timedelta(days=QUEUE_WINDOW_DAYS)).strftime('%Y-%m-%d')

    # ── 1. Fetch ─────────────────────────────────────────────────────────────
    fetch_rc = run_step(
        f'Fetch (since {since_gog})',
        ['python3', FETCH_SCRIPT, '--since', since_gog],
    )

    # ── 2. Import ─────────────────────────────────────────────────────────────
    import_rc = run_step(
        f'Import (since {since_imp})',
        ['python3', IMPORT_SCRIPT, '--since', since_imp],
    )

    # ── 3. Connect to DB ──────────────────────────────────────────────────────
    try:
        import pymongo
        col = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)[DB_NAME][COLLECTION]
        col.find_one({}, {'_id': 1})   # smoke-test connection
    except Exception as exc:
        log(f'FATAL: cannot connect to MongoDB: {exc}')
        sys.exit(2)

    # ── 4. Load existing pending queue ────────────────────────────────────────
    existing_pending: list[dict] = load_json(PENDING_FILE, [])
    existing_ids = {item['emailMessageId'] for item in existing_pending}

    # Drop items that have since been enriched (classificationSource changed)
    still_unclassified_ids = {
        doc['emailMessageId']
        for doc in col.find(
            {'emailMessageId': {'$in': list(existing_ids)},
             'classificationSource': 'unclassified'},
            {'emailMessageId': 1}
        )
    }
    carried_over = [
        item for item in existing_pending
        if item['emailMessageId'] in still_unclassified_ids
        and item['occurredAt'] >= since_queue   # respect the queue window
    ]
    dropped = len(existing_pending) - len(carried_over)
    if dropped:
        log(f'  Removed {dropped} item(s) from queue (enriched or outside window)')

    # ── 5. Find recent unclassified transactions not already in the queue ────────
    # Only queue transactions within the fetch window — historical unclassified
    # records are handled automatically by backward matching in finance-enrich.py
    # when a similar new transaction is manually classified. No need to surface
    # months of history to the agent.
    state = load_json(STATE_FILE, {})

    new_docs = list(col.find(
        {
            'classificationSource': 'unclassified',
            'transactionType':      {'$ne': 'opening-balance'},
            'occurredAt':           {'$gte': since_queue},
            'emailMessageId':       {'$nin': list(existing_ids)},
        },
        {'_id': 0,
         'emailMessageId': 1, 'occurredAt': 1, 'transactionType': 1,
         'direction': 1, 'amount': 1, 'merchant': 1,
         'recipient': 1, 'sender': 1, 'rawNotification': 1}
    ).sort('occurredAt', 1))

    # Build slim review items — just what the agent needs to ask a good question
    new_items = []
    for doc in new_docs:
        mid = doc['emailMessageId']
        if mid in existing_ids:
            continue   # already in queue (carried over above)

        # Human-readable counterparty label
        label = (
            doc.get('merchant')
            or (doc.get('recipient') or {}).get('name')
            or (doc.get('sender') or {}).get('name')
            or '?'
        )

        new_items.append({
            'emailMessageId':  mid,
            'occurredAt':      doc['occurredAt'],
            'transactionType': doc['transactionType'],
            'direction':       doc['direction'],
            'amount':          doc['amount'],
            'counterparty':    label,
            'rawNotification': doc.get('rawNotification', ''),
        })

    # ── 6. Write pending-review.json ──────────────────────────────────────────
    pending = sorted(
        carried_over + new_items,
        key=lambda x: x['occurredAt']
    )

    try:
        save_json(PENDING_FILE, pending)
    except Exception as exc:
        log(f'FATAL: cannot write {PENDING_FILE}: {exc}')
        sys.exit(2)

    # ── 7. Save state ─────────────────────────────────────────────────────────
    state['lastSyncUtc'] = now_utc.isoformat()   # informational only
    save_json(STATE_FILE, state)

    # ── 8. Summary ────────────────────────────────────────────────────────────
    log(f'Done. New items: {len(new_items)}  '
        f'Carried over: {len(carried_over)}  '
        f'Total pending: {len(pending)}  '
        f'→ {PENDING_FILE}')

    worst_rc = max(fetch_rc, import_rc)
    sys.exit(1 if worst_rc > 0 else 0)


if __name__ == '__main__':
    main()
