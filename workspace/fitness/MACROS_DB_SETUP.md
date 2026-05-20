# Fitness Macros Database - Setup Complete

## What Was Created

### 1. Macros Database (`/workspace/fitness/macros-db/`)

#### Files Created:
- **food-macros.json** - Primary collection (23 items)
  - Eggs, egg whites, chicken breast, white fish
  - Greek yogurt, whey protein, rice, potato, olive oil
  - Berries, avocado, oats, cottage cheese, tuna
  - Beans, turkey mince, lean beef, lentils, salmon
  - Sweet potato, nuts, apple, banana

- **food-macros-part2.json** - Secondary collection (5 items)
  - Arepa (small)
  - Vegetables (mixed)
  - Salad (large)
  - Cheese (placeholder - needs local product data)
  - Eggs (2 whole - duplicate entry for convenience)

- **README.md** - Documentation for the collection
- **load-macros.sh** - Script to load data into MongoDB

### 3. Data Sources
- USDA.gov for standard items
- Eat This Much for eggs
- FatSecret for egg whites
- Product labels for whey protein
- Estimated values for arepa, vegetables, and local cheese

## Items Requiring Manual Input

1. **Arepa** - Values vary by recipe (cornmeal, cheese, butter content)
2. **Vegetables** - Mix varies (lettuce, tomatoes, cucumbers, peppers)
3. **Local Cheese** - Needs specific brand/product data from local market

## Loading into MongoDB

```bash
cd /workspace/fitness/macros-db
./load-macros.sh
```

Or manually:
```javascript
// MongoDB shell
use(fitness);
db.dropCollection("food_macros");

// Load food-macros.json
db.insertMany(JSON.parse(fs.readFileSync('/workspace/fitness/macros-db/food-macros.json', 'utf8').items));

// Load food-macros-part2.json
db.insertMany(JSON.parse(fs.readFileSync('/workspace/fitness/macros-db/food-macros-part2.json', 'utf8').items));
```

## Query Examples

```javascript
// Get chicken breast macros
db.food_macros.findOne({"name": "Chicken Breast", "unit": "100g cooked"});

// Get all protein sources
db.food_macros.find({"name": {"$regex": "Chicken|Fish|Beef|Turkey|Tuna"}});

// Calculate macros for Day 1 Meal 2 (160g chicken + 120g rice + 10g olive oil)
db.food_macros.findOne({"name": "Chicken Breast", "unit": "100g cooked"}); // 165 cal, 31g protein, 3.6g fat
db.food_macros.findOne({"name": "Rice", "unit": "100g cooked"}); // 130 cal, 2.7g protein, 0.3g fat
db.food_macros.findOne({"name": "Olive Oil", "unit": "10g"}); // 119 cal, 0g protein, 13.5g fat
```

## Next Steps

1. Load data into MongoDB using `load-macros.sh`
2. Add specific local cheese product data
3. Fine-tune arepa and vegetable values based on actual portions
4. Create automation to calculate daily totals from meal plans

## Notes

- All weights match the meal plan specifications
- Cooked weights apply to rice, potatoes, beans, lentils, meats
- Local market products should override generic values
- Estimates are clearly marked in the source field
