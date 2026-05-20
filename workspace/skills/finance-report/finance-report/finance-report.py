#!/usr/bin/env python3
"""
Finance spending summary by time window.

Usage:
  python3 finance-report.py <window> [category]

Windows:
  today         Today only
  this-week     Monday of current week → today
  last-week     Previous Mon–Sun
  this-month    1st of current month → today
  last-month    Full previous calendar month
  last-7        Rolling last 7 days
  last-30       Rolling last 30 days
  YYYY-MM-DD:YYYY-MM-DD   Custom range

Optional second arg: filter to one category (e.g. groceries)
"""

import sys
import pymongo
from datetime import date, timedelta, datetime, timezone

# ── Colombia timezone (UTC-5) ─────────────────────────────────────────────────
COL = timezone(timedelta(hours=-5))

def today_col():
    return datetime.now(COL).date()

def get_window(arg):
    today = today_col()
    if arg == 'today':
        return today, today
    if arg == 'last-7':
        return today - timedelta(days=6), today
    if arg == 'last-30':
        return today - timedelta(days=29), today
    if arg == 'this-week':
        return today - timedelta(days=today.weekday()), today
    if arg == 'last-week':
        mon = today - timedelta(days=today.weekday() + 7)
        return mon, mon + timedelta(days=6)
    if arg == 'this-month':
        return today.replace(day=1), today
    if arg == 'last-month':
        first = today.replace(day=1)
        end = first - timedelta(days=1)
        return end.replace(day=1), end
    if ':' in arg:
        s, e = arg.split(':', 1)
        return date.fromisoformat(s), date.fromisoformat(e)
    print(f"Unknown window '{arg}'. Use: today / this-week / last-week / this-month / last-month / last-7 / last-30 / YYYY-MM-DD:YYYY-MM-DD")
    sys.exit(1)

# ── args ──────────────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

start, end = get_window(sys.argv[1])
cat_filter = sys.argv[2] if len(sys.argv) > 2 else None

# ── query ─────────────────────────────────────────────────────────────────────
client = pymongo.MongoClient('mongodb://172.28.228.83:27017/')
col    = client['personal']['finance.outgoing']

query = {
    'occurredAt': { '$gte': start.isoformat(), '$lte': f"{end.isoformat()}T23:59:59" },
    'isTemplate': { '$exists': False }
}
if cat_filter:
    query['category'] = cat_filter

docs = list(col.find(query, {'_id': 0}))

# ── helpers ───────────────────────────────────────────────────────────────────
def cop(n):
    return f"${n:>14,.0f} COP"

def bar(value, total, width=24):
    filled = round(width * value / total) if total else 0
    return '█' * filled + '░' * (width - filled)

# ── compute ───────────────────────────────────────────────────────────────────
total_amount = sum(d['amount']['value'] for d in docs)
by_cat = {}
for d in docs:
    c = d.get('category') or 'uncategorized'
    by_cat.setdefault(c, {'total': 0, 'count': 0})
    by_cat[c]['total']  += d['amount']['value']
    by_cat[c]['count']  += 1

cat_rows = sorted(by_cat.items(), key=lambda x: -x[1]['total'])
max_cat  = cat_rows[0][1]['total'] if cat_rows else 1

largest = max(docs, key=lambda d: d['amount']['value']) if docs else None

# ── print ─────────────────────────────────────────────────────────────────────
W = 66
label = f"{start}  →  {end}" + (f"  [{cat_filter}]" if cat_filter else "")
print('=' * W)
print(f" SPENDING REPORT  —  {label}".center(W))
print('=' * W)
print(f"  Transactions: {len(docs)}     Total: {cop(total_amount)}")
print()

if not docs:
    print("  No transactions found.")
else:
    print('─' * W)
    print('  BY CATEGORY')
    print('─' * W)
    for cat, data in cat_rows:
        b = bar(data['total'], max_cat)
        pct = 100 * data['total'] / total_amount if total_amount else 0
        print(f"  {cat:<22}  {data['count']:>3}x  {b}  {cop(data['total'])}  ({pct:.0f}%)")
    print()

    if largest:
        m   = largest.get('merchant') or '—'
        dt  = largest['occurredAt'][:10]
        cat = largest.get('category', '?')
        print(f"  Largest: {m} · {cop(largest['amount']['value'])} · {dt} · {cat}")

print('=' * W)
