# orders - Structure

## Overview
- **Collection**: `orders`
- **Document Count**: 2,424
- **Average Document Size**: 362 bytes
- **Total Size**: 878,815 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_402-4136876-4519559`, `6895638c452dc4315750e826_406-8378008-1520342`, `6895638c452dc4315750e826_403-7150154-5142761`

### `city`

- **Type**: `str`
- **Sample Values**: `Mumbai`, `Dehri`, `Gurugram`

### `code`

- **Type**: `str`
- **Sample Values**: `400053`, `821305`, `122011`

### `country`

- **Type**: `str`
- **Sample Values**: `IN`, `IN`, `IN`

### `date`

- **Type**: `datetime`

### `fulfillment`

- **Type**: `str`
- **Sample Values**: `Merchant`, `Merchant`, `Merchant`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `orderdate`

- **Type**: `datetime`

### `orderid`

- **Type**: `str`
- **Sample Values**: `402-4136876-4519559`, `406-8378008-1520342`, `403-7150154-5142761`

### `orderstatus`

- **Type**: `str`
- **Enum Values**: `Cancelled`, `Shipped - Delivered to Buyer`

### `state`

- **Type**: `str`
- **Enum Values**: `Bihar`, `Haryana`, `Maharashtra`

### `synctoken`

- **Type**: `ObjectId`
- **Sample Values**: `68b6bcccd3cbec34b1b2f306`, `68b6bcccd3cbec34b1b2f306`, `68b6bcccd3cbec34b1b2f306`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826_402-4136876-4519559",
  "city": "Mumbai",
  "code": "400053",
  "country": "IN",
  "date": "2025-08-01T00:00:00",
  "fulfillment": "Merchant",
  "marketplace": "6895638c452dc4315750e826",
  "orderdate": "2025-08-01T17:56:54",
  "orderid": "402-4136876-4519559",
  "orderstatus": "Shipped - Delivered to Buyer",
  "state": "Maharashtra",
  "synctoken": "68b6bcccd3cbec34b1b2f306",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

### Sample 2

```json
{
  "_id": "6895638c452dc4315750e826_406-8378008-1520342",
  "city": "Dehri",
  "code": "821305",
  "country": "IN",
  "date": "2025-08-01T00:00:00",
  "fulfillment": "Merchant",
  "marketplace": "6895638c452dc4315750e826",
  "orderdate": "2025-08-01T17:43:23",
  "orderid": "406-8378008-1520342",
  "orderstatus": "Shipped - Delivered to Buyer",
  "state": "Bihar",
  "synctoken": "68b6bcccd3cbec34b1b2f306",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

