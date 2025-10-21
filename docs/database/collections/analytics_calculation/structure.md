# analytics_calculation - Structure

## Overview
- **Collection**: `analytics_calculation`
- **Document Count**: 3
- **Average Document Size**: 1800 bytes
- **Total Size**: 5,402 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `682b1ca43621d26cbcb46567`, `682b1ca43621d26cbcb46568`, `682b1ca43621d26cbcb46566`

### `index`

- **Type**: `int`
- **Sample Values**: `2`, `3`, `1`

### `items`

- **Type**: `list[]`

### `items.ispercent`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `items.label`

- **Type**: `str`
- **Sample Values**: `Impressions`, `Sessions`, `Revenue`

### `items.querygroup`

- **Type**: `str`
- **Sample Values**: `Ad Spend`, `Traffic`, `Sales`

### `items.value`

- **Type**: `str`
- **Sample Values**: `impressions`, `sessions`, `revenue`

### `label`

- **Type**: `str`
- **Sample Values**: `Advertisement`, `Traffic`, `Sales`

### `value`

- **Type**: `str`
- **Sample Values**: `ad`, `traffic`, `sales`


## Sample Documents

### Sample 1

```json
{
  "_id": "682b1ca43621d26cbcb46567",
  "value": "ad",
  "label": "Advertisement",
  "index": 2,
  "items": [
    {
      "value": "impressions",
      "ispercent": false,
      "label": "Impressions",
      "querygroup": "Ad Spend"
    },
    {
      "value": "clicks",
      "ispercent": false,
      "label": "Clicks",
      "querygroup": "Ad Spend"
    },
    {
      "value": "ctr",
      "ispercent": true,
      "label": "Click Through Rate (CTR)",
      "subkeys": [
        "clicks",
        "impressions"
      ],
      "operation": "divide",
      "querygroup": "Ad Spend"
    },
    {
      "value": "cost",
      "ispercent": false,
      "label": "Ad Spend",
      "querygroup": "Ad Spend"
    },
    {
      "value": "cpc",
      "ispercent": false,
      "label": "Cost Per Click (CPC)",
      "subkeys": [
        "cost",
        "clicks"
      ],
      "operation": "divide",
      "querygroup": "Ad Sales"
    },
    {
      "value": "orders",
      "label": "Ad Orders",
      "project": false
    },
    {
      "value": "units",
      "ispercent": false,
      "label": "Units",
      "project": false
    },
    {
      "value": "cvr",
      "ispercent": true,
      "label": "Conversion Ratio (CVR)",
      "subkeys": [
        "orders",
        "clicks"
      ],
      "operation": "divide",
      "querygroup": "Ad Sales"
    },
    {
      "value": "sales",
      "ispercent": false,
      "label": "Ad Sales",
      "querygroup": "Ad Sales"
    },
    {
      "value": "roas",
      "ispercent": false,
      "label": "RoAS",
      "subkeys": [
        "sales",
        "cost"
      ],
      "operation": "divide",
      "querygroup": "Ad Sales"
    },
    {
      "value": "acos",
      "ispercent": true,
      "label": "ACoS",
      "subkeys": [
        "cost",
        "sales"
      ],
      "operation": "divide",
      "reversegrowth": true
    }
  ]
}
```

### Sample 2

```json
{
  "_id": "682b1ca43621d26cbcb46568",
  "value": "traffic",
  "label": "Traffic",
  "index": 3,
  "items": [
    {
      "value": "sessions",
      "ispercent": false,
      "label": "Sessions",
      "querygroup": "Traffic"
    },
    {
      "value": "unitsessionpercent",
      "ispercent": true,
      "label": "Unit Session %",
      "operation": "divide",
      "subkeys": [
        "unitsessions",
        "sessions"
      ],
      "child": true,
      "querygroup": "Traffic"
    },
    {
      "value": "browsersessions",
      "ispercent": false,
      "label": "Browser Sessions",
      "child": true
    },
    {
      "value": "mobileappsessions",
      "ispercent": false,
      "label": "Mobile Sessions",
      "child": true
    },
    {
      "value": "pageviews",
      "ispercent": false,
      "label": "Page Views",
      "querygroup": "Traffic"
    },
    {
      "value": "buyboxpercent",
      "ispercent": true,
      "label": "Buy Box %",
      "operation": "divide",
      "subkeys": [
        "buyboxviews",
        "pageviews"
      ],
      "querygroup": "Traffic"
    },
    {
      "value": "browserpageviews",
      "ispercent": false,
      "label": "Browser Page Views",
      "child": true
    },
    {
      "value": "mobileapppageviews",
      "ispercent": false,
      "label": "Mobile Page Views",
      "child": true
    },
    {
      "value": "browserpageviewspercent",
      "ispercent": true,
      "label": "Browser Page Views %",
      "operation": "divide",
      "subkeys": [
        "browserpageviews",
        "pageviews"
      ]
    },
    {
      "value": "mobileapppageviewspercent",
      "ispercent": true,
      "label": "Mobile App Page Views %",
      "operation": "divide",
      "subkeys": [
        "mobileapppageviews",
        "pageviews"
      ]
    },
    {
      "value": "browsersessionspercent",
      "ispercent": true,
      "label": "Browser Sessions %",
      "operation": "divide",
      "subkeys": [
        "browsersessions",
        "sessions"
      ]
    },
    {
      "value": "mobileappsessionspercent",
      "ispercent": true,
      "label": "Mobile App Sessions %",
      "operation": "divide",
      "subkeys": [
        "mobileappsessions",
        "sessions"
      ]
    },
    {
      "value": "buyboxviews",
      "ispercent": false,
      "label": "Buy Box Views",
      "project": false
    },
    {
      "value": "unitsessions",
      "ispercent": false,
      "label": "Unit Sessions",
      "project": false
    }
  ]
}
```

