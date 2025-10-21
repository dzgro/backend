# gstin - Structure

## Overview
- **Collection**: `gstin`
- **Document Count**: 3
- **Average Document Size**: 307 bytes
- **Total Size**: 922 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68c3844f8735a6e4b8f00439`, `68f1e6c437c5362eb4747c0e`, `68f1e76a37c5362eb4747c0f`

### `addressline1`

- **Type**: `str`
- **Sample Values**: `4TH FLOOR, B4-401, Kanchanjunga Apartments`, `Kanchanjunga AParatments`, `Kanchanjunga AParatments`

### `addressline2`

- **Type**: `str`
- **Sample Values**: `Sector 8, Indira Gandhi Nagar, Jagatpura`, ``, ``

### `addressline3`

- **Type**: `str`
- **Sample Values**: ``, ``, ``

### `city`

- **Type**: `str`
- **Sample Values**: `Jaipur`, `Jaipur`, `Jaipur`

### `createdat`

- **Type**: `datetime`

### `gstin`

- **Type**: `str`
- **Sample Values**: `08DQAPS9574Q1ZN`, `08DQAPS9574Q1ZA`, `08DQAPS9574Q1ZN`

### `name`

- **Type**: `str`
- **Sample Values**: `DZGRO TECHNOLOGIES`, `DZGRO TECHNOLOGIES`, `DZGRO TECHNOLOGIES`

### `pincode`

- **Type**: `str`
- **Sample Values**: `302017`, `302017`, `302017`

### `state`

- **Type**: `str`
- **Sample Values**: `Rajasthan`, `Rajasthan`, `Rajasthan`

### `statecode`

- **Type**: `str`
- **Sample Values**: `08`, `08`

### `uid`

- **Type**: `str`
- **Sample Values**: `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce1`, `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`, `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`


## Sample Documents

### Sample 1

```json
{
  "_id": "68c3844f8735a6e4b8f00439",
  "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce1",
  "gstin": "08DQAPS9574Q1ZN",
  "name": "DZGRO TECHNOLOGIES",
  "addressline1": "4TH FLOOR, B4-401, Kanchanjunga Apartments",
  "addressline2": "Sector 8, Indira Gandhi Nagar, Jagatpura",
  "addressline3": "",
  "pincode": "302017",
  "city": "Jaipur",
  "state": "Rajasthan"
}
```

### Sample 2

```json
{
  "_id": "68f1e6c437c5362eb4747c0e",
  "state": "Rajasthan",
  "statecode": "08",
  "gstin": "08DQAPS9574Q1ZA",
  "name": "DZGRO TECHNOLOGIES",
  "addressline1": "Kanchanjunga AParatments",
  "addressline2": "",
  "addressline3": "",
  "pincode": "302017",
  "city": "Jaipur",
  "uid": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
  "createdat": "2025-10-17T06:48:36.485000"
}
```

