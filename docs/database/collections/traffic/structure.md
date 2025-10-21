# traffic - Structure

## Overview
- **Collection**: `traffic`
- **Document Count**: 52,119
- **Average Document Size**: 375 bytes
- **Total Size**: 19,554,473 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_B07CBV91MV_2025-07-02`, `6895638c452dc4315750e826_B07D6MZ5S2_2025-07-02`, `6895638c452dc4315750e826_B07D6NCQ3L_2025-07-02`

### `asin`

- **Type**: `str`
- **Sample Values**: `B07CBV91MV`, `B07D6MZ5S2`, `B07D6NCQ3L`

### `category`

- **Type**: `str`
- **Enum Values**: `HOME_FURNITURE_AND_DECOR`, `WALL_ART`

### `date`

- **Type**: `datetime`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `parentasin`

- **Type**: `str`
- **Sample Values**: `B0CGKHHCBN`, `B0CJ7CD9YX`, `B0CL157F5R`

### `parentsku`

- **Type**: `str`
- **Sample Values**: `Mad 1019-$P`, `Mad 1103-$P`, `Mad 1013-$P`

### `synctoken`

- **Type**: `ObjectId`
- **Sample Values**: `68b5461c5505d021e87b9de8`, `68b5461c5505d021e87b9de8`, `68b5461c5505d021e87b9de8`

### `traffic`

- **Type**: `dict`

### `traffic.browserpageviews`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `traffic.browsersessions`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `traffic.buyboxviews`

- **Type**: `int`
- **Sample Values**: `1`, `6`, `2`

### `traffic.mobileapppageviews`

- **Type**: `int`
- **Sample Values**: `1`, `5`, `2`

### `traffic.mobileappsessions`

- **Type**: `int`
- **Sample Values**: `1`, `4`, `1`

### `traffic.pageviews`

- **Type**: `int`
- **Sample Values**: `1`, `6`, `2`

### `traffic.sessions`

- **Type**: `int`
- **Sample Values**: `1`, `5`, `1`

### `traffic.unitsessions`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826_B07CBV91MV_2025-07-02",
  "asin": "B07CBV91MV",
  "date": "2025-07-02T00:00:00",
  "marketplace": "6895638c452dc4315750e826",
  "synctoken": "68b5461c5505d021e87b9de8",
  "traffic": {
    "pageviews": 1,
    "sessions": 1,
    "mobileapppageviews": 1,
    "mobileappsessions": 1,
    "buyboxviews": 1
  },
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

### Sample 2

```json
{
  "_id": "6895638c452dc4315750e826_B07D6MZ5S2_2025-07-02",
  "asin": "B07D6MZ5S2",
  "date": "2025-07-02T00:00:00",
  "marketplace": "6895638c452dc4315750e826",
  "synctoken": "68b5461c5505d021e87b9de8",
  "traffic": {
    "pageviews": 6,
    "sessions": 5,
    "browserpageviews": 1,
    "browsersessions": 1,
    "mobileapppageviews": 5,
    "mobileappsessions": 4,
    "buyboxviews": 6
  },
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

