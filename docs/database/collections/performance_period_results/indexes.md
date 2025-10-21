# performance_period_results - Indexes

## Overview

Total Indexes: **14**

## _id_

### Details

- **Name**: `_id_`
- **Fields**: `_id` (ascending)
- **Type**: Single Field

### Purpose

Primary key index for document identification. Automatically created by MongoDB.

---

## marketplace_1_queryid_1_collatetype_1

### Details

- **Name**: `marketplace_1_queryid_1_collatetype_1`
- **Fields**: `marketplace` (ascending), `queryid` (ascending), `collatetype` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Category/type-based filtering. Compound index for efficient queries on marketplace, queryid, collatetype.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>, collatetype: <collatetype_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>})
```

---

## marketplace_1_queryid_1_value_1

### Details

- **Name**: `marketplace_1_queryid_1_value_1`
- **Fields**: `marketplace` (ascending), `queryid` (ascending), `value` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Compound index for efficient queries on marketplace, queryid, value.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>, value: <value_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>})
```

---

## marketplace_1_queryid_1_parentsku_1

### Details

- **Name**: `marketplace_1_queryid_1_parentsku_1`
- **Fields**: `marketplace` (ascending), `queryid` (ascending), `parentsku` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Compound index for efficient queries on marketplace, queryid, parentsku.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>, parentsku: <parentsku_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>})
```

---

## marketplace_1_queryid_1_category_1

### Details

- **Name**: `marketplace_1_queryid_1_category_1`
- **Fields**: `marketplace` (ascending), `queryid` (ascending), `category` (ascending)
- **Type**: Compound

### Purpose

Filter and query by marketplace. Compound index for efficient queries on marketplace, queryid, category.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>, category: <category_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>})
```

```javascript
db.performance_period_results.find({marketplace: <marketplace_value>, queryid: <queryid_value>})
```

---

## data.netrevenue.curr_1

### Details

- **Name**: `data.netrevenue.curr_1`
- **Fields**: `data.netrevenue.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.netrevenue.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.netrevenue.curr: <value>})
```

```javascript
db.performance_period_results.find({data.netrevenue.curr: <value>}).sort({data.netrevenue.curr: 1})
```

---

## data.quantity.curr_1

### Details

- **Name**: `data.quantity.curr_1`
- **Fields**: `data.quantity.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.quantity.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.quantity.curr: <value>})
```

```javascript
db.performance_period_results.find({data.quantity.curr: <value>}).sort({data.quantity.curr: 1})
```

---

## data.averagesaleprice.curr_1

### Details

- **Name**: `data.averagesaleprice.curr_1`
- **Fields**: `data.averagesaleprice.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.averagesaleprice.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.averagesaleprice.curr: <value>})
```

```javascript
db.performance_period_results.find({data.averagesaleprice.curr: <value>}).sort({data.averagesaleprice.curr: 1})
```

---

## data.payoutpercentage.curr_1

### Details

- **Name**: `data.payoutpercentage.curr_1`
- **Fields**: `data.payoutpercentage.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.payoutpercentage.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.payoutpercentage.curr: <value>})
```

```javascript
db.performance_period_results.find({data.payoutpercentage.curr: <value>}).sort({data.payoutpercentage.curr: 1})
```

---

## data.returnpercentage.curr_1

### Details

- **Name**: `data.returnpercentage.curr_1`
- **Fields**: `data.returnpercentage.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.returnpercentage.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.returnpercentage.curr: <value>})
```

```javascript
db.performance_period_results.find({data.returnpercentage.curr: <value>}).sort({data.returnpercentage.curr: 1})
```

---

## data.cost.curr_1

### Details

- **Name**: `data.cost.curr_1`
- **Fields**: `data.cost.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.cost.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.cost.curr: <value>})
```

```javascript
db.performance_period_results.find({data.cost.curr: <value>}).sort({data.cost.curr: 1})
```

---

## data.roas.curr_1

### Details

- **Name**: `data.roas.curr_1`
- **Fields**: `data.roas.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.roas.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.roas.curr: <value>})
```

```javascript
db.performance_period_results.find({data.roas.curr: <value>}).sort({data.roas.curr: 1})
```

---

## data.tacos.curr_1

### Details

- **Name**: `data.tacos.curr_1`
- **Fields**: `data.tacos.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.tacos.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.tacos.curr: <value>})
```

```javascript
db.performance_period_results.find({data.tacos.curr: <value>}).sort({data.tacos.curr: 1})
```

---

## data.unitsessionpercentage.curr_1

### Details

- **Name**: `data.unitsessionpercentage.curr_1`
- **Fields**: `data.unitsessionpercentage.curr` (ascending)
- **Type**: Single Field

### Purpose

Optimize queries on data.unitsessionpercentage.curr.

### Example Queries

This index optimizes the following query patterns:

```javascript
db.performance_period_results.find({data.unitsessionpercentage.curr: <value>})
```

```javascript
db.performance_period_results.find({data.unitsessionpercentage.curr: <value>}).sort({data.unitsessionpercentage.curr: 1})
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
db.performance_period_results.find({...}).explain("executionStats")
```
