# state_analytics - Structure

## Overview
- **Collection**: `state_analytics`
- **Document Count**: 8,691
- **Average Document Size**: 284 bytes
- **Total Size**: 2,469,444 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68df878deb3729c7db7d499b`, `68df878deb3729c7db7d499c`, `68df878deb3729c7db7d499d`

### `asin`

- **Type**: `str`
- **Sample Values**: `B07F122YQX`, `B07DYMLPVL`, `B07DWVGKPF`

### `category`

- **Type**: `str`
- **Sample Values**: `WALL_ART`, `WALL_ART`, `WALL_ART`

### `collatetype`

- **Type**: `str`
- **Sample Values**: `sku`, `sku`, `sku`

### `data`

- **Type**: `dict`

### `data.fbmcancelledorders`

- **Type**: `int`
- **Sample Values**: `2`, `2`, `2`

### `data.fbmfees`

- **Type**: `float`
- **Sample Values**: `-76.7`, `-76.7`, `-76.7`

### `data.fbmorders`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `data.fbmotherexpenses`

- **Type**: `float`
- **Sample Values**: `-1.25`, `-1.25`, `-1.25`

### `data.fbmquantity`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `data.fbmrevenue`

- **Type**: `float`
- **Sample Values**: `299.0`, `299.0`, `299.0`

### `data.fbmtax`

- **Type**: `float`
- **Sample Values**: `32.04`, `32.04`, `32.04`

### `date`

- **Type**: `datetime`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `parentsku`

- **Type**: `str`
- **Sample Values**: `Mad 1732-$P`, `Mad 1903-$P`, `Mad 1863-$P`

### `state`

- **Type**: `str`
- **Sample Values**: `Karnataka`, `Karnataka`, `Karnataka`

### `value`

- **Type**: `str`
- **Sample Values**: `Mad 1732`, `Mad 1903`, `Mad 1863`


## Sample Documents

### Sample 1

```json
{
  "_id": "68df878deb3729c7db7d499b",
  "asin": "B07F122YQX",
  "category": "WALL_ART",
  "collatetype": "sku",
  "data": {
    "fbmrevenue": 299.0,
    "fbmtax": 32.04,
    "fbmorders": 1,
    "fbmquantity": 1,
    "fbmfees": -76.7,
    "fbmotherexpenses": -1.25
  },
  "date": "2025-07-03T00:00:00",
  "marketplace": "6895638c452dc4315750e826",
  "parentsku": "Mad 1732-$P",
  "state": "Karnataka",
  "value": "Mad 1732"
}
```

### Sample 2

```json
{
  "_id": "68df878deb3729c7db7d499c",
  "asin": "B07DYMLPVL",
  "category": "WALL_ART",
  "collatetype": "sku",
  "data": {
    "fbmrevenue": 299.0,
    "fbmtax": 32.04,
    "fbmorders": 1,
    "fbmquantity": 1,
    "fbmfees": -76.7,
    "fbmotherexpenses": -1.25
  },
  "date": "2025-07-03T00:00:00",
  "marketplace": "6895638c452dc4315750e826",
  "parentsku": "Mad 1903-$P",
  "state": "Karnataka",
  "value": "Mad 1903"
}
```

