---
name: db-connection
description: Reference for all MongoDB operations — connection string, collection naming, and how to run queries. Apply this whenever a DB lookup or write is needed and no domain-specific skill covers it.
---

# Database Connection

**URI:** `mongodb://172.28.228.83:27017/`  
**Database:** `personal`  
**Full connection string:** `mongodb://172.28.228.83:27017/personal`

Collections use dot-notation names within the `personal` database (e.g. `finance.outgoing`, `shopping.items`). Check `db-map.md` to confirm the collection name before querying.

---

## How to run queries

**Do not create script files for ad-hoc lookups.** Run mongosh directly.

### Simple one-liner
```bash
mongosh 'mongodb://172.28.228.83:27017/personal' --eval "db['finance.outgoing'].find({category:'groceries'}).limit(5).toArray()"
```

### Multi-line query — use a heredoc
```bash
mongosh 'mongodb://172.28.228.83:27017/personal' --eval "
  db['shopping.items'].find(
    { status: 'pending' },
    { name: 1, category: 1, _id: 0 }
  ).sort({ category: 1 }).toArray()
"
```

### Complex logic — write to /tmp and run
```bash
cat > /tmp/q.js << 'EOF'
db['finance.outgoing'].aggregate([
  { \$match: { occurredAt: { \$gte: '2026-05-01' }, isTemplate: { \$exists: false } } },
  { \$group: { _id: '\$category', total: { \$sum: '\$amount.value' } } },
  { \$sort: { total: -1 } }
]).forEach(printjson)
EOF
mongosh 'mongodb://172.28.228.83:27017/personal' /tmp/q.js
```

Use /tmp for the script file — never create permanent `.js` files in the workspace for one-off queries.

---

## Collection syntax

Collections with dots in their name must use bracket notation:

```javascript
db['finance.outgoing']        // ✓
db['shopping.items']          // ✓
db['hobbies.global.hobbies_list']  // ✓

db.finance.outgoing           // ✗ — treated as nested objects, wrong
```

---

## When a domain skill exists, use it instead

Check `skills/` for a skill that covers the domain before running a raw query. Use mongosh directly only when no skill covers the lookup.

---

## Key facts

- Exclude template documents from all queries: `{ isTemplate: { $exists: false } }`
- Check `db-map.md` to confirm the collection name and schema before querying
