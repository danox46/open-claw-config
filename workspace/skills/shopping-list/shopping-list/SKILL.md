---
name: shopping-list
description: Manage a live shopping list. Use when the user says they need to buy something, asks what's on the list, marks items as bought or done, or removes an item. Supports short / mid / long term timeframes with priority levels for mid and long term. Writes to shopping.items in MongoDB.
---

# Shopping List Skill

## Overview

A persistent, conversational shopping list. The user tells the agent what to add; asks what's pending; marks items bought. DB-first — no file needed.

**Timeframes:**
- `short` — buy soon / this week (groceries, immediate needs). Default when no timeframe is mentioned.
- `mid` — buy within the next few weeks / this month (has priority)
- `long` — buy eventually / when budget allows (has priority)

**Priority** (`high` / `medium` / `low`) — only applies to `mid` and `long` term items. Ignored for short term. Default `medium` if timeframe is mid/long but priority not stated.

**Status values:** `pending` → `bought`

**Two future integrations (design is ready, not yet wired):**
- **Meal plan** — meal-plan skill will push items here with `source: "meal-plan"`, always as `short` term.
- **Finance/budget** — `estimatedPrice` on items lets the finance skill pre-calculate spending before a trip.

---

## Workflow

### Add Items

Parse the user's message for item names, timeframe, and priority. A single message can add many items.

For each item, infer or default:
- `timeframe` — from message context (`"eventually"`, `"next month"` → `long`; `"soon"`, `"this week"` → `short`; explicit `"mid term"` / `"long term"`). Default: `short`.
- `priority` — only for mid/long. Parse from message (`"high priority"`, `"urgent"`, `"whenever"` → `low`). Default: `medium`.
- `category` — see table below
- `quantity` + `unit` if specified
- `estimatedPrice` — only if the user mentioned a price

```javascript
db['shopping.items'].insertOne({
  name: "...",
  quantity: 1,
  unit: null,             // "kg", "L", "pack", "dozen", etc.
  category: "...",        // groceries / household / pharmacy / personal-care / other
  estimatedPrice: null,   // COP — only if user mentioned a price
  timeframe: "short",     // "short" | "mid" | "long"
  priority: null,         // null for short; "high" | "medium" | "low" for mid/long
  status: "pending",
  source: "manual",       // "manual" | "meal-plan"
  addedDate: "YYYY-MM-DD",
  boughtDate: null,
  notes: null
})
```

Deduplicate: if a `pending` item with the same `name` already exists, skip it and tell the user.

**Category inference:**

| Category | Examples |
|---|---|
| `groceries` | food, drinks, snacks, condiments, spices |
| `household` | cleaning products, paper goods, trash bags, foil |
| `pharmacy` | medicine, vitamins, supplements |
| `personal-care` | shampoo, soap, deodorant, razors |
| `other` | electronics, clothes, furniture, anything else |

After adding, confirm tersely:
> "Added: eggs, milk · short · groceries"
> "Added: headphones · mid · high priority · other"

---

### View List

**Default ("what do I need?" / "show my list")** → short term only, grouped by category.

**"mid term list"** → mid term, sorted by priority (high → medium → low), then grouped by category.

**"long term list"** → long term, same priority sort.

**"everything" / "full list"** → all pending, grouped by timeframe section (Short → Mid → Long), then category within each section.

#### Short term query:
```javascript
db['shopping.items'].find({ status: "pending", timeframe: "short" })
  .sort({ category: 1, addedDate: 1 })
```

#### Mid / Long term query:
```javascript
const priorityOrder = { high: 1, medium: 2, low: 3 };
db['shopping.items'].find({ status: "pending", timeframe: "mid" })
  // sort in JS: by priority then addedDate
```

#### Format — Short term:
```
Shopping list · short term (N items):

Groceries
  • eggs (1 dozen)
  • milk

Household
  • trash bags
```

#### Format — Mid / Long term:
```
Shopping list · mid term (N items):

[high priority]
  • headphones · other
  • new backpack · personal-care

[medium priority]
  • desk lamp · household

[low priority]
  • board game · other
```

#### Format — Full list:
```
Shopping list · all (N items):

── Short term ──
Groceries: eggs, milk
Household: trash bags

── Mid term ──
[high] headphones · [medium] desk lamp

── Long term ──
[low] new couch · household
```

If a section is empty, omit it. If everything is empty: "Nothing on the list."

---

### Mark Bought

Match by name (case-insensitive, partial match ok). Works across all timeframes. The user can name one item, several, or say "all" / "done shopping" / "got everything" (marks all `short` term as bought — mid/long require explicit naming).

```javascript
db['shopping.items'].updateOne(
  { name: /item/i, status: "pending" },
  { $set: { status: "bought", boughtDate: "YYYY-MM-DD" } }
)
```

Confirm:
> "Marked bought: eggs, milk ✓"

---

### Change Timeframe / Priority

When the user says "move headphones to long term" or "make the lamp high priority":

```javascript
db['shopping.items'].updateOne(
  { name: /headphones/i, status: "pending" },
  { $set: { timeframe: "long", priority: "medium" } }
)
```

Confirm: "Headphones moved to long term · medium priority."

---

### Remove Item

For items added by mistake (still pending). Hard-delete.

```javascript
db['shopping.items'].deleteOne({ name: /item/i, status: "pending" })
```

---

### Clear Bought Items

Run when the user says "clear the list", "clean up", or "start fresh."

```javascript
db['shopping.items'].deleteMany({ status: "bought" })
```

Confirm: "Cleared N bought items."

---

## Schema — `shopping.items`

| Field | Type | Notes |
|---|---|---|
| `name` | string | item name, lowercase preferred |
| `quantity` | number | default 1 |
| `unit` | string | null if not specified |
| `category` | string | `groceries` / `household` / `pharmacy` / `personal-care` / `other` |
| `estimatedPrice` | number | COP, null if unknown — for future budget tie-in |
| `timeframe` | string | `short` / `mid` / `long` — default `short` |
| `priority` | string | `high` / `medium` / `low` — null for short term, default `medium` for mid/long |
| `status` | string | `pending` / `bought` |
| `source` | string | `manual` / `meal-plan` |
| `addedDate` | string | YYYY-MM-DD |
| `boughtDate` | string | null until bought |
| `notes` | string | null unless needed |

---

## Future Integrations

### Meal-plan → Shopping List
When ready: update `meal-plan` skill to push items to `shopping.items` with `source: "meal-plan"` and `timeframe: "short"`. They appear in the default short-term view alongside manual grocery adds.

### Finance / Budget Planning
When ready: before a shopping trip, sum `estimatedPrice` of pending short-term items:
```javascript
db['shopping.items'].aggregate([
  { $match: { status: "pending", timeframe: "short", estimatedPrice: { $ne: null } } },
  { $group: { _id: null, total: { $sum: "$estimatedPrice" } } }
])
```
For mid/long term budget forecasting, query by timeframe without the short filter.

---

## Resources

- **DB collection:** `personal` → `shopping.items`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`
- **Related skill:** `skills/meal-plan/` — will eventually push items here as short term
- **Related skill:** `skills/finance-review/` — will eventually read `estimatedPrice` for budget

## Completion Checklist

- [ ] Timeframe inferred from context; default `short`
- [ ] Priority inferred for mid/long; default `medium`; null for short
- [ ] Category inferred for each item
- [ ] Deduplication checked before insert
- [ ] Terse confirmation includes timeframe and priority
- [ ] Default view shows short term only, grouped by category
- [ ] Mid/long view sorts by priority then groups by category
- [ ] Full view sections by timeframe then category
- [ ] "All" / "done shopping" marks short term only; mid/long require explicit name
- [ ] Change timeframe/priority supported
- [ ] Remove only deletes pending items
- [ ] Clear deletes bought items
