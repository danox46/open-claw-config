# Fitness Macros Database

## Overview
This collection stores nutritional macro data for the fitness meal planning project. It enables quick reference to food macros without needing to look up values online.

## Collection Structure

### `food-macros.json`
Primary collection with standard food items including:
- Eggs, egg whites
- Proteins (chicken, fish, beef, turkey, tuna)
- Carbs (rice, potato, oats, beans, lentils)
- Fats (olive oil, avocado, nuts)
- Dairy (Greek yogurt, cottage cheese)
- Produce (berries, apples, bananas, mixed vegetables)

### `food-macros-part2.json`
Additional items and placeholders:
- Arepa
- Vegetables (mixed)
- Local market cheese (placeholder - needs specific product data)

## Adding New Items

For each food item, record:
```json
{
  "id": <unique_id>,
  "name": "<food_name>",
  "unit": "<measurement_unit>",
  "calories": <number>,
  "protein_g": <number>,
  "fat_g": <number>,
  "carbs_g": <number>,
  "fiber_g": <number>,
  "source": "<source_url_or_label>",
  "notes": "<optional_notes>"
}
```

## Local Market Variations

For items with local variations (like cheese from nearby markets):
1. Add the specific product name
2. Record actual nutritional values from the product label
3. Use a distinct ID to avoid conflicts with generic values

## Loading into MongoDB

```javascript
// Load part 1
db.dropCollection("food_macros");
fs.readFile("/workspace/fitness/macros-db/food-macros.json", "utf8", (err, data) => {
  const macros = JSON.parse(data);
  macros.items.forEach(item => {
    db.food_macros.insertOne(item);
  });
});

// Load part 2
fs.readFile("/workspace/fitness/macros-db/food-macros-part2.json", "utf8", (err, data) => {
  const macros2 = JSON.parse(data);
  macros2.items.forEach(item => {
    db.food_macros.insertOne(item);
  });
});
```

## Query Examples

```javascript
// Get protein per 100g
db.food_macros.findOne({"name": "Chicken Breast", "unit": "100g cooked"});

// Get all carbs
db.food_macros.find({});

// Calculate macros for a meal (example)
// 160g chicken breast + 120g rice + 10g olive oil
db.food_macros.find({"name": {"$regex": "Chicken"}});
db.food_macros.find({"name": {"$regex": "Rice"}});
db.food_macros.find({"name": {"$regex": "Olive"}});
```

## Notes
- All weights are as specified in the meal plans
- Cooked weights apply to rice, potatoes, beans, lentils, meats
- Local market products should override generic values with specific product data
- Estimates are marked with source "estimated"
