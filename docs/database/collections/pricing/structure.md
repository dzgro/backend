# pricing - Structure

## Overview
- **Collection**: `pricing`
- **Document Count**: 2
- **Average Document Size**: 722 bytes
- **Total Size**: 1,444 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68e87dd5f4c92075038137a4`, `68e87eccf4c92075038137a5`

### `countryCode`

- **Type**: `str`
- **Sample Values**: `IN`, `US`

### `plans`

- **Type**: `list[]`

### `plans.durations`

- **Type**: `list[]`

### `plans.durations.duration`

- **Type**: `str`
- **Sample Values**: `Month`, `Month`

### `plans.durations.price`

- **Type**: `int`
- **Sample Values**: `199`, `5`

### `plans.durations.variable`

- **Type**: `int`
- **Sample Values**: `70`, `50`

### `plans.durations.variableType`

- **Type**: `str`
- **Sample Values**: `Orders`, `Orders`

### `plans.durations.variableUnit`

- **Type**: `int`
- **Sample Values**: `100`, `1`

### `plans.name`

- **Type**: `str`
- **Sample Values**: `Payment Reconciliation`, `Payment Reconciliation`


## Sample Documents

### Sample 1

```json
{
  "_id": "68e87dd5f4c92075038137a4",
  "countryCode": "IN",
  "plans": [
    {
      "name": "Payment Reconciliation",
      "durations": [
        {
          "duration": "Month",
          "price": 199,
          "variable": 70,
          "variableUnit": 100,
          "variableType": "Orders"
        },
        {
          "duration": "Year",
          "price": 1892,
          "variable": 70,
          "variableUnit": 100,
          "variableType": "Orders"
        }
      ]
    },
    {
      "name": "Analytics",
      "durations": [
        {
          "duration": "Month",
          "price": 948,
          "variable": 0.1,
          "variableType": "Revenue"
        },
        {
          "duration": "Year",
          "price": 9238,
          "variable": 0.1,
          "variableType": "Revenue"
        }
      ]
    },
    {
      "name": "Advertising",
      "durations": [
        {
          "duration": "Month",
          "price": 2384,
          "variable": 0.2,
          "variableType": "Revenue"
        },
        {
          "duration": "Year",
          "price": 21588,
          "variable": 0.2,
          "variableType": "Revenue"
        }
      ]
    }
  ]
}
```

### Sample 2

```json
{
  "_id": "68e87eccf4c92075038137a5",
  "countryCode": "US",
  "plans": [
    {
      "name": "Payment Reconciliation",
      "durations": [
        {
          "duration": "Month",
          "price": 5,
          "variable": 50,
          "variableUnit": 1,
          "variableType": "Orders"
        },
        {
          "duration": "Year",
          "price": 55,
          "variable": 50,
          "variableUnit": 1,
          "variableType": "Orders"
        }
      ]
    },
    {
      "name": "Analytics",
      "durations": [
        {
          "duration": "Month",
          "price": 19,
          "variable": 0.2,
          "variableType": "Revenue"
        },
        {
          "duration": "Year",
          "price": 198,
          "variable": 0.2,
          "variableType": "Revenue"
        }
      ]
    },
    {
      "name": "Advertising",
      "durations": [
        {
          "duration": "Month",
          "price": 49,
          "variable": 0.4,
          "variableType": "Revenue"
        },
        {
          "duration": "Year",
          "price": 534,
          "variable": 0.4,
          "variableType": "Revenue"
        }
      ]
    }
  ]
}
```

