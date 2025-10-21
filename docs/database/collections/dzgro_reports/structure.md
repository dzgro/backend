# dzgro_reports - Structure

## Overview
- **Collection**: `dzgro_reports`
- **Document Count**: 2
- **Average Document Size**: 450 bytes
- **Total Size**: 900 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68e3a11c999a41947d0999f6`, `68e52224dee8b9acabf455fe`

### `completedat`

- **Type**: `datetime`

### `count`

- **Type**: `int`
- **Sample Values**: `87`, `96`

### `createdat`

- **Type**: `datetime`

### `key`

- **Type**: `str`
- **Sample Values**: `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce/6895638c452dc4315750e826/ORDER_PAYMENT_RECON/68e3a11c999a41947d0999f6/Order Payment Reconciliation.xlsx`, `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce/6895638c452dc4315750e826/ORDER_PAYMENT_RECON/68e52224dee8b9acabf455fe/Order Payment Reconciliation.xlsx`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `messageid`

- **Type**: `str`
- **Sample Values**: `507f19fd-1a74-4b90-9b10-0e2759901cfe`, `3cbb1fa2-128f-4208-bc4c-e026fd6832fb`

### `orderPaymentRecon`

- **Type**: `dict`

### `orderPaymentRecon.dates`

- **Type**: `dict`

### `orderPaymentRecon.dates.endDate`

- **Type**: `datetime`

### `orderPaymentRecon.dates.startDate`

- **Type**: `datetime`

### `orderPaymentRecon.settlementRange`

- **Type**: `str`
- **Sample Values**: `NO_END_DATE`, `NO_END_DATE`

### `reporttype`

- **Type**: `str`
- **Sample Values**: `Order Payment Reconciliation`, `Order Payment Reconciliation`


## Sample Documents

### Sample 1

```json
{
  "_id": "68e3a11c999a41947d0999f6",
  "reporttype": "Order Payment Reconciliation",
  "orderPaymentRecon": {
    "dates": {
      "startDate": "2025-08-05T00:00:00",
      "endDate": "2025-08-06T00:00:00"
    },
    "settlementRange": "NO_END_DATE"
  },
  "createdat": "2025-10-06T10:59:40.416000",
  "marketplace": "6895638c452dc4315750e826",
  "messageid": "507f19fd-1a74-4b90-9b10-0e2759901cfe",
  "count": 87,
  "completedat": "2025-10-06T11:00:15.573000",
  "key": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce/6895638c452dc4315750e826/ORDER_PAYMENT_RECON/68e3a11c999a41947d0999f6/Order Payment Reconciliation.xlsx"
}
```

### Sample 2

```json
{
  "_id": "68e52224dee8b9acabf455fe",
  "reporttype": "Order Payment Reconciliation",
  "orderPaymentRecon": {
    "dates": {
      "startDate": "2025-09-02T00:00:00",
      "endDate": "2025-09-04T00:00:00"
    },
    "settlementRange": "NO_END_DATE"
  },
  "createdat": "2025-10-07T14:22:28.914000",
  "marketplace": "6895638c452dc4315750e826",
  "messageid": "3cbb1fa2-128f-4208-bc4c-e026fd6832fb",
  "count": 96,
  "completedat": "2025-10-07T14:23:15.256000",
  "key": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce/6895638c452dc4315750e826/ORDER_PAYMENT_RECON/68e52224dee8b9acabf455fe/Order Payment Reconciliation.xlsx"
}
```

