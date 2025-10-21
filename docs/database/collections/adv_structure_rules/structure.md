# adv_structure_rules - Structure

## Overview
- **Collection**: `adv_structure_rules`
- **Document Count**: 5
- **Average Document Size**: 909 bytes
- **Total Size**: 4,546 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68c655a813ca9065c58c7568`, `68c655a813ca9065c58c7569`, `68c655a813ca9065c58c756a`

### `assettype`

- **Type**: `str`
- **Sample Values**: `Ad Group`, `Ad Group`, `Ad Group`

### `benefits`

- **Type**: `list[]`

### `colorScale`

- **Type**: `list[]`

### `colorScale.color`

- **Type**: `str`
- **Sample Values**: `#B71C1C`, `#B71C1C`, `#B71C1C`

### `colorScale.comment`

- **Type**: `str`
- **Sample Values**: `Very Poor`, `Very Poor`, `Very Poor`

### `colorScale.threshold`

- **Type**: `float`
- **Sample Values**: `19.9`, `19.9`, `19.9`

### `description`

- **Type**: `str`
- **Sample Values**: `This rule ensures that each ad group contains only a single product (ASIN or SKU). Keeping ad groups focused on one product allows for precise control over bids and budgets, minimizes keyword conflict, and produces more actionable performance insights.`, `This rule recommends using only one match type (Broad, Phrase, or Exact) within each ad group. It enables better targeting, less overlap, and easier performance tuning.`, `Limits keywords to a max of 10 per ad group. Helps avoid budget dilution and ensures better keyword focus for high-performance results.`

### `label`

- **Type**: `str`
- **Sample Values**: `One Product per Ad Group`, `Single Match Type Strategy`, `No Keyword Stuffing`

### `ruleId`

- **Type**: `str`
- **Sample Values**: `rule1`, `rule2`, `rule3`

### `weight`

- **Type**: `int`
- **Sample Values**: `9`, `8`, `6`


## Sample Documents

### Sample 1

```json
{
  "_id": "68c655a813ca9065c58c7568",
  "ruleId": "rule1",
  "label": "One Product per Ad Group",
  "weight": 9,
  "description": "This rule ensures that each ad group contains only a single product (ASIN or SKU). Keeping ad groups focused on one product allows for precise control over bids and budgets, minimizes keyword conflict, and produces more actionable performance insights.",
  "benefits": [
    "\ud83c\udfaf Better keyword-to-product relevance",
    "\ud83d\udcca Cleaner performance reporting",
    "\ud83d\udcb0 Smarter bid and budget allocation",
    "\ud83e\uddea Easier A/B testing and optimization"
  ],
  "colorScale": [
    {
      "threshold": 19.9,
      "color": "#B71C1C",
      "comment": "Very Poor"
    },
    {
      "threshold": 39.9,
      "color": "#E53935",
      "comment": "Poor"
    },
    {
      "threshold": 59.9,
      "color": "#FB8C00",
      "comment": "Average"
    },
    {
      "threshold": 79.9,
      "color": "#FBC02D",
      "comment": "Good"
    },
    {
      "threshold": 99.9,
      "color": "#FFA000",
      "comment": "Excellent"
    },
    {
      "threshold": 100,
      "color": "#2E7D32",
      "comment": "Perfect"
    }
  ],
  "assettype": "Ad Group"
}
```

### Sample 2

```json
{
  "_id": "68c655a813ca9065c58c7569",
  "ruleId": "rule2",
  "label": "Single Match Type Strategy",
  "weight": 8,
  "description": "This rule recommends using only one match type (Broad, Phrase, or Exact) within each ad group. It enables better targeting, less overlap, and easier performance tuning.",
  "benefits": [
    "\ud83d\udd0d Clearer intent targeting",
    "\ud83d\udcc8 More reliable performance data",
    "\ud83d\udeab Prevents cannibalization across match types",
    "\ud83e\udde9 Easier optimization by match type"
  ],
  "colorScale": [
    {
      "threshold": 19.9,
      "color": "#B71C1C",
      "comment": "Very Poor"
    },
    {
      "threshold": 39.9,
      "color": "#E53935",
      "comment": "Poor"
    },
    {
      "threshold": 59.9,
      "color": "#FB8C00",
      "comment": "Average"
    },
    {
      "threshold": 79.9,
      "color": "#FBC02D",
      "comment": "Good"
    },
    {
      "threshold": 99.9,
      "color": "#FFA000",
      "comment": "Excellent"
    },
    {
      "threshold": 100,
      "color": "#2E7D32",
      "comment": "Perfect"
    }
  ],
  "assettype": "Ad Group"
}
```

