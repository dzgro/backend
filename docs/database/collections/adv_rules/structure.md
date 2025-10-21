# adv_rules - Structure

## Overview
- **Collection**: `adv_rules`
- **Document Count**: 1
- **Average Document Size**: 2059 bytes
- **Total Size**: 2,059 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `6854fa52069a4be7a017602e`

### `adproduct`

- **Type**: `str`
- **Sample Values**: `SPONSORED_PRODUCTS`

### `assettype`

- **Type**: `str`
- **Sample Values**: `Target`

### `criterias`

- **Type**: `list[]`

### `criterias.conditions`

- **Type**: `list[]`

### `criterias.conditions.metric`

- **Type**: `str`
- **Sample Values**: `acos`

### `criterias.conditions.operator`

- **Type**: `str`
- **Sample Values**: `Greater Than`

### `criterias.conditions.val`

- **Type**: `int`
- **Sample Values**: `150`

### `criterias.result`

- **Type**: `dict`

### `criterias.result.action`

- **Type**: `str`
- **Sample Values**: `Pause Target`

### `description`

- **Type**: `str`
- **Sample Values**: `Adjust Bids for targets where Clicks>30 and orders>1 based on Acos.
Example: If Acos>150%, Pause the target. or if Acos<15, Increase Bid by 10%`

### `exclude`

- **Type**: `int`
- **Sample Values**: `0`

### `filters`

- **Type**: `list[]`

### `filters.metric`

- **Type**: `str`
- **Sample Values**: `clicks`

### `filters.operator`

- **Type**: `str`
- **Sample Values**: `Greater Than`

### `filters.val`

- **Type**: `int`
- **Sample Values**: `30`

### `lookback`

- **Type**: `int`
- **Sample Values**: `60`

### `name`

- **Type**: `str`
- **Sample Values**: `Acos Optimiser`

### `template`

- **Type**: `bool`
- **Enum Values**: `true`, `false`


## Sample Documents

### Sample 1

```json
{
  "_id": "6854fa52069a4be7a017602e",
  "name": "Acos Optimiser",
  "template": true,
  "description": "Adjust Bids for targets where Clicks>30 and orders>1 based on Acos.\nExample: If Acos>150%, Pause the target. or if Acos<15, Increase Bid by 10%",
  "assettype": "Target",
  "adproduct": "SPONSORED_PRODUCTS",
  "lookback": 60,
  "exclude": 0,
  "filters": [
    {
      "metric": "clicks",
      "operator": "Greater Than",
      "val": 30
    },
    {
      "metric": "orders",
      "operator": "Greater Than",
      "val": 1
    }
  ],
  "criterias": [
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 150
        }
      ],
      "result": {
        "action": "Pause Target"
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 100
        }
      ],
      "result": {
        "action": "Update Bid",
        "subaction": "Decrease %",
        "val": 30
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 70
        }
      ],
      "result": {
        "action": "Update Bid",
        "subaction": "Decrease %",
        "val": 25
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 50
        }
      ],
      "result": {
        "action": "Set Bid",
        "subaction": "CPC * Target Acos/Actual Acos",
        "val": 40
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 40
        }
      ],
      "result": {
        "action": "Set Bid",
        "subaction": "CPC * Target Acos/Actual Acos",
        "val": 30
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 30
        }
      ],
      "result": {
        "action": "Set Bid",
        "subaction": "CPC * Target Acos/Actual Acos",
        "val": 25
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 20
        }
      ],
      "result": {
        "action": "Set Bid",
        "subaction": "CPC * Target Acos/Actual Acos",
        "val": 15
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 15
        }
      ],
      "result": {
        "action": "Update Bid",
        "subaction": "Increase %",
        "val": 10
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 10
        }
      ],
      "result": {
        "action": "Update Bid",
        "subaction": "Increase %",
        "val": 20
      }
    },
    {
      "conditions": [
        {
          "metric": "acos",
          "operator": "Greater Than",
          "val": 1
        }
      ],
      "result": {
        "action": "Update Bid",
        "subaction": "Increase %",
        "val": 30
      }
    }
  ]
}
```

