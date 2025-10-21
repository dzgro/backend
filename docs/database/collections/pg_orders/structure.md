# pg_orders - Structure

## Overview
- **Collection**: `pg_orders`
- **Document Count**: 2
- **Average Document Size**: 400 bytes
- **Total Size**: 800 bytes

## Fields

### `_id`

- **Type**: `str | ObjectId`

### `amount`

- **Type**: `int | float`

### `amount_due`

- **Type**: `int`
- **Sample Values**: `254240`

### `amount_paid`

- **Type**: `int`
- **Sample Values**: `0`

### `attempts`

- **Type**: `int`
- **Sample Values**: `0`

### `category`

- **Type**: `str`
- **Sample Values**: `MARKETPLACE_ONBOARDING`, `MARKETPLACE_ONBOARDING`

### `created_at`

- **Type**: `int`
- **Sample Values**: `1758016868`

### `createdat`

- **Type**: `datetime`

### `currency`

- **Type**: `str`
- **Sample Values**: `INR`, `INR`

### `id`

- **Type**: `str`
- **Sample Values**: `order_RIEU3aVKQbBjJ5`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `68c7ccbd8c03f5f63334e824`

### `notes`

- **Type**: `dict`

### `notes.gstin`

- **Type**: `str`
- **Sample Values**: `68f1e6c437c5362eb4747c0e`

### `notes.marketplace`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826`

### `notes.plan`

- **Type**: `dict`

### `notes.plan.duration`

- **Type**: `str`
- **Sample Values**: `Year`

### `notes.plan.plan`

- **Type**: `str`
- **Sample Values**: `Payment Reconciliation`

### `notes.plan.pricing`

- **Type**: `str`
- **Sample Values**: `68e8f4b1f4c92075038137aa`

### `notes.uid`

- **Type**: `str`
- **Sample Values**: `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`

### `plantype`

- **Type**: `str`
- **Sample Values**: `Reports`

### `pricing`

- **Type**: `ObjectId`
- **Sample Values**: `689587b8fd3cb8068a0280d2`

### `receipt`

- **Type**: `str`
- **Sample Values**: `68c7ccbd8c03f5f63334e824`

### `status`

- **Type**: `str`
- **Sample Values**: `created`, `created`

### `uid`

- **Type**: `str`
- **Sample Values**: `31e3fdaa-80a1-7022-a469-84eb62ae3d05`, `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`


## Sample Documents

### Sample 1

```json
{
  "_id": "68c93571521cb3d76a3b9484",
  "receipt": "68c7ccbd8c03f5f63334e824",
  "amount": 254240,
  "currency": "INR",
  "id": "order_RIEU3aVKQbBjJ5",
  "amount_paid": 0,
  "amount_due": 254240,
  "status": "created",
  "attempts": 0,
  "created_at": 1758016868,
  "marketplace": "68c7ccbd8c03f5f63334e824",
  "plantype": "Reports",
  "pricing": "689587b8fd3cb8068a0280d2",
  "uid": "31e3fdaa-80a1-7022-a469-84eb62ae3d05",
  "category": "MARKETPLACE_ONBOARDING",
  "createdat": "2025-09-16T10:01:21.404000"
}
```

### Sample 2

```json
{
  "_id": "order_RUUmryXMGA66Ys",
  "amount": 14705.16,
  "currency": "INR",
  "status": "created",
  "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
  "notes": {
    "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
    "marketplace": "6895638c452dc4315750e826",
    "gstin": "68f1e6c437c5362eb4747c0e",
    "plan": {
      "plan": "Payment Reconciliation",
      "pricing": "68e8f4b1f4c92075038137aa",
      "duration": "Year"
    }
  },
  "category": "MARKETPLACE_ONBOARDING",
  "createdat": "2025-10-17T09:46:39.598000"
}
```

