# defaults - Structure

## Overview
- **Collection**: `defaults`
- **Document Count**: 2
- **Average Document Size**: 2281 bytes
- **Total Size**: 4,562 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `invoice_number`, `adv_structure_rules`

### `rules`

- **Type**: `list[]`

### `rules.assettype`

- **Type**: `str`
- **Sample Values**: `Ad Group`

### `rules.benefits`

- **Type**: `list[]`

### `rules.colorScale`

- **Type**: `list[]`

### `rules.colorScale.color`

- **Type**: `str`
- **Sample Values**: `#B71C1C`

### `rules.colorScale.comment`

- **Type**: `str`
- **Sample Values**: `Very Poor`

### `rules.colorScale.threshold`

- **Type**: `float`
- **Sample Values**: `19.9`

### `rules.description`

- **Type**: `str`
- **Sample Values**: `This rule ensures that each ad group contains only a single product (ASIN or SKU). Keeping ad groups focused on one product allows for precise control over bids and budgets, minimizes keyword conflict, and produces more actionable performance insights.`

### `rules.label`

- **Type**: `str`
- **Sample Values**: `One Product per Ad Group`

### `rules.ruleId`

- **Type**: `str`
- **Sample Values**: `rule1`

### `rules.weight`

- **Type**: `int`
- **Sample Values**: `9`

### `value`

- **Type**: `int`
- **Sample Values**: `124`


## Sample Documents

### Sample 1

```json
{
  "_id": "invoice_number",
  "value": 124
}
```

### Sample 2

```json
{
  "_id": "adv_structure_rules",
  "rules": [
    {
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
    },
    {
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
    },
    {
      "ruleId": "rule3",
      "label": "No Keyword Stuffing",
      "weight": 6,
      "description": "Limits keywords to a max of 10 per ad group. Helps avoid budget dilution and ensures better keyword focus for high-performance results.",
      "benefits": [
        "\ud83c\udfaf Focused budget on top terms",
        "\ud83d\udcca Easier keyword-level reporting",
        "\ud83d\ude80 Faster performance insights",
        "\ud83e\uddf9 Less clutter in ad group structure"
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
    },
    {
      "ruleId": "rule4",
      "label": "Clean Campaign Structure",
      "weight": 5,
      "description": "Ensures each campaign contains only one ad group. It allows better budget control and strategic scaling by isolating goals.",
      "benefits": [
        "\ud83d\udca1 Easier budgeting per strategy",
        "\ud83d\udcc9 Reduced noise in performance data",
        "\ud83e\uddfe Simpler reporting and diagnostics",
        "\ud83d\udcd0 Structured scale across campaigns"
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
      "assettype": "Campaign"
    },
    {
      "ruleId": "rule5",
      "label": "Organized in Portfolios",
      "weight": 2,
      "description": "Assigning campaigns to portfolios keeps things clean and enables reporting at a higher level. Portfolios act as folders for better team and strategy organization.",
      "benefits": [
        "\ud83d\uddc2\ufe0f Streamlined campaign organization",
        "\ud83d\udcc8 Simplified reporting at portfolio level",
        "\ud83d\udd0d Easier monitoring by brand or category",
        "\ud83d\udc65 Better team collaboration and ownership"
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
      "assettype": "Campaign"
    }
  ]
}
```

