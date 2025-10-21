# adv_rule_criteria_groups - Structure

## Overview
- **Collection**: `adv_rule_criteria_groups`
- **Document Count**: 3
- **Average Document Size**: 210 bytes
- **Total Size**: 631 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68490ab95002fb002e437d18`, `68490ab95002fb002e437d1a`, `68490ab95002fb002e437d19`

### `action`

- **Type**: `str`
- **Enum Values**: `Pause Target`, `Set Bid`, `Update Bid`

### `adproduct`

- **Type**: `str`
- **Sample Values**: `SPONSORED_PRODUCTS`, `SPONSORED_PRODUCTS`, `SPONSORED_PRODUCTS`

### `assettype`

- **Type**: `str`
- **Sample Values**: `Target`, `Target`, `Target`

### `subactions`

- **Type**: `list[]`

### `subactions.action`

- **Type**: `str`
- **Enum Values**: `Increase %`, `Set Exact Bid`

### `subactions.currency`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `subactions.label`

- **Type**: `str`
- **Enum Values**: `Bid Value`, `Set % Increase`

### `subactions.suffix`

- **Type**: `str`
- **Sample Values**: `%`


## Sample Documents

### Sample 1

```json
{
  "_id": "68490ab95002fb002e437d18",
  "action": "Pause Target",
  "adproduct": "SPONSORED_PRODUCTS",
  "assettype": "Target"
}
```

### Sample 2

```json
{
  "_id": "68490ab95002fb002e437d1a",
  "action": "Update Bid",
  "subactions": [
    {
      "action": "Increase %",
      "label": "Set % Increase",
      "suffix": "%"
    },
    {
      "action": "Decrease %",
      "label": "Set % Decrease",
      "suffix": "%"
    }
  ],
  "adproduct": "SPONSORED_PRODUCTS",
  "assettype": "Target"
}
```

