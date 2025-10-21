# performance_periods - Indexes

## Overview

Total Indexes: **3**

## _id_

### Details

- **Name**: `_id_`
- **Fields**: `_id` (ascending)
- **Type**: Single Field

### Purpose

Primary key index for document identification. Automatically created by MongoDB.

---

## marketplace_1

### Details

- **Name**: `marketplace_1`
- **Fields**: `marketplace` (ascending)
- **Type**: Single Field

### Purpose

Filter and query by marketplace.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_periods.find({marketplace: <value>})
```

```javascript
db.performance_periods.find({marketplace: <value>}).sort({marketplace: 1})
```

---

## createdat_1

### Details

- **Name**: `createdat_1`
- **Fields**: `createdat` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on createdat.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_periods.find({createdat: <value>})
```

```javascript
db.performance_periods.find({createdat: <value>}).sort({createdat: 1})
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
db.performance_periods.find({...}).explain("executionStats")
```
