# advertising_accounts - Indexes

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

## uid_1

### Details

- **Name**: `uid_1`
- **Fields**: `uid` (ascending)
- **Type**: Single Field

### Purpose

User-specific queries.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.advertising_accounts.find({uid: <value>})
```

```javascript
db.advertising_accounts.find({uid: <value>}).sort({uid: 1})
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
db.advertising_accounts.find({...}).explain("executionStats")
```
