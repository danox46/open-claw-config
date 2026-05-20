---
name: irl-event-search
description: Search for and track in-real-life hobby events and workshops in Bogotá. Use when the user asks about upcoming hobby events, requests a daily or weekly event report, or when triggered by a cron. Searches for both approved hobbies and active pitches, deduplicates against previously pitched events, saves to personal.hobby_events, and delivers a notification.
---

# IRL Event Search Skill

## Overview

Finds upcoming workshops, classes, and events for active hobbies and pitches in Bogotá. Runs as daily (next 7 days) or weekly (next 30 days). Always deduplicates against events already in the database.

## Workflow

### Step 1: Determine search scope

- **Daily:** today + next 7 days → morning notification
- **Weekly:** next 30 days → Sunday evening notification
- **Manual:** date range and hobbies specified by user

### Step 2: Get active hobbies and pitches

Query both:
```javascript
// Approved hobbies
db['hobbies.global.hobbies_list'].find({ status: "active", isTemplate: { $exists: false } })

// Active pitches
db.hobby_pitches.find({ status: { $in: ["testing", "approved"] }, isTemplate: { $exists: false } })
```

Also read `hobbies/pitches-active.md` as a fallback if DB is stale.

### Step 3: Search for events

For each hobby (approved + pitches), search:
- General web: `[hobby] bogota [date range] taller clase workshop`
- Social/Facebook: `[hobby] bogota eventos [month]`
- Language: Spanish preferred, English fallback

### Step 4: Deduplicate

Check `personal.hobby_events` for existing records in the date range. Mark any match (same name + date) as duplicate — do not re-insert.

Unique key: `event_name` + `event_date` + `hobby`

### Step 5: Categorize and prioritize

- **Category:** workshop · class · seminar · expo · festival · other
- **Priority:** high (≤3 days away) · medium (4–14 days) · low (15+ days)

### Step 6: Save to database

```javascript
db.hobby_events.insertOne({
  hobby, event_name, event_date, event_time,
  price, currency, location, address, website, instructor,
  status: "pending",      // pending / approved / rejected / cancelled
  rejection_reason: null,
  source_platform,
  research_date: "YYYY-MM-DD",
  category, priority,
  ttl_days: 14
})
```

Only insert if not already present.

### Step 7: Notify user

**Daily:**
> "Found N new hobby events for this week. [Top 3–5 with name, date, price]"

**Weekly:**
> "Weekly event report: N events across X hobbies for [date range]. [Grouped by hobby, high-priority first]"

Keep it scannable — name, date, price, category. Full details on request.

## Schema — `hobby_events`

| Field | Type | Notes |
|-------|------|-------|
| `hobby` | string | |
| `event_name` | string | |
| `event_date` | string | YYYY-MM-DD |
| `event_time` | string | HH:MM |
| `price` | number | COP |
| `location` | string | Venue name |
| `address` | string | |
| `website` | string | |
| `instructor` | string | |
| `status` | string | `pending` / `approved` / `rejected` / `cancelled` |
| `rejection_reason` | string | Set when status = rejected |
| `source_platform` | string | |
| `research_date` | string | YYYY-MM-DD |
| `category` | string | workshop / class / expo / festival / other |
| `priority` | string | high / medium / low |
| `ttl_days` | number | Auto-expiry hint |

## Resources

- **Search script:** `/home/danox/.openclaw/workspace/skills/irl-event-search/irl-event-search/search-irl-events.mjs`
- **Active pitches:** `/home/danox/.openclaw/workspace/hobbies/pitches-active.md`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`
- **Related skill:** `skills/hobby-pitch/` — for managing pitches
- **Cron schedules:** daily at 08:00 Bogotá · weekly Sunday at 20:00 Bogotá

## Completion Checklist

- [ ] Hobbies and pitches retrieved from DB
- [ ] Events searched for each hobby
- [ ] Duplicates checked and excluded
- [ ] New events saved to `hobby_events` with `status: "pending"`
- [ ] Notification delivered (concise — not a wall of text)
