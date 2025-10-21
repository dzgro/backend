# payments - Structure

## Overview
- **Collection**: `payments`
- **Document Count**: 4
- **Average Document Size**: 161 bytes
- **Total Size**: 644 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `686dfd11c585374cf2464943`, `686dff79af4394da65f72bf0`, `686e02e71a259575ec567314`

### `amount`

- **Type**: `float`
- **Sample Values**: `8988.0`, `8988.0`, `8988.0`

### `invoice`

- **Type**: `int`
- **Sample Values**: `121`, `122`, `123`

### `paymentid`

- **Type**: `str`
- **Sample Values**: `pay_QqZZu1GuofubdS`, `pay_QqZZu1GuofubdS`, `pay_QqZZu1GuofubdS`

### `paymenttype`

- **Type**: `str`
- **Sample Values**: `subscription`, `subscription`, `subscription`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "686dfd11c585374cf2464943",
  "paymentid": "pay_QqZZu1GuofubdS",
  "invoice": 121,
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "paymenttype": "subscription",
  "amount": 8988.0
}
```

### Sample 2

```json
{
  "_id": "686dff79af4394da65f72bf0",
  "paymentid": "pay_QqZZu1GuofubdS",
  "invoice": 122,
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "paymenttype": "subscription",
  "amount": 8988.0
}
```

