# products - Indexes

## Overview

Total Indexes: **5**

## _id_

### Details

- **Name**: `_id_`
- **Fields**: `_id` (ascending)
- **Type**: Single Field

### Purpose

Primary key index for document identification. Automatically created by MongoDB.

---

## marketplace_1_sku_1

### Details

- **Name**: `marketplace_1_sku_1`
- **Fields**: `marketplace` (ascending), `sku` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Compound index for efficient queries on marketplace, sku.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.products.find({marketplace: <marketplace_value>, sku: <sku_value>})
```

```javascript
db.products.find({marketplace: <marketplace_value>})
```

---

## marketplace_1_asin_1

### Details

- **Name**: `marketplace_1_asin_1`
- **Fields**: `marketplace` (ascending), `asin` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Compound index for efficient queries on marketplace, asin.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.products.find({marketplace: <marketplace_value>, asin: <asin_value>})
```

```javascript
db.products.find({marketplace: <marketplace_value>})
```

---

## marketplace_1_producttype_1

### Details

- **Name**: `marketplace_1_producttype_1`
- **Fields**: `marketplace` (ascending), `producttype` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Category/type-based filtering. Compound index for efficient queries on marketplace, producttype.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.products.find({marketplace: <marketplace_value>, producttype: <producttype_value>})
```

```javascript
db.products.find({marketplace: <marketplace_value>})
```

---

## marketplace_1_parentsku_1

### Details

- **Name**: `marketplace_1_parentsku_1`
- **Fields**: `marketplace` (ascending), `parentsku` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Compound index for efficient queries on marketplace, parentsku.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.products.find({marketplace: <marketplace_value>, parentsku: <parentsku_value>})
```

```javascript
db.products.find({marketplace: <marketplace_value>})
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
db.products.find({...}).explain("executionStats")
```
