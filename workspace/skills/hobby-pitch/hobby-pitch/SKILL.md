---
name: hobby-pitch
description: Manage hobby pitches — lightweight trials before committing to full hobby tracking. Use when the user wants to start testing a new hobby, update a pitch's status or next steps, convert a pitch to a full approved hobby, or reject a pitch. Writes to personal.hobby_pitches and hobbies/pitches-active.md.
---

# Hobby Pitch Skill

## Overview

A pitch is a temporary trial for a hobby you're not yet sure about. When approved, it gets a full folder and tracking collections. When rejected, the reason is recorded and it's archived.

**Status values:** `suggested` → `testing` → `approved` or `rejected`

- `suggested` — created by weekly discovery, not yet accepted by the user
- `testing` — user accepted; actively testing the hobby
- `approved` — converted to full hobby tracking
- `rejected` — abandoned; reason recorded

## Workflow

### Promote Suggested → Testing

When the user accepts a suggested pitch from weekly discovery:

```javascript
db.hobby_pitches.updateOne(
  { hobbyName: "...", status: "suggested" },
  { $set: {
      status: "testing",
      startDate: "YYYY-MM-DD",   // today
      nextSteps: [...],
      conversionCriteria: { consistency: false, commitment: false, time: false }
  }}
)
```

Append entry to `hobbies/pitches-active.md`.

---

### Add New Pitch

1. Insert into `personal.hobby_pitches`:

```javascript
db.hobby_pitches.insertOne({
  hobbyName: "...",
  status: "testing",
  startDate: "YYYY-MM-DD",
  notes: "...",
  nextSteps: [...],
  conversionCriteria: { consistency: false, commitment: false, time: false },
  convertedDate: null,
  convertedTo: null
})
```

2. Append entry to `hobbies/pitches-active.md`

---

### Update Pitch (notes / next steps)

```javascript
db.hobby_pitches.updateOne(
  { hobbyName: "..." },
  { $set: { notes: "...", nextSteps: [...] } }
)
```

---

### Convert Pitch to Full Hobby

1. Check conversion criteria with user (consistency · commitment · time)
2. Update record:

```javascript
db.hobby_pitches.updateOne(
  { hobbyName: "..." },
  { $set: {
      status: "approved",
      convertedDate: "YYYY-MM-DD",
      "conversionCriteria.consistency": true,
      "conversionCriteria.commitment": true,
      "conversionCriteria.time": true
  }}
)
```

3. Insert into `hobbies.global.hobbies_list` — this is what makes the hobby visible to IRL event searches and weekly summaries:

```javascript
db['hobbies.global.hobbies_list'].insertOne({
  hobbyName: "...",
  startDate: "YYYY-MM-DD",
  status: "active",
  category: "...",   // creative / physical / intellectual / social / technical
  budget: 0,
  notes: "..."
})
```

4. Create full hobby structure:
   - Folder: `hobbies/<hobbyName>/`
   - Collections: `hobbies.<hobbyName>.daily`, `hobbies.<hobbyName>.weekly`, `hobbies.<hobbyName>.info`
   - Insert template documents (`isTemplate: true`) in each
   - Update `db-map.md` with new collections

---

### Reject Pitch

```javascript
db.hobby_pitches.updateOne(
  { hobbyName: "..." },
  { $set: { status: "rejected", rejectionReason: "..." } }
)
```

Update `hobbies/pitches-active.md` to mark as rejected.

## Schema — `hobby_pitches`

| Field | Type | Notes |
|-------|------|-------|
| `hobbyName` | string | |
| `status` | string | `suggested` / `testing` / `approved` / `rejected` |
| `startDate` | string | YYYY-MM-DD |
| `notes` | string | |
| `nextSteps` | array | |
| `conversionCriteria` | object | `{consistency, commitment, time}` booleans |
| `convertedDate` | string | null until approved |
| `convertedTo` | string | null until approved |
| `rejectionReason` | string | null until rejected |

## Resources

- **Active pitches file:** `hobbies/pitches-active.md`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`
- **Related skill:** `skills/hobby-research/` — for researching a hobby before pitching

## Completion Checklist

- [ ] DB record inserted / updated
- [ ] `pitches-active.md` updated
- [ ] Next steps defined (new pitches)
- [ ] Conversion criteria confirmed with user (conversions)
- [ ] Inserted into `hobbies.global.hobbies_list` with `status: "active"` (if approved)
- [ ] Full hobby structure created (if approved): folder + 3 collections + templates + db-map
- [ ] Rejection reason documented (if rejected)
