# adv_performance - Structure

## Overview
- **Collection**: `adv_performance`
- **Document Count**: 43,933
- **Average Document Size**: 344 bytes
- **Total Size**: 15,135,925 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_117229195451880_Detail Page on-Amazon_2025-08-03`, `6895638c452dc4315750e826_117229195451880_Detail Page on-Amazon_2025-08-04`, `6895638c452dc4315750e826_117229195451880_Detail Page on-Amazon_2025-08-05`

### `ad`

- **Type**: `dict`

### `ad.clicks`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `ad.cost`

- **Type**: `float`
- **Sample Values**: `1.0`, `1.0`, `1.0`

### `ad.impressions`

- **Type**: `int`
- **Sample Values**: `44`, `37`, `29`

### `ad.orders`

- **Type**: `int`
- **Sample Values**: `1`, `1`

### `ad.sales`

- **Type**: `float`
- **Sample Values**: `266.96`, `266.96`

### `ad.units`

- **Type**: `int`
- **Sample Values**: `1`, `1`

### `assettype`

- **Type**: `str`
- **Sample Values**: `Campaign`, `Campaign`, `Campaign`

### `date`

- **Type**: `datetime`

### `id`

- **Type**: `str`
- **Sample Values**: `117229195451880`, `117229195451880`, `117229195451880`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `placementclassification`

- **Type**: `str`
- **Sample Values**: `Detail Page on-Amazon`, `Detail Page on-Amazon`, `Detail Page on-Amazon`

### `synctoken`

- **Type**: `ObjectId`
- **Sample Values**: `68b59733da7b8c7c5e21fedf`, `68b59733da7b8c7c5e21fedf`, `68b59733da7b8c7c5e21fedf`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826_117229195451880_Detail Page on-Amazon_2025-08-03",
  "ad": {
    "impressions": 44
  },
  "assettype": "Campaign",
  "date": "2025-08-03T00:00:00",
  "id": "117229195451880",
  "marketplace": "6895638c452dc4315750e826",
  "placementclassification": "Detail Page on-Amazon",
  "synctoken": "68b59733da7b8c7c5e21fedf",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

### Sample 2

```json
{
  "_id": "6895638c452dc4315750e826_117229195451880_Detail Page on-Amazon_2025-08-04",
  "ad": {
    "impressions": 37,
    "clicks": 1,
    "cost": 1.0
  },
  "assettype": "Campaign",
  "date": "2025-08-04T00:00:00",
  "id": "117229195451880",
  "marketplace": "6895638c452dc4315750e826",
  "placementclassification": "Detail Page on-Amazon",
  "synctoken": "68b59733da7b8c7c5e21fedf",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

