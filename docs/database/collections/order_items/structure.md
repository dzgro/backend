# order_items - Structure

## Overview
- **Collection**: `order_items`
- **Document Count**: 2,524
- **Average Document Size**: 289 bytes
- **Total Size**: 731,554 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68b590ecb9858c5f242a7cd9`, `68b590ecb9858c5f242a7cda`, `68b590ecb9858c5f242a7cdb`

### `asin`

- **Type**: `str`
- **Sample Values**: `B07DYMLPVL`, `B07DYNTV1T`, `B07DWVGKPF`

### `date`

- **Type**: `datetime`

### `itemstatus`

- **Type**: `str`
- **Sample Values**: `Shipped`, `Shipped`, `Shipped`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `order`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_405-7715676-2945917`, `6895638c452dc4315750e826_405-7715676-2945917`, `6895638c452dc4315750e826_405-7715676-2945917`

### `price`

- **Type**: `float`
- **Sample Values**: `299.0`, `299.0`, `299.0`

### `quantity`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `revenue`

- **Type**: `float`
- **Sample Values**: `299.0`, `299.0`, `299.0`

### `sku`

- **Type**: `str`
- **Sample Values**: `Mad 1903`, `Mad R1 1954`, `Mad 1863`

### `tax`

- **Type**: `float`
- **Sample Values**: `32.04`, `32.04`, `32.04`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "68b590ecb9858c5f242a7cd9",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "marketplace": "6895638c452dc4315750e826",
  "order": "6895638c452dc4315750e826_405-7715676-2945917",
  "date": "2025-07-03T00:00:00",
  "itemstatus": "Shipped",
  "sku": "Mad 1903",
  "asin": "B07DYMLPVL",
  "quantity": 1,
  "revenue": 299.0,
  "price": 299.0,
  "tax": 32.04
}
```

### Sample 2

```json
{
  "_id": "68b590ecb9858c5f242a7cda",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "marketplace": "6895638c452dc4315750e826",
  "order": "6895638c452dc4315750e826_405-7715676-2945917",
  "date": "2025-07-03T00:00:00",
  "itemstatus": "Shipped",
  "sku": "Mad R1 1954",
  "asin": "B07DYNTV1T",
  "quantity": 1,
  "revenue": 299.0,
  "price": 299.0,
  "tax": 32.04
}
```

