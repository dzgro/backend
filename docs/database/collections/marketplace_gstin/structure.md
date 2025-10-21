# marketplace_gstin - Structure

## Overview
- **Collection**: `marketplace_gstin`
- **Document Count**: 2
- **Average Document Size**: 104 bytes
- **Total Size**: 208 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68f203b6841f300995b56fd1`, `68f2436a1ee3018afcd94159`

### `createdat`

- **Type**: `datetime`

### `gstin`

- **Type**: `ObjectId`
- **Sample Values**: `68f1e6c437c5362eb4747c0e`, `68f1e6c437c5362eb4747c0e`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `status`

- **Type**: `str`
- **Enum Values**: `Active`, `active`


## Sample Documents

### Sample 1

```json
{
  "_id": "68f203b6841f300995b56fd1",
  "gstin": "68f1e6c437c5362eb4747c0e",
  "marketplace": "6895638c452dc4315750e826",
  "createdat": "2025-10-17T08:52:06.037000",
  "status": "active"
}
```

### Sample 2

```json
{
  "_id": "68f2436a1ee3018afcd94159",
  "gstin": "68f1e6c437c5362eb4747c0e",
  "marketplace": "6895638c452dc4315750e826",
  "status": "Active",
  "createdat": "2025-10-17T13:23:54.532000"
}
```

