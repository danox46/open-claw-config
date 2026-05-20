---
name: weekly-summary
description: Generate and save weekly aggregate summaries across tracking domains. Use when the user asks for a weekly summary, at end of week, or when triggered by a Sunday cron. Queries daily records, calculates aggregates, saves to file and MongoDB, then notifies the user — but does NOT send the full report unprompted. The user requests specific reports separately.
---

# Weekly Summary Skill

## Overview

Aggregates daily tracking records into weekly summaries, saves them to disk and MongoDB, then sends a brief ready-notification. The full report is only delivered if the user asks for it.

**Key rule:** Notify with "Weekly metrics summary is ready" — do not dump the full summary unless the user requests it.

## Workflow

### Step 1: Verify collections

Check `db-map.md` for:
- Which collections have daily records (`*.daily_stats`, etc.)
- Confirm schema matches expected fields
- Determine the week range (Monday–Sunday or Sunday–Saturday)

### Step 2: Query daily records

```javascript
db['fitness.daily_stats'].find({
  date: { $gte: "YYYY-MM-DD", $lte: "YYYY-MM-DD" },
  isTemplate: { $exists: false }
})
```

Repeat for each active tracking domain.

### Step 3: Calculate aggregates

- Totals and averages for numeric fields
- Top categories or tags (if applicable)
- Week-over-week delta vs previous week

### Step 4: Save weekly file

- Path: `<domain>/weeklystats.json`
- Include: week start/end dates, aggregates, record count

### Step 5: Insert to MongoDB

```javascript
db['fitness.weekly_stats'].insertOne({
  weekStart: "YYYY-MM-DD",
  weekEnd:   "YYYY-MM-DD",
  // calculated aggregates
})
```

Collection naming: `<domain>.weekly_stats`

### Step 6: Notify user

Send exactly this (adapt domain):

> "Weekly metrics summary is ready. You can now request specific reports for the week."

**Do not send the full summary unless asked.**

### Step 7: Verify

- Weekly file exists on disk
- DB document count is correct
- Notification sent

## Resources

- **Schema reference:** `db-map.md`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`
- **Cron schedule:** Sunday at 19:00 Bogotá time

## Completion Checklist

- [ ] `db-map.md` checked for collection schemas
- [ ] Daily records queried (templates excluded)
- [ ] Aggregates calculated
- [ ] Weekly JSON file saved to disk
- [ ] Document inserted in MongoDB
- [ ] Brief ready-notification sent (not the full report)
- [ ] File and DB count verified
