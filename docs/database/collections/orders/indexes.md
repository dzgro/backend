# orders - Indexes

## Overview

Total Indexes: **2**

## _id_

### Details

- **Name**: `_id_`
- **Fields**: `_id` (ascending)
- **Type**: Single Field

### Purpose

Primary key index for document identification. Automatically created by MongoDB.

---

## marketplace_1_date_1

### Details

- **Name**: `marketplace_1_date_1`
- **Fields**: `marketplace` (ascending), `date` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Time-based queries and analytics. Compound index for efficient queries on marketplace, date.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.orders.find({marketplace: <marketplace_value>, date: <date_value>})
```

```javascript
db.orders.find({marketplace: <marketplace_value>})
```

---

## Index Usage Notes

### Compound Index Prefix Rule

For compound indexes, queries can use the index if they query on a prefix of the indexed fields. For example, an index on `(a, b, c)` can optimize queries on:
- `a`
- `a, b`
- `a, b, c`

But NOT on:
- `b`
- `c`
- `b, c`

### Index Selection

MongoDB automatically selects the most efficient index for each query. You can use `.explain()` to see which index was used:

```javascript
db.orders.find({...}).explain("executionStats")
```
