---
name: balancing
description: Reconcile the system's calculated account balance against the actual bank balance. Use when the user provides their current bank balance, asks what the system thinks their balance is, or wants to remove duplicates or add a balancing entry.
---

# Balancing Skill

## Scripts

### Check system balance
```bash
python3 /home/danox/.openclaw/workspace/skills/balancing/balancing/finance-balance.py
```
Calculates opening + income − expenses from MongoDB. Excludes `duplicateStatus: "exact"` records.

### Reconcile against actual balance
```bash
python3 /home/danox/.openclaw/workspace/skills/balancing/balancing/finance-reconcile.py <actual_balance>
```
Compares system balance to the user's actual bank balance and fixes the gap:

| Situation | Action |
|---|---|
| Actual > System | System over-counts expenses — removes exact duplicates (largest first) until balanced |
| Actual < System | System under-counts expenses — inserts a `balancing` expense for the gap |

---

## Duplicate statuses

`duplicateStatus` is set automatically by `finance-import.py` on new imports:

| Value | Meaning |
|---|---|
| `"exact"` | Same `rawNotification` text already exists — Bancolombia sent the same email twice. Excluded from balance calculations. |
| *(absent)* | Normal transaction |

Possible holds (same merchant, rapid consecutive charges, different amounts) are **not** auto-marked — Uber and similar services adjust hold amounts before final charge, making automatic detection unreliable. Flag these manually if needed.

---

## When to use

- User says "my balance is X" → run `finance-reconcile.py X`
- User asks "what does the system think my balance is?" → run `finance-balance.py`
- User asks to clean up duplicates without a target balance → run `finance-balance.py`, show current dupes via mongosh, then ask which to remove

## Notes

- Balancing entries use `category: "balancing"` — filter them out of spending reports with `{ category: { $ne: "balancing" } }`
- After reconciling, always confirm the new balance with `finance-balance.py`
