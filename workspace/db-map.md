# Database Map

**Database:** `personal`  
**Purpose:** Persistent tracking of fitness, shopping, and personal metrics  
**Created:** 05-10-2026

---

## 📊 Existing Collections

### Fitness Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `fitness.daily_stats` | Daily fitness metrics | `date`, `weight`, `currentMode`, `meals`, `meals_total` |
| `fitness.weekly_stats` | Weekly summaries | `weekStart`, `weekEnd`, `dailySteps`, `mode`, `startWeight`, `endWeight`, `avgWeightChange` |
| `fitness.meal_plans` | Meal plan archive | `date`, `sourceFile`, `week`, `targets`, `days`, `notes` |
| `fitness.food_macros` | Nutritional macro data | `id`, `name`, `unit`, `calories`, `protein_g`, `fat_g`, `carbs_g`, `fiber_g`, `source` |

### Meal Tracking Schema

```json
{
  "date": "YYYY-MM-DD",
  "weight": <number>,
  "currentMode": "re-entry|base-building|active-fat-loss|stability|build-recomp|final-fat-loss|maintenance|reset",
  "meals": {
    "breakfast": {
      "total_calories": <number>,
      "protein_g": <number>,
      "fat_g": <number>,
      "carbs_g": <number>,
      "status": "recorded|pending|skipped"
    },
    "lunch": <same structure>,
    "dinner": <same structure>
  },
  "meals_total": {
    "calories": <number>,
    "protein_g": <number>,
    "fat_g": <number>,
    "carbs_g": <number>
  }
}
```

### Shopping List Schema

**File:** `household/shopping/shopping-list-active.md`

**Rules:**
- DO NOT use raw ingredient measurements (e.g., "2 eggs")
- USE practical store items (e.g., "eggs (dozen packs)")
- Include batch quantities for weekly supply
- Add shopping tips and consumption notes

**Categories:**
- PRODUCE (fresh items)
- PROTEIN SOURCES (meat, fish, dairy, eggs)
- STAPLES (dry goods)
- PANTRY & OILS
- DAIRY & PROTEIN SUPPLEMENTS

**File-Based Tracking:** `household/shopping/dailyshopping.json`
- `date`, `items[]`, `total`, `store`

**Weekly Aggregation:** `household/shopping/weeklyshopping.json`
- `weekStart`, `weekEnd`, `shoppingDays[]`, `totalItems`, `totalSpent`

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `personal.finance.current_balance` | Current account balance | `date`, `balance`, `currency`, `accountType`, `lastUpdated` |
| `personal.finance.incoming` | All incoming payments (salary, Deel, transfers) | `date`, `amount`, `currency`, `from`, `description`, `source`, `account`, `reference` |
| `personal.finance.outgoing` | All outgoing transactions (purchases, subscriptions) | `date`, `amount`, `currency`, `to`, `category`, `description`, `account`, `reference` |
| `personal.finance.expenses` | Categorized expenses | `date`, `amount`, `currency`, `category`, `subcategory`, `merchant`, `description`, `paymentMethod` |
| `personal.finance.payments` | Payment confirmations | `date`, `amount`, `currency`, `from`, `description`, `account`, `reference` |
| `personal.finance.daily` | Daily financial snapshots | `date`, `startingBalance`, `endingBalance`, `totalIncoming`, `totalOutgoing`, `transactions[]` |
| `personal.finance.weekly` | Weekly summaries | `weekStart`, `weekEnd`, `startingBalance`, `endingBalance`, `totalIncoming`, `totalOutgoing`, `netChange`, `categoryBreakdown[]` |

### File-Based Finance Tracking (matching fitness structure)

| File | Purpose | Key Fields |
|------|---------|------------|
| `finance/dailystats.json` | Daily statistics and transactions | `date`, `startingBalance`, `endingBalance`, `transactions[]`, `totals`, `categoryBreakdown` |
| `finance/weeklystats.json` | Weekly summaries and aggregates | `weekStart`, `weekEnd`, `startingBalance`, `endingBalance`, `totals`, `categoryBreakdown[]`, `topCategories` |
| `finance/shopping-list-active.md` | Current active budget and pending transactions | `date`, `source`, `assumptions`, `categories`, `summary` |
| `finance/finance-summary.md` | Overview and documentation | `date`, `status`, `files`, `collections`, `currentBalance` |

### Hobbies Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `hobbies.global.daily` | Daily totals across all hobbies | `date`, `totalTimeHours`, `totalMoneySpent`, `hobbiesTracked[]`, `hobbyBreakdown`, `friendsMade`, `notes` |
| `hobbies.global.weekly` | Weekly summaries | `weekStart`, `weekEnd`, `totalTimeHours`, `totalMoneySpent`, `hobbiesTracked[]`, `weeklyBreakdown`, `friendsMade`, `notes` |
| `hobbies.global.hobbies_list` | Active hobbies registry | `hobbyName`, `startDate`, `status`, `category`, `budget`, `notes` |
| `hobbies.{hobby}.daily` | Daily metrics for individual hobby | `date`, `timeHours`, `moneySpent`, `friendsMade`, `activities`, `notes` |
| `hobbies.{hobby}.weekly` | Weekly summaries for individual hobby | `weekStart`, `weekEnd`, `totalTimeHours`, `totalMoneySpent`, `friendsMade`, `activities`, `notes` |
| `hobbies.{hobby}.info` | Hobby details and metadata | `hobbyName`, `category`, `started`, `budget`, `timeCommitment`, `equipment`, `resources`, `community`, `notes` |
| `hobbies.{hobby}.friends` | Friends network for hobby | `friendName`, `howMet`, `dateMet`, `notes`, `contactInfo` |

### Hobby Calendar Events

| Collection | Purpose | TTL | Key Fields |
|------------|---------|-----|------------|
| `hobby_events` | Found hobby events/workshops (calendar tracking) | 14 days after event_date | `hobby`, `event_name`, `event_date`, `event_time`, `price`, `location`, `address`, `website`, `image`, `instructor`, `capacity`, `registration`, `materials`, `source`, `status`, `rejection_reason`, `ttl_days`, `expires_at` |
| `hobby_pitches` | Hobby pitches (testing before full tracking) | none | `hobbyName`, `status`, `startDate`, `notes`, `nextSteps`, `conversionCriteria`, `convertedDate`, `convertedTo` |

### Shopping Collections

| Collection | Purpose | Entry method | Key Fields |
|------------|---------|------------|------------|
| `shopping.items` | Live shopping list — items to buy | Agent (shopping-list skill) | `name`, `quantity`, `unit`, `category`, `estimatedPrice`, `timeframe`, `priority`, `status`, `source`, `addedDate`, `boughtDate` |
| `shopping.active_list` | Meal-plan-generated shopping snapshots | meal-plan skill | `date`, `sourceMealPlan`, `assumptions`, `items[]`, `summary` |
| `shopping.daily` | Daily shopping trip records | manual | `date`, `items[]`, `total`, `store` |
| `shopping.weekly` | Weekly shopping summaries | manual | `weekStart`, `weekEnd`, `shoppingDays[]`, `totalItems`, `totalSpent` |

---

## 🏗️ Schema Patterns

### Daily Records Pattern
```json
{
  "date": "YYYY-MM-DD",           // Primary key, ISO format
  "items": [...]                  // Array of tracked items
}
```

### Weekly Summary Pattern
```json
{
  "weekStart": "YYYY-MM-DD",      // Week boundary
  "weekEnd": "YYYY-MM-DD",
  "aggregates": {...},            // Computed stats
  "topTags": [...]                // Most frequent categories
}
```

### Archive/Template Pattern
```json
{
  "isTemplate": true,             // Mark for exclusion from reports
  "isTest": true,
  "description": "Sample data for schema validation"
}
```

### Generated Lists Pattern
```json
{
  "source": "path/to/source.md",  // Reference original file
  "assumptions": {...},            // Context about assumptions made
  "categories": {...},             // Organized data structure
  "summary": {...}                 // Quick stats
}
```

---

## 📝 Naming Conventions

### Collections
- **Domain prefix:** `fitness.`, `shopping.`, `health.`, `goals.`, `finance.`
- **Granularity suffix:** `.daily`, `.weekly`, `.monthly`, `.active_list`, `.archive`
- **Examples:**
  - `fitness.daily_stats` - daily fitness metrics
  - `shopping.active_list` - current shopping list
  - `finance.current_balance` - current account balance
  - `finance.incoming` - all incoming payments

### Files
- **Date-based:** `meal-plan-05-10-26.md`, `dailystats.json`, `finance-daily-05-10-26.md`
- **Category-based:** `dailyshopping.json`, `weeklyshopping.json`, `finance-expenses.md`
- **Active state:** `shopping-list-active.md`, `finance-current.md` (no date in name)

---

## 🔑 Best Practices

### 1. **Template Markers**
Always mark sample/test data:
```javascript
{ isTemplate: true, isTest: true }
```
Query to exclude from reports:
```javascript
db.collection.find({ isTemplate: { $exists: false } })
```

### 2. **Source References**
Link data to original files:
```json
{ "sourceFile": "fitness/meal-plan-05-10-26.md" }
```

### 3. **Assumptions Tracking**
Document assumptions in generated data:
```json
{ "assumptions": { "kitchen": "empty" } }
```

### 4. **Date Format**
Use `YYYY-MM-DD` consistently for sorting and queries.

### 5. **Sparse Data**
OK to have empty days - only create records when data exists.

### 6. **Schema Validation**
Use JSON schema validators for critical collections.

---

## ➕ Adding New Collections

### Step 1: Define Schema
```javascript
db.createCollection('new.collection', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['date', 'keyField'],
      properties: {
        date: { bsonType: 'string' },
        keyField: { bsonType: 'string' }
      }
    }
  }
});
```

### Step 2: Insert Template Data
```javascript
db.new.collection.insertOne({
  date: '05-10-2026',
  keyField: 'value',
  isTemplate: true,
  isTest: true,
  description: 'Sample data for schema validation'
});
```

### Step 3: Document in This File
Add to the "Existing Collections" table above.

---

## 🔄 Data Flow Examples

### Meal Plan → Shopping List
```
fitness/meal-plan-05-10-26.md
        ↓ (parse ingredients)
shopping.active_list (05-10-2026)   ← snapshot, generated by meal-plan skill
        ↓ (future: also push to)
shopping.items (source: "meal-plan") ← live list, driven by shopping-list skill
        ↓ (future: estimatedPrice sum)
finance budget planning
```

### Live Shopping List (manual)
```
User: "add eggs, milk"
        ↓ (shopping-list skill)
shopping.items (status: "pending")
        ↓ (user: "got the eggs")
shopping.items (status: "bought")
        ↓ (future: match to finance.outgoing after purchase)
budget reconciliation
```

### Banking Transaction
```
Bancolombia notification → finance.incoming (insert)
Bancolombia notification → finance.outgoing (insert)
End of day → finance.daily (aggregate)
End of week → finance.weekly (aggregate)
```

### Shopping Trip
```
Actual shopping → shopping.daily (insert)
End of week → shopping.weekly (aggregate)
```

### Fitness Tracking
```
Daily workout → fitness.daily_stats (insert)
Weekly review → fitness.weekly_stats (aggregate)
```

---

## 📈 Aggregation Queries

### Total Spending by Tag
```javascript
db.shopping.daily.aggregate([
  { $unwind: "$items" },
  { $group: {
      _id: "$items.tags",
      total: { $sum: "$items.price" },
      count: { $sum: 1 }
    }
  },
  { $sort: { total: -1 } }
]);
```

### Calories by Day
```javascript
db.fitness.meal_plans.aggregate([
  { $unwind: "$days" },
  { $unwind: "$days.meals" },
  { $group: {
      _id: "$date",
      totalCalories: { $sum: "$days.totals.calories" },
      days: { $addToSet: "$days.dayNum" }
    }
  }
]);
```

### Total Income by Source
```javascript
db.finance.incoming.aggregate([
  { $group: {
      _id: "$source",
      total: { $sum: "$amount" },
      count: { $sum: 1 }
    }
  },
  { $sort: { total: -1 } }
]);
```

---

## 🚨 Important Notes

- **No authentication required** on this MongoDB instance
- **Connection:** `mongodb://localhost:27017/personal`
- **Backup strategy:** TBD (filesystem + MongoDB export)
- **Data retention:** Keep all historical data for reporting
- **Template exclusion:** Always flag test/template data

---

**Last Updated:** 05-10-2026  
**Next Review:** When new collection types are added
