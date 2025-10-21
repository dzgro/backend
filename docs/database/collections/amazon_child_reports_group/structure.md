# amazon_child_reports_group - Structure

## Overview
- **Collection**: `amazon_child_reports_group`
- **Document Count**: 1
- **Average Document Size**: 285 bytes
- **Total Size**: 285 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68bfa71ad8a531d44e4b8fef`

### `completedat`

- **Type**: `datetime`

### `createdat`

- **Type**: `datetime`

### `dates`

- **Type**: `dict`

### `dates.enddate`

- **Type**: `datetime`

### `dates.label`

- **Type**: `str`
- **Sample Values**: `Aug 09, 2025 - Sep 08, 2025`

### `dates.startdate`

- **Type**: `datetime`

### `error`

- **Type**: `str`
- **Sample Values**: `expected ':'`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`

### `productsComplete`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `status`

- **Type**: `str`
- **Sample Values**: `COMPLETED`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "68bfa71ad8a531d44e4b8fef",
  "status": "COMPLETED",
  "dates": {
    "startdate": "2025-08-09T00:00:00",
    "enddate": "2025-09-08T00:00:00",
    "label": "Aug 09, 2025 - Sep 08, 2025"
  },
  "createdat": "2025-09-09T04:03:38.148000",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "marketplace": "6895638c452dc4315750e826",
  "productsComplete": true,
  "error": "expected ':'",
  "completedat": "2025-09-09T05:23:29.426000"
}
```

