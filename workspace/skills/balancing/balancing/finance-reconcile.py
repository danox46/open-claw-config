#!/usr/bin/env python3
"""
Reconcile system balance against actual bank balance.

Usage:
  python3 finance-reconcile.py <actual_balance>

Behaviour:
  actual > system  →  system is over-counting expenses (holds/duplicates).
                       Removes exact duplicates one by one (largest first) until
                       system balance reaches actual, then reports remaining gap.
  actual < system  →  system is under-counting expenses (unrecorded transactions).
                       Inserts a balancing expense entry for the gap amount.
  actual == system →  Nothing to do.
"""

import sys
import pymongo
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

try:
    actual = int(sys.argv[1].replace(',', '').replace('.', ''))
except ValueError:
    print(f"Error: could not parse '{sys.argv[1]}' as an integer balance.")
    sys.exit(1)

client = pymongo.MongoClient('mongodb://172.28.228.83:27017/')
col    = client['personal']['finance.outgoing']

# ── Calculate current system balance (excluding known exact duplicates) ────────
def get_balance():
    docs = list(col.find({
        'isTemplate':      {'$exists': False},
        'duplicateStatus': {'$ne': 'exact'},
    }, {'transactionType': 1, 'amount': 1, '_id': 0}))

    opening = income = purchases = withdrawals = transfers = 0
    for d in docs:
        v, t = d['amount']['value'], d['transactionType']
        if   t == 'opening-balance': opening     = v
        elif t == 'income':          income      += v
        elif t == 'purchase':        purchases   += v
        elif t == 'withdrawal':      withdrawals += v
        elif t == 'transfer':        transfers   += v

    return opening + income - (purchases + withdrawals + transfers)

system = get_balance()
gap    = actual - system

print(f"  System balance : ${system:>14,.0f} COP")
print(f"  Actual balance : ${actual:>14,.0f} COP")
print(f"  Gap            : ${gap:>+14,.0f} COP")
print()

# ── No gap ─────────────────────────────────────────────────────────────────────
if gap == 0:
    print("Balances match. Nothing to do.")
    sys.exit(0)

# ── actual > system: system over-counts expenses → remove exact duplicates ─────
if gap > 0:
    print(f"System is under by ${gap:,.0f}. Looking for exact duplicates to remove...")

    dupes = list(col.find(
        {'duplicateStatus': 'exact', 'isTemplate': {'$exists': False},
         'transactionType': {'$in': ['purchase', 'withdrawal']}},
        {'_id': 1, 'emailMessageId': 1, 'amount': 1, 'occurredAt': 1,
         'merchant': 1, 'rawNotification': 1}
    ).sort('amount.value', -1))

    if not dupes:
        print("No exact duplicates found. Gap remains — may need a balancing entry.")
        sys.exit(0)

    removed = 0
    for d in dupes:
        if gap <= 0:
            break
        v = d['amount']['value']
        print(f"  Removing duplicate: {d.get('merchant','?')} ${v:,.0f}  [{d['emailMessageId']}]")
        col.delete_one({'_id': d['_id']})
        gap    -= v
        removed += v

    final = get_balance()
    print()
    print(f"  Removed ${removed:,.0f} in exact duplicates.")
    print(f"  New system balance: ${final:,.0f} COP")
    if gap > 0:
        remaining = actual - final
        print(f"  Remaining gap: ${remaining:,.0f} — no more exact duplicates to remove.")
        print(f"  Consider checking possible-hold transactions manually.")
    elif gap < 0:
        print(f"  Over-removed by ${abs(gap):,.0f}. Balance now slightly above actual.")

# ── actual < system: system over-counts balance → add balancing expense ────────
else:
    gap_abs = abs(gap)
    print(f"System is over by ${gap_abs:,.0f}. Unrecorded expenses missing from the DB.")
    print(f"Inserting balancing expense of ${gap_abs:,.0f} COP...")

    now_col = datetime.now(timezone(datetime.now(timezone.utc).utcoffset())).isoformat()
    now_utc = datetime.now(timezone.utc).isoformat()
    today   = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    doc = {
        'emailMessageId':       None,
        'threadId':             None,
        'occurredAt':           f"{today}T00:00:00-05:00",
        'rawNotification':      None,
        'transactionType':      'purchase',
        'direction':            'out',
        'amount':               {'value': gap_abs, 'currency': 'COP'},
        'merchant':             None,
        'ref':                  None,
        'recipient':            None,
        'sender':               None,
        'category':             'balancing',
        'tags':                 ['balancing-adjustment'],
        'items':                [{'name': 'balancing adjustment', 'quantity': 1, 'unitPrice': gap_abs}],
        'classificationSource': 'manual',
        'importedAt':           now_utc,
        'notes':                f"Manual balancing entry. Actual balance provided: ${actual:,.0f}. System was ${system:,.0f}.",
    }

    col.insert_one(doc)
    final = get_balance()
    print(f"  Done. New system balance: ${final:,.0f} COP")
