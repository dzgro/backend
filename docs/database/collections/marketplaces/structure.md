# marketplaces - Structure

## Overview
- **Collection**: `marketplaces`
- **Document Count**: 1
- **Average Document Size**: 265 bytes
- **Total Size**: 265 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`

### `ad`

- **Type**: `ObjectId`
- **Sample Values**: `68949cd83a48f7a095b9f527`

### `countrycode`

- **Type**: `str`
- **Sample Values**: `IN`

### `createdat`

- **Type**: `datetime`

### `marketplaceid`

- **Type**: `str`
- **Sample Values**: `A21TJRUUN4KGV`

### `profileid`

- **Type**: `Int64`

### `seller`

- **Type**: `ObjectId`
- **Sample Values**: `68949cbc3a48f7a095b9f526`

### `sellerid`

- **Type**: `str`
- **Sample Values**: `AUYWKTHB2JM7A`

### `status`

- **Type**: `str`
- **Sample Values**: `New`

### `storename`

- **Type**: `str`
- **Sample Values**: `Mad Master`

### `uid`

- **Type**: `str`
- **Sample Values**: `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826",
  "seller": "68949cbc3a48f7a095b9f526",
  "ad": "68949cd83a48f7a095b9f527",
  "sellerid": "AUYWKTHB2JM7A",
  "marketplaceid": "A21TJRUUN4KGV",
  "countrycode": "IN",
  "storename": "Mad Master",
  "profileid": 476214271739435,
  "status": "New",
  "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
  "createdat": "2025-09-09T04:03:38.148000"
}
```

