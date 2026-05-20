---
name: goal-tracking
description: Scaffold full tracking infrastructure for a new trackable item. Use when the user says "I want to track X" — gym sessions, sleep, spending in a new category, anything. Creates the workspace folder, a simple data-entry queue file, MongoDB collections with proper naming, a dedicated SKILL.md for the new domain, and wires it into the weekly summary. Does not perform the actual tracking — it builds the system that will.
---

# Goal Tracking Skill

## Overview

When the user decides to track something new, this skill builds all the infrastructure: folder, queue file, DB collections, a dedicated skill, and weekly summary integration. Think of it as the scaffolding layer — finance tracking was built the same way.

Use the finance domain as the reference pattern throughout.

## Workflow

### Step 1: Define the domain

Ask the user:
- **What are we tracking?** (e.g., gym sessions, sleep, weight, reading)
- **What fields matter?** (e.g., for gym: exercise, sets, reps, duration, notes)
- **What's the entry pattern?** User feeds data manually / automated sync / cron pull

Propose a short domain name (e.g., `gym`, `sleep`, `reading`) — this becomes the folder name, collection prefix, and skill name. Confirm with the user before proceeding.

### Step 2: Create the workspace folder and queue file

```
workspace/<domain>/
workspace/<domain>/pending-entry.json   ← starts as []
```

`pending-entry.json` is the simple data-entry queue — the user or agent drops entries here, a save script (created later or manually) persists them to MongoDB. Start it as an empty array.

### Step 3: Create MongoDB collections

Naming convention: `personal.<domain>.<collection>` — never use a bare `goals.*` prefix.

Minimum collections (adjust based on Step 1):

| Collection | Purpose |
|---|---|
| `personal.<domain>.stats` | Individual session/event records |
| `personal.<domain>.weekly` | Weekly aggregates (if applicable) |

For each collection insert one template document with `isTemplate: true` that matches the agreed schema. Include at minimum: `date` (YYYY-MM-DD), the core metric fields, and `notes`.

### Step 4: Update `db-map.md`

Add the new collections to the Existing Collections table:
- Collection name
- Required fields
- File path(s)
- Entry method (manual / agent / cron)

### Step 5: Create the dedicated skill

Create `/home/danox/.openclaw/workspace/skills/<domain>/<domain>/SKILL.md` following the same structure as `finance-review`:

- **Frontmatter:** `name` + `description` that triggers when the user mentions this domain
- **Overview:** what the skill tracks and how data gets in
- **Workflow:** how to add entries, query recent data, handle the pending-entry.json queue
- **Schema:** field names and types
- **Resources:** file paths, collection names, DB connection
- **Completion checklist**

### Step 6: Wire into weekly summary

Update `/home/danox/.openclaw/workspace/skills/weekly-summary/weekly-summary/SKILL.md`:
- Add the new collection(s) to the list of domains queried each week
- Add the relevant aggregate fields (what to sum/average/count)

### Step 7: Ask about cron

> "Should I set up a cron to automatically pull or save <domain> data? Or will you feed it manually?"

If yes: collect schedule and trigger details, but note the cron itself needs to be configured separately (flag for user).

### Step 8: Ask about standard reports

> "Do you want a standard report format for <domain> — e.g., weekly totals, trends, personal bests?"

If yes: add a Reports section to the new skill's SKILL.md describing what to show and how to calculate it.

## Naming conventions

| Thing | Pattern | Example |
|---|---|---|
| Workspace folder | `workspace/<domain>/` | `workspace/gym/` |
| Queue file | `<domain>/pending-entry.json` | `gym/pending-entry.json` |
| DB collection (stats) | `personal.<domain>.stats` | `personal.gym.stats` |
| DB collection (weekly) | `personal.<domain>.weekly` | `personal.gym.weekly` |
| Skill folder | `skills/<domain>/<domain>/SKILL.md` | `skills/gym/gym/SKILL.md` |

## Resources

- **Reference pattern:** `skills/finance-review/` and `workspace/finance/`
- **Weekly summary skill:** `skills/weekly-summary/weekly-summary/SKILL.md`
- **Schema reference:** `db-map.md`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`

## Completion Checklist

- [ ] Domain name confirmed with user
- [ ] `workspace/<domain>/` folder created
- [ ] `pending-entry.json` created as empty array
- [ ] MongoDB collections created with template documents
- [ ] `db-map.md` updated
- [ ] `skills/<domain>/<domain>/SKILL.md` created
- [ ] Weekly summary skill updated to include new domain
- [ ] Cron question asked and flagged if needed
- [ ] Reports question asked and added to skill if wanted
