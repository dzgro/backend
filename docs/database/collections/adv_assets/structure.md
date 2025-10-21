# adv_assets - Structure

## Overview
- **Collection**: `adv_assets`
- **Document Count**: 50,847
- **Average Document Size**: 312 bytes
- **Total Size**: 15,888,309 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_184746987536667`, `6895638c452dc4315750e826_154127457907712`, `6895638c452dc4315750e826_527373352890804`

### `adproduct`

- **Type**: `str`
- **Sample Values**: `SPONSORED_DISPLAY`, `SPONSORED_DISPLAY`, `SPONSORED_DISPLAY`

### `assettype`

- **Type**: `str`
- **Sample Values**: `Campaign`, `Campaign`, `Campaign`

### `budget`

- **Type**: `float`
- **Sample Values**: `300.0`, `100.0`, `1000.0`

### `id`

- **Type**: `str`
- **Sample Values**: `184746987536667`, `154127457907712`, `527373352890804`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `name`

- **Type**: `str`
- **Sample Values**: `Bolo Har Har-SD-PAGE_VIEWS2022-12-07T10:53`, `Retargeting`, `Photo Collage - SD - Video`

### `parent`

- **Type**: `str | NoneType`

### `state`

- **Type**: `str`
- **Enum Values**: `ARCHIVED`, `PAUSED`

### `synctoken`

- **Type**: `ObjectId`
- **Sample Values**: `68bfa71ad8a531d44e4b8fef`, `68bfa71ad8a531d44e4b8fef`, `68bfa71ad8a531d44e4b8fef`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826_184746987536667",
  "adproduct": "SPONSORED_DISPLAY",
  "assettype": "Campaign",
  "budget": 300.0,
  "id": "184746987536667",
  "marketplace": "6895638c452dc4315750e826",
  "name": "Bolo Har Har-SD-PAGE_VIEWS2022-12-07T10:53",
  "parent": null,
  "state": "ARCHIVED",
  "synctoken": "68bfa71ad8a531d44e4b8fef",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

### Sample 2

```json
{
  "_id": "6895638c452dc4315750e826_154127457907712",
  "adproduct": "SPONSORED_DISPLAY",
  "assettype": "Campaign",
  "budget": 100.0,
  "id": "154127457907712",
  "marketplace": "6895638c452dc4315750e826",
  "name": "Retargeting",
  "parent": null,
  "state": "PAUSED",
  "synctoken": "68bfa71ad8a531d44e4b8fef",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

