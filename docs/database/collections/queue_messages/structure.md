# queue_messages - Structure

## Overview
- **Collection**: `queue_messages`
- **Document Count**: 7
- **Average Document Size**: 341 bytes
- **Total Size**: 2,388 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `123a712d-f8c7-4344-ad8d-64e3429893cb`, `834af3b6-6ceb-4e3a-ae69-2ef8b6d142fa`, `22d14871-185b-419e-829f-7b2429200f04`

### `body`

- **Type**: `dict`

### `body.index`

- **Type**: `str`
- **Sample Values**: `68e3953134ce7bfea93b5a98`, `68e39a9334ce7bfea93b5a99`, `68e39e83999a41947d0999f4`

### `body.marketplace`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `body.reporttype`

- **Type**: `str`
- **Sample Values**: `Order Payment Reconciliation`, `Order Payment Reconciliation`, `Order Payment Reconciliation`

### `body.step`

- **Type**: `str`
- **Sample Values**: `CREATE_REPORTS`

### `body.uid`

- **Type**: `str`
- **Sample Values**: `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`, `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`, `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`

### `completedat`

- **Type**: `datetime`

### `createdat`

- **Type**: `datetime`

### `error`

- **Type**: `str`
- **Sample Values**: `MongoDB URI options are key=value pairs.`, `MongoDB URI options are key=value pairs.`

### `model`

- **Type**: `str`
- **Sample Values**: `DzgroReportQM`, `DzgroReportQM`, `DzgroReportQM`

### `queue`

- **Type**: `str`
- **Sample Values**: `DzgroReports`, `DzgroReports`, `DzgroReports`

### `status`

- **Type**: `str`
- **Enum Values**: `COMPLETED`, `FAILED`


## Sample Documents

### Sample 1

```json
{
  "_id": "123a712d-f8c7-4344-ad8d-64e3429893cb",
  "model": "DzgroReportQM",
  "body": {
    "index": "68e3953134ce7bfea93b5a98",
    "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
    "marketplace": "6895638c452dc4315750e826",
    "reporttype": "Order Payment Reconciliation"
  },
  "status": "FAILED",
  "queue": "DzgroReports",
  "createdat": "2025-10-06T10:08:51.746000",
  "error": "MongoDB URI options are key=value pairs."
}
```

### Sample 2

```json
{
  "_id": "834af3b6-6ceb-4e3a-ae69-2ef8b6d142fa",
  "model": "DzgroReportQM",
  "body": {
    "index": "68e39a9334ce7bfea93b5a99",
    "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
    "marketplace": "6895638c452dc4315750e826",
    "reporttype": "Order Payment Reconciliation"
  },
  "status": "FAILED",
  "queue": "DzgroReports",
  "createdat": "2025-10-06T10:31:49.121000",
  "error": "MongoDB URI options are key=value pairs."
}
```

