# marketplace_plans - Structure

## Overview
- **Collection**: `marketplace_plans`
- **Document Count**: 3
- **Average Document Size**: 187 bytes
- **Total Size**: 563 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68f20ef824f295ff5d97021c`, `68f20f3b24f295ff5d97021d`, `68f211ec38610f009f4f7908`

### `createdat`

- **Type**: `datetime`

### `duration`

- **Type**: `str`
- **Sample Values**: `Year`, `Year`, `Year`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `orderid`

- **Type**: `str`
- **Sample Values**: `order_RUUmryXMGA66Ys`

### `plan`

- **Type**: `str`
- **Sample Values**: `Payment Reconciliation`, `Payment Reconciliation`, `Payment Reconciliation`

### `pricing`

- **Type**: `str`
- **Sample Values**: `68e8f4b1f4c92075038137aa`, `68e8f4b1f4c92075038137aa`, `68e8f4b1f4c92075038137aa`

### `status`

- **Type**: `str`
- **Enum Values**: `active`, `archived`


## Sample Documents

### Sample 1

```json
{
  "_id": "68f20ef824f295ff5d97021c",
  "marketplace": "6895638c452dc4315750e826",
  "status": "archived",
  "plan": "Payment Reconciliation",
  "pricing": "68e8f4b1f4c92075038137aa",
  "duration": "Year",
  "createdat": "2025-10-17T09:40:08.226000"
}
```

### Sample 2

```json
{
  "_id": "68f20f3b24f295ff5d97021d",
  "marketplace": "6895638c452dc4315750e826",
  "status": "archived",
  "plan": "Payment Reconciliation",
  "pricing": "68e8f4b1f4c92075038137aa",
  "duration": "Year",
  "createdat": "2025-10-17T09:41:15.855000"
}
```

