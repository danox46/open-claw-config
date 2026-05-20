---
name: finance-report
description: Run standard spending reports. Use when the user asks how much they spent (last week, last month, this month, this week, today, by category, or any time window). Run the pre-built scripts — do not write ad-hoc queries.
---

# Finance Report Skill

## Scripts

### Summary (totals by category)
```bash
python3 /home/danox/.openclaw/workspace/skills/finance-report/finance-report/finance-report.py <window> [category]
```

### Transaction list (one line per transaction, grouped by day)
```bash
python3 /home/danox/.openclaw/workspace/skills/finance-report/finance-report/finance-list.py <window> [category]
```

---

## Window values

| What the user says | Argument |
|---|---|
| last week / last calendar week | `last-week` |
| this week / so far this week | `this-week` |
| last month | `last-month` |
| this month / so far this month | `this-month` |
| last 7 days | `last-7` |
| last 30 days | `last-30` |
| today | `today` |
| specific range | `YYYY-MM-DD:YYYY-MM-DD` |

## Optional category filter

Pass a category as the second argument to narrow results:
```bash
python3 /home/danox/.openclaw/workspace/skills/finance-report/finance-report/finance-report.py this-month groceries
python3 /home/danox/.openclaw/workspace/skills/finance-report/finance-report/finance-list.py last-week transport
```

Valid categories: `groceries` `dining` `transport` `health` `utilities` `subscriptions` `clothing` `grooming` `electronics` `entertainment` `car` `rent` `home` `cleaning` `education` `travel` `savings` `income` `cash` `other`

---

## Which script to use

- **"How much did I spend…"** → run `finance-report.py` (summary)
- **"List / show my transactions…"** → run `finance-list.py` (flat list)
- **"How much on groceries…"** → `finance-report.py this-month groceries`
- **"Show me my OXXO transactions"** → `finance-list.py` — merchant filtering isn't a flag, but OXXO rows are visible in the output

Relay the script output to the user as-is. Do not reformat or summarize unless asked.
