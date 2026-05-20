---
name: meal-plan
description: Process a new meal plan and generate a practical shopping list. Use when the user uploads or describes a meal plan, requests a shopping list, marks shopping items as purchased, or adds new items to the active shopping list. Saves the plan to fitness.meal_plans and the shopping list to shopping.active_list.
---

# Meal Plan Skill

## Overview

Two related workflows: (1) ingesting a new meal plan and generating a shopping list, (2) updating the active shopping list when items are purchased or added.

**Critical distinction:**
- **Meal plan** = nutritional targets and daily meal breakdowns (fitness domain)
- **Shopping list** = practical items to buy at a store (household domain)

## Workflow

### New Meal Plan

#### Step 1: Read the meal plan

Parse:
- Nutritional targets (calories, protein, carbs, fat)
- Daily meal breakdowns
- All ingredients used across the week

#### Step 2: Save to `fitness.meal_plans`

```javascript
db['fitness.meal_plans'].insertOne({
  date: "YYYY-MM-DD",
  week: "YYYY-WNN",
  targets: { calories, protein, carbs, fat },
  days: [...],
  sourceFile: "path/to/file"
})
```

#### Step 3: Generate a practical shopping list

**RULES — do not skip these:**

1. **No raw measurements** — never write "2 eggs" or "150g chicken"
2. **Practical store items** — write "eggs (dozen pack)", "chicken breast (bulk pack)"
3. **Batch quantities** for a week's supply — "4–6 dozen eggs", "1–2 kg rice"
4. **Group by category:** Protein · Produce · Staples · Pantry · Dairy
5. **Add shopping tips** — batch-buy suggestions, check existing stock notes
6. **Include assumptions** — note if the kitchen is assumed empty or partially stocked

Write the list to: `household/shopping/shopping-list-active.md`

#### Step 4: Insert to `shopping.active_list`

```javascript
db['shopping.active_list'].insertOne({
  date: "YYYY-MM-DD",
  sourceMealPlan: "week ref",
  assumptions: ["kitchen: empty", ...],
  items: [...],   // practical items only
  summary: { totalItems, categories }
})
```

#### Step 5: Verify

- `fitness.meal_plans` has the new document
- `shopping-list-active.md` exists and has grouped, practical items
- `shopping.active_list` inserted correctly

---

### Shopping List Update

#### Items purchased

1. Read `shopping.active_list` — find the items
2. Mark as purchased (set `purchased: true`, add `purchasedDate`)
3. Update `shopping-list-active.md` to reflect

#### New items added

1. Append to `shopping.active_list`
2. Recalculate summary (total items, categories)
3. Update `shopping-list-active.md`

## Resources

- **Active list file:** `household/shopping/shopping-list-active.md`
- **DB collections:** `personal.fitness.meal_plans`, `personal.shopping.active_list`
- **Database:** `personal` at `mongodb://172.28.228.83:27017/`
- **Future integration:** `skills/shopping-list/` — when ready, push meal-plan items to `shopping.items` with `source: "meal-plan"` so they appear in the user's live list alongside manual adds

## Completion Checklist

**New meal plan:**
- [ ] Plan saved to `fitness.meal_plans`
- [ ] Shopping list uses practical items (no raw measurements)
- [ ] Items grouped by category
- [ ] `shopping-list-active.md` written
- [ ] `shopping.active_list` inserted
- [ ] Both DB and file verified

**Shopping update:**
- [ ] Active list read
- [ ] Purchased items marked / new items appended
- [ ] Summary recalculated
- [ ] File updated
