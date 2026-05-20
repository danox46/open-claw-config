---
name: hobby-research
description: Research hobbies in depth — find courses, workshops, instructors, and pricing in Bogotá. Two modes: (1) targeted research when the user asks about a specific hobby, (2) weekly discovery that reads hobby-research-config.json, searches for new hobby candidates, and pitches good ones. Saves findings to personal.hobby_events and notifies the user with a compact summary.
---

# Hobby Research Skill

## Overview

Two modes:
- **Targeted** — user asks about a specific hobby, deep-dive on that one
- **Weekly discovery** — cron-triggered, reads config, finds new hobby candidates, creates pitches, notifies user

Bogotá-focused, Spanish-first. Distinct from IRL event search (which sweeps for events on existing hobbies).

## Workflow — Targeted Research

Use when the user names a specific hobby to research.

### Step 1: Determine language and search strategy

Default to Spanish searches — Bogotá hobby providers almost exclusively use Spanish on social media.

Search in this order:
1. `taller de [hobby] bogota`
2. `curso de [hobby] bogota`
3. `[hobby] bogota eventos`
4. `escuela de [hobby] bogota`
5. `[hobby] bogota instagram` / `[hobby] bogota facebook`

Only fall back to English (`[hobby] workshop bogota`) if Spanish returns nothing useful.

### Step 2: Platform priority

Work through these in order — stop when you have 3+ solid options:

1. **Instagram** — most Bogotá hobby providers live here; search hashtags like `#[hobby]bogota`, `#talleres[hobby]bogota`
2. **Facebook Events/Groups** — search `[hobby] bogota eventos`, check local groups
3. **Google Maps** — find physical schools/studios, check reviews and contact info
4. **Eventbrite / local classifieds** — `listado.co`, `gruposurbano.com.co`
5. **Direct websites** — last resort; many don't maintain them

### Step 3: Extract per option

For each opportunity, get:
- **Date & time** — exact, not "coming soon"
- **Price** — specific amount in COP, not "contact us"
- **Location** — physical address or online link
- **Instructor** — name and credentials if available
- **Registration** — link or DM method
- **Source** — platform and post date (prefer last 30 days)

Skip options missing date or price — flag them as unverified rather than including with gaps.

### Step 4: Save to database

```javascript
db.hobby_events.insertOne({
  hobby: "[hobbyName]",
  event_name: "[course/workshop name]",
  event_date: "YYYY-MM-DD",
  event_time: "HH:MM",
  price: 0,           // COP
  currency: "COP",
  location: "...",
  address: "...",
  website: "...",
  instructor: "...",
  source_platform: "instagram | facebook | google | other",
  research_date: "YYYY-MM-DD",
  status: "pending",
  category: "workshop | class | seminar | expo | other",
  priority: "high | medium | low",   // high = ≤3 days, medium = 4–14, low = 15+
  ttl_days: 14
})
```

Only insert if not already present (deduplicate on `event_name` + `event_date`).

### Step 5: Notify user

Deliver a compact summary — do not dump the full structured report unprompted:

> "Found N options for [hobby]:
> 1. [Name] — [date] · $[price] COP · [location]
> 2. ...
> Best option: [brief recommendation]"

Full details (instructor, registration link, etc.) on request.

---

## Workflow — Weekly Discovery

Use when triggered by cron or when the user asks for new hobby ideas.

### Step 1: Read the config and current pitches

Read `/home/danox/.openclaw/workspace/hobbies/hobby-research-config.json`.

Extract:
- `preferences.categories` — only look in these domains
- `preferences.vibe` — use this as the research brief
- `preferences.socialGoal` — use to evaluate social fit of each candidate
- `preferences.preferredFormats` — prefer hobbies with these entry formats (recurring workshops, drop-in classes, etc.)
- `preferences.location.preferredZones` — prefer hobbies with classes/communities in these zones
- `preferences.budget` — filter out hobbies that exceed these limits
- `preferences.timeCommitment` — filter out hobbies that don't fit
- `avoid` — skip anything matching these notes

Always query `personal.hobby_pitches` for hobbies already in `testing` or `suggested` status and skip those:

```javascript
db.hobby_pitches.find({ status: { $in: ["testing", "suggested"] } })
```

### Step 2: Search for new hobby candidates

Look for hobbies that match the config profile — not events for existing hobbies, but hobby types themselves. Good sources:
- `hobbies bogota [category] ideas` / `actividades creativas bogota`
- `mejores hobbies para adultos bogota`
- Reddit, local blogs, community boards for what people in Bogotá are doing
- Platforms from targeted research (Instagram, Facebook groups)

Aim for 5–8 raw candidates. Filter against the config: budget, time, avoid list, current pitches, and preferred formats. Aim to present 3 strong options that fit the `socialGoal` and have classes available in the `preferredZones`.

### Step 3: For each candidate, do a quick scan

Don't do a full targeted research pass — just enough to confirm the hobby is viable:
- Classes or communities exist in Bogotá
- Rough cost range fits the budget
- Time commitment is realistic

### Step 4: Create pitch entries for the top candidates

For each strong candidate, create a `status: "suggested"` entry using the hobby-pitch skill — this surfaces it to the user without automatically adding it to their testing list:

```javascript
db.hobby_pitches.insertOne({
  hobbyName: "...",
  status: "suggested",
  startDate: "YYYY-MM-DD",
  notes: "Weekly discovery — [one sentence why this fits the config]",
  nextSteps: [],
  source: "weekly-discovery"
})
```

### Step 5: Notify user

Compact message — one line per candidate:

> "3 new hobby ideas this week:
> 1. [Hobby] — [category] · ~$[cost]/session · [one sentence why]
> 2. ...
> 3. ...
> Reply with a number to add it as a testing pitch, or pass."

If the user picks one, update the pitch status from `"suggested"` to `"testing"` via the hobby-pitch skill.

---

## Resources

- **Config file:** `hobbies/hobby-research-config.json` — edit to change discovery preferences
- **DB collections:** `personal.hobby_events`, `personal.hobby_pitches`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`
- **Related skill:** `skills/irl-event-search/` — periodic event sweep for existing hobbies
- **Related skill:** `skills/hobby-pitch/` — for managing pitches after research

## Completion Checklist

**Targeted research:**
- [ ] Spanish searches attempted first
- [ ] At least 3 platforms checked
- [ ] Each option has confirmed date and price (not vague)
- [ ] Results saved to `hobby_events` with `status: "pending"`
- [ ] Compact summary delivered with recommendation

**Weekly discovery:**
- [ ] Config file read
- [ ] Current pitches fetched from DB (testing + suggested status)
- [ ] Candidates filtered against budget, time, avoid list, existing pitches, preferredFormats, preferredZones
- [ ] Top 3 candidates have quick viability scan done
- [ ] Pitch entries created with `status: "suggested"`
- [ ] Compact notification delivered — one line per candidate
- [ ] User response handled (suggested → testing if accepted)
