#!/usr/bin/env python3
"""
Calculate current system account balance from MongoDB.

Excludes transactions marked duplicateStatus="exact" from all calculations.

Usage:
  python3 finance-balance.py
"""

import pymongo

client = pymongo.MongoClient('mongodb://172.28.228.83:27017/')
col    = client['personal']['finance.outgoing']

docs = list(col.find({
    'isTemplate':     {'$exists': False},
    'duplicateStatus': {'$ne': 'exact'},
}, {'_id': 0, 'transactionType': 1, 'amount': 1}))

opening     = 0
income      = 0
purchases   = 0
withdrawals = 0
transfers   = 0

for d in docs:
    v = d['amount']['value']
    t = d['transactionType']
    if   t == 'opening-balance':   opening     = v
    elif t == 'income':            income      += v
    elif t == 'purchase':          purchases   += v
    elif t == 'withdrawal':        withdrawals += v
    elif t == 'transfer':          transfers   += v

total_out = purchases + withdrawals + transfers
balance   = opening + income - total_out

W = 52
print('=' * W)
print(' SYSTEM BALANCE'.center(W))
print('=' * W)
print(f'  Opening balance   ${opening:>14,.0f} COP')
print(f'  + Income          ${income:>14,.0f} COP')
print(f'  - Purchases       ${purchases:>14,.0f} COP')
print(f'  - Withdrawals     ${withdrawals:>14,.0f} COP')
print(f'  - Transfers       ${transfers:>14,.0f} COP')
print('─' * W)
print(f'  Balance           ${balance:>14,.0f} COP')
print('=' * W)
print(f'  (exact duplicates excluded from all figures)')
