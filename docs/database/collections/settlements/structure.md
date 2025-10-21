# settlements - Structure

## Overview
- **Collection**: `settlements`
- **Document Count**: 22,246
- **Average Document Size**: 326 bytes
- **Total Size**: 7,261,461 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68b58f39b9858c5f242a2b0a`, `68b58f39b9858c5f242a2b0b`, `68b58f39b9858c5f242a2b0c`

### `amount`

- **Type**: `float`
- **Sample Values**: `0.0`, `311.61`, `37.39`

### `amountdescription`

- **Type**: `str`
- **Sample Values**: `Principal`, `Product Tax`, `TCS-IGST`

### `amounttype`

- **Type**: `str`
- **Enum Values**: `ItemPrice`, `Other`

### `date`

- **Type**: `datetime`

### `depositdate`

- **Type**: `datetime`

### `enddate`

- **Type**: `datetime`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `orderid`

- **Type**: `str`
- **Sample Values**: `171-0436831-3386763`, `171-0436831-3386763`, `171-0436831-3386763`

### `orderitemid`

- **Type**: `str`
- **Sample Values**: `53015465466362`, `53015465466362`, `53015465466362`

### `settlementid`

- **Type**: `str`
- **Sample Values**: `25408414142`, `25408414142`, `25408414142`

### `sku`

- **Type**: `str`
- **Sample Values**: `Mad 3457 8x12 Px BLK`, `Mad 3457 8x12 Px BLK`, `Mad 3457 8x12 Px BLK`

### `startdate`

- **Type**: `datetime`

### `totalamount`

- **Type**: `float`
- **Sample Values**: `11115.91`

### `transactiontype`

- **Type**: `str`
- **Enum Values**: `Order`, `Other`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "68b58f39b9858c5f242a2b0a",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "marketplace": "6895638c452dc4315750e826",
  "settlementid": "25408414142",
  "amounttype": "Other",
  "transactiontype": "Other",
  "startdate": "2025-08-19T06:44:16",
  "enddate": "2025-08-26T06:44:15",
  "depositdate": "2025-08-28T06:44:15",
  "totalamount": 11115.91,
  "amount": 0.0
}
```

### Sample 2

```json
{
  "_id": "68b58f39b9858c5f242a2b0b",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "marketplace": "6895638c452dc4315750e826",
  "settlementid": "25408414142",
  "amounttype": "ItemPrice",
  "transactiontype": "Order",
  "orderid": "171-0436831-3386763",
  "orderitemid": "53015465466362",
  "sku": "Mad 3457 8x12 Px BLK",
  "date": "2025-08-20T00:00:00",
  "amountdescription": "Principal",
  "amount": 311.61
}
```

