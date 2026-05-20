---
name: finance-review
description: Review and classify pending financial transactions. Use when the user asks to review transactions, classify spending, or check what's pending in the finance queue. Reads pending-review.json, presents transactions to the user for categorization in batches of ~10, writes classifications to disk, then runs finance-enrich.py to save to MongoDB. Never calls finance-sync.py — that runs automatically via cron every 30 minutes. Responds with exactly NO_REPLY if the queue is empty.
---

# Finance Review Skill

## Overview

Classifies pending bank transactions by asking the user for a category, then saves them to MongoDB via `finance-enrich.py`. The sync pipeline runs on its own — this skill only handles the queue.

**Key rule:** If `pending-review.json` is empty, respond with exactly `NO_REPLY` — no punctuation, no explanation, no markdown, nothing else.

## Communication style

The user knows this process. Be terse throughout:
- No preamble, no step announcements, no "I'll now run enrich..."
- Conflicts and errors get one short sentence, then the question
- Status updates after enrich: one line (e.g. "Saved 8. 2 older records auto-matched.")
- Only speak up when you need input or something went wrong

## Workflow

### Step 1: Check the queue

Read `/home/danox/.openclaw/workspace/finance/pending-review.json`.

- **Empty array → respond with exactly `NO_REPLY` and stop. No other text.**
- Items present → continue to Step 2.

### Step 2: Save any already-classified items first

Some items may have a `category` field from a previous session where the user classified but enrich never ran. Run enrich immediately for those before asking about anything new:

```bash
python3 /home/danox/.openclaw/workspace/finance/finance-enrich.py
```

Parse stdout as JSON and handle the result (see Step 4 for handling logic). If no pre-classified items exist, skip to Step 3.

### Step 3: Classify transactions

Present up to 10 transactions as a compact numbered list, then ask for categories in one shot. The user knows the process — no preamble, no explanation, no category table.

**Format each line as:**
```
1. May 19 · OXXO INFINITUM · $15,800 · purchase
2. May 19 · Uber · $12,400 · purchase
```

Only include the raw notification if the counterparty name alone is ambiguous. Ask once at the end:

> "Categories? (reply by number, e.g. 1=groceries 2=transport)"

The user may also add items inline, e.g. `1=groceries smokes coke`. Accept that naturally — items are names only, no prices needed.

**Valid categories** (for your reference — do not display this table to the user):
`groceries` `dining` `transport` `health` `utilities` `subscriptions` `clothing` `grooming` `electronics` `entertainment` `car` `rent` `home` `cleaning` `education` `travel` `savings` `income` `cash` `other`

If a category the user gives isn't in this list, flag it — don't use `other` as a workaround.

Once the user replies, **write the full updated array back to `pending-review.json`** before moving on.

### Step 4: Run enrich

```bash
python3 /home/danox/.openclaw/workspace/finance/finance-enrich.py
```

Parse **stdout** as JSON (not just the exit code). Handle each case:

| `status` | Action |
|----------|--------|
| `ok` | Queue cleared. Go back to Step 1 to check for more. |
| `partial` | Check `errors[]` and `conflicts[]` below. |
| `error` | Stop and report the `error` field to the user. |

**`backwardUpdates > 0`:** Tell the user — "N older matching transactions were automatically classified to match."

**`errors[]` non-empty:** Each error has `field` and `message`. Fix those fields on the affected items in `pending-review.json`, then re-run enrich.

**`conflicts[]` non-empty:** For each conflict, read the `instruction` field and ask the user **exactly what it says**. Once the user decides, re-run enrich.

**`queueCleared: false`:** Conflicted items are already back in the queue — do **not** re-run sync. Go straight to Step 3 to re-present those items.

### Step 5: Repeat until empty

Go back to Step 1. Stop when the queue is empty.

## Resources

### Scripts

- **Sync** (cron only — never call manually): `/home/danox/.openclaw/workspace/finance/finance-sync.py`
- **Enrich** (agent calls this): `/home/danox/.openclaw/workspace/skills/finance-review/finance-review/finance-enrich.py`

### Files

- **Queue**: `/home/danox/.openclaw/workspace/finance/pending-review.json`
- **Categories**: `/home/danox/.openclaw/workspace/finance/categories.json`

### Database

- **Collection**: `personal.finance.outgoing` (MongoDB at `172.28.228.83:27017`)

## Completion Checklist

- [ ] Empty queue produced exactly `NO_REPLY` and nothing else
- [ ] Pre-classified leftover items saved before asking user anything
- [ ] All classified items written to disk before enrich was called
- [ ] Enrich stdout parsed as JSON (not just exit code)
- [ ] `backwardUpdates` reported to user if > 0
- [ ] Conflicts surfaced with the `instruction` text verbatim
- [ ] Validation errors fixed in the file and enrich re-run
- [ ] `pending-review.json` is empty after the last successful enrich run
