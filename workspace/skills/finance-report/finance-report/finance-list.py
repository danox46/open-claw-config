#!/usr/bin/env python3
"""
List transactions for a time window, grouped by day.

Usage:
  python3 finance-list.py <window> [category]

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
from collections import defaultdict

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

docs = sorted(
    col.find(query, {'_id': 0}),
    key=lambda d: d['occurredAt']
)

# ── helpers ───────────────────────────────────────────────────────────────────
def cop(n):
    return f"${n:,.0f}"

def fmt_items(items):
    if not items:
        return ''
    names = [i['name'] for i in items if i.get('name') and i['name'] != 'unclassified']
    return ', '.join(names) if names else ''

# ── group by day ──────────────────────────────────────────────────────────────
by_day = defaultdict(list)
for d in docs:
    day = d['occurredAt'][:10]
    by_day[day].append(d)

# ── print ─────────────────────────────────────────────────────────────────────
label = f"{start}  →  {end}" + (f"  [{cat_filter}]" if cat_filter else "")
print(f"Transactions  —  {label}  ({len(docs)} total)\n")

if not docs:
    print("  No transactions found.")
    sys.exit(0)

total = 0
for day in sorted(by_day):
    day_docs = by_day[day]
    day_total = sum(d['amount']['value'] for d in day_docs)
    total += day_total

    # Day header
    dt = datetime.fromisoformat(day_docs[0]['occurredAt'])
    weekday = dt.strftime('%a')
    print(f"  {weekday} {day}  ({cop(day_total)})")

    for d in day_docs:
        time    = d['occurredAt'][11:16]
        merchant = d.get('merchant') or '—'
        amount  = cop(d['amount']['value'])
        cat     = d.get('category') or '?'
        items   = fmt_items(d.get('items', []))
        item_str = f"  · {items}" if items else ''
        print(f"    {time}  {merchant:<28}  {amount:>12} COP  {cat}{item_str}")

    print()

print(f"  Total: {cop(total)} COP  ({len(docs)} transactions)")
