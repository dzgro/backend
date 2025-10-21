# date_analytics - Structure

## Overview
- **Collection**: `date_analytics`
- **Document Count**: 81,420
- **Average Document Size**: 271 bytes
- **Total Size**: 22,128,917 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68df8791eb3729c7db7d6b8f`, `68df8791eb3729c7db7d6b8e`, `68df8791eb3729c7db7d6b90`

### `asin`

- **Type**: `str`
- **Sample Values**: `B07DJC1VH2`, `B07D6PRY1T`, `B07DJCWXWK`

### `category`

- **Type**: `str`
- **Sample Values**: `WALL_ART`, `WALL_ART`, `WALL_ART`

### `collatetype`

- **Type**: `str`
- **Sample Values**: `sku`, `sku`, `sku`

### `data`

- **Type**: `dict`

### `data.clicks`

- **Type**: `int`
- **Sample Values**: `11`, `135`, `126`

### `data.cost`

- **Type**: `float`
- **Sample Values**: `30.48`, `399.33`, `533.67`

### `data.fbmcancelledorders`

- **Type**: `int`
- **Sample Values**: `2`, `1`

### `data.fbmfees`

- **Type**: `float`
- **Sample Values**: `-76.7`, `-76.7`, `-76.7`

### `data.fbmorders`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `data.fbmotherexpenses`

- **Type**: `float`
- **Sample Values**: `-7.5`, `-1.25`, `-7.5`

### `data.fbmquantity`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `data.fbmreturnquantity`

- **Type**: `float`
- **Sample Values**: `1.0`, `1.0`, `2.0`

### `data.fbmreturntax`

- **Type**: `float`
- **Sample Values**: `-32.04`, `-32.04`, `-134.25`

### `data.fbmreturnvalue`

- **Type**: `float`
- **Sample Values**: `-299.0`, `-299.0`, `-1253.0`

### `data.fbmrevenue`

- **Type**: `float`
- **Sample Values**: `299.0`, `299.0`, `299.0`

### `data.fbmtax`

- **Type**: `float`
- **Sample Values**: `32.04`, `32.04`, `32.04`

### `data.impressions`

- **Type**: `int`
- **Sample Values**: `1579`, `22749`, `16317`

### `data.orders`

- **Type**: `int`
- **Sample Values**: `1`, `4`, `5`

### `data.sales`

- **Type**: `float`
- **Sample Values**: `355.36`, `1793.75`, `2485.72`

### `data.units`

- **Type**: `int`
- **Sample Values**: `1`, `4`, `5`

### `date`

- **Type**: `datetime`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `parentsku`

- **Type**: `str`
- **Sample Values**: `Mad 1155-$P`, `Mad 1036-$P`, `Mad 1175-$P`

### `value`

- **Type**: `str`
- **Sample Values**: `Mad 1155`, `Mad 1036`, `Mad 1175`


## Sample Documents

### Sample 1

```json
{
  "_id": "68df8791eb3729c7db7d6b8f",
  "asin": "B07DJC1VH2",
  "category": "WALL_ART",
  "collatetype": "sku",
  "data": {
    "fbmfees": -76.7,
    "fbmorders": 1,
    "fbmotherexpenses": -7.5,
    "fbmquantity": 1,
    "fbmrevenue": 299.0,
    "fbmtax": 32.04
  },
  "date": "2025-07-03T00:00:00",
  "marketplace": "6895638c452dc4315750e826",
  "parentsku": "Mad 1155-$P",
  "value": "Mad 1155"
}
```

### Sample 2

```json
{
  "_id": "68df8791eb3729c7db7d6b8e",
  "asin": "B07D6PRY1T",
  "category": "WALL_ART",
  "collatetype": "sku",
  "data": {
    "fbmfees": -76.7,
    "fbmorders": 1,
    "fbmotherexpenses": -1.25,
    "fbmquantity": 1,
    "fbmrevenue": 299.0,
    "fbmtax": 32.04
  },
  "date": "2025-07-03T00:00:00",
  "marketplace": "6895638c452dc4315750e826",
  "parentsku": "Mad 1036-$P",
  "value": "Mad 1036"
}
```

