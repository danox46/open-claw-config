#!/bin/bash

# Load fitness macros into MongoDB
# Usage: ./load-macros.sh

set -e

MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
DATABASE_NAME="${DATABASE_NAME:-personal}"

echo "Loading fitness macros into MongoDB..."
echo "URI: $MONGODB_URI"
echo "Database: $DATABASE_NAME"

# Load part 1
echo "Loading part 1..."
mongosh --quiet "$MONGODB_URI" --eval "
use('$DATABASE_NAME');
const fs = require('fs');
const macros = JSON.parse(fs.readFileSync('/home/danox/.openclaw/workspace/fitness/macros-db/food-macros.json', 'utf8'));
macros.items.forEach(item => {
  db.food_macros.insertOne(item);
});
console.log('Loaded ' + macros.items.length + ' items from part 1');
"

# Load part 2
echo "Loading part 2..."
mongosh --quiet "$MONGODB_URI" --eval "
use('$DATABASE_NAME');
const fs = require('fs');
const macros2 = JSON.parse(fs.readFileSync('/home/danox/.openclaw/workspace/fitness/macros-db/food-macros-part2.json', 'utf8'));
macros2.items.forEach(item => {
  db.food_macros.insertOne(item);
});
console.log('Loaded ' + macros2.items.length + ' items from part 2');
"

# Verify
echo "Verifying collection..."
mongosh --quiet "$MONGODB_URI" --eval "
use('$DATABASE_NAME');
const count = db.food_macros.countDocuments();
console.log('Total items in food_macros collection: ' + count);
console.log('Sample items:');
db.food_macros.find().limit(3).forEach(doc => console.log(JSON.stringify(doc)));
"

echo "Done!"
