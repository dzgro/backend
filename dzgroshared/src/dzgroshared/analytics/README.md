# MongoDB Aggregation Pipeline Transformations for Analytics

This module provides MongoDB aggregation pipeline-based transformations to replace the Pythonic `transformData()` function calls in the analytics controller. Currently supports the `MONTH_METER_GROUPS` schema type transformation.

## Overview

The existing analytics system uses Python-based transformations after fetching raw data from MongoDB. This approach:

- Requires additional processing time
- Uses more memory
- Doesn't leverage MongoDB's native aggregation capabilities

The new pipeline-based approach transforms data directly in MongoDB, providing:

- Better performance through database-level processing
- Reduced memory usage
- Native MongoDB optimization
- Consistent formatting and calculations

## Current Implementation

### Supported Schema Types

- ✅ `MONTH_METER_GROUPS` (`'Month Meters'`) - Complete implementation
- ✅ `MONTH_BARS` (`'Month Bars'`) - Complete implementation
- ✅ `MONTH_DATA` (`'Month Data'`) - Complete implementation
- ✅ **Complete MonthDataResponse** - All components supported
- ✅ **Currency Symbol Support** - Automatic currency prefixing based on country code

### Files Structure

```
dzgroshared/src/dzgroshared/db/date_analytics/
├── AnalyticsPipelineBuilder.py          # Main pipeline builder class
├── IntegratedTransformations.py         # Integration helpers and drop-in replacements
└── pipelines/
    ├── MonthMeterGroupsTransform.py     # Specialized meter groups transformation
    └── CurrencyUtils.py                 # Currency symbol utilities and formatting
```

## Usage Examples

### 1. Drop-in Replacement for transformData()

Replace existing transformData calls:

```python
# Old approach - separate transformData calls
metergroups = controller.transformData('Month Meters', [month], req.collatetype, self.client.marketplace.countrycode)
bars = controller.transformData('Month Bars', [month], req.collatetype, self.client.marketplace.countrycode)[0]['data']
data = controller.transformData('Month Data', [month], req.collatetype, self.client.marketplace.countrycode)[0]['data']
```

With these new approaches:

```python
# New approach - individual replacements
from dzgroshared.db.date_analytics.IntegratedTransformations import (
    replace_transform_data_month_meters, replace_transform_data_month_bars, replace_transform_data_month_data
)

metergroups = replace_transform_data_month_meters([month], req.collatetype, self.client.marketplace.countrycode)
bars = replace_transform_data_month_bars([month], req.collatetype, self.client.marketplace.countrycode)
data = replace_transform_data_month_data([month], req.collatetype, self.client.marketplace.countrycode)

# Or - all at once
from dzgroshared.db.date_analytics.IntegratedTransformations import replace_all_transform_data_calls

transformed = replace_all_transform_data_calls([month], req.collatetype, self.client.marketplace.countrycode)
metergroups = transformed['meterGroups']
bars = transformed['bars']
data = transformed['data']
```

### 2. Pipeline-based Transformation (Recommended)

Add all transformation stages to your existing aggregation pipeline:

```python
from dzgroshared.db.date_analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder

# Your existing pipeline
pipeline = GetMonthsLiteData.pipeline(self.db.pp, self.client.marketplaceId, req)

# Add all transformations
builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
transformation_stages = builder.create_complete_month_data_response_pipeline('data')
complete_pipeline = pipeline + transformation_stages

# Execute - result will have all fields: 'meterGroups', 'bars', 'data'
data = await self.client.db.marketplaces.db.aggregate(complete_pipeline)
```

### 3. Complete Pipeline Replacement

For `getMonthLiteData` method, use the complete pipeline that handles everything:

```python
from dzgroshared.db.date_analytics.IntegratedTransformations import AnalyticsTransformationIntegrator

# Replace the entire pipeline with complete transformation
pipeline = AnalyticsTransformationIntegrator.get_complete_month_lite_data_pipeline(
    self.client.marketplaceId, req, self.client.marketplace.countrycode
)
data = await self.client.db.marketplaces.db.aggregate(pipeline)

# Use the transformed data directly - all components are ready!
result = [{
    "month": month['month'],
    "period": month['period'],
    "metergroups": month['meterGroups'],  # ✅ Already transformed!
    "bars": month['bars'],                # ✅ Already transformed!
    "data": month['data']                 # ✅ Already transformed!
} for month in data]
```

## Output Format

The transformations produce the complete `MonthDataResponse` structure:

### Complete MonthDataResponse

```json
{
  "month": "Dec 2024",
  "period": "01 Dec - 31 Dec",
  "data": {
    "label": "MONTH_DATA",
    "items": [
      {
        "label": "Net Revenue",
        "value": 250000.75,
        "valueString": "₹2.50 Lacs",
        "description": "Total value of orders after returns including tax"
      },
      {
        "label": "Total Units",
        "value": 1250,
        "valueString": "1.25 K"
      }
      // ... more data items
    ]
  },
  "bars": {
    "label": "MONTH_BARS",
    "items": [
      {
        "label": "TACOS",
        "value": 12.5,
        "valueString": "12.50%",
        "description": "Total Ad Cost as a percentage of Pre Tax Revenue"
      },
      {
        "label": "ACOS",
        "value": 25.8,
        "valueString": "25.80%"
      }
      // ... more bar items
    ]
  },
  "meterGroups": [
    // ... meter groups as shown below
  ]
}
```

### MeterGroups (list[AnalyticPeriodGroup])

```json
[
  {
    "label": "MONTH_SESSIONS_METER_GROUPS",
    "items": [
      {
        "label": "Browser",
        "value": 65.5,
        "valueString": "65.50%",
        "description": "Browser page views as a percentage of total page views"
      },
      {
        "label": "Mobile App",
        "value": 34.5,
        "valueString": "34.50%",
        "description": "Mobile app page views as a percentage of total page views"
      }
    ]
  },
  {
    "label": "MONTH_PAGE_VIEWS_METER_GROUPS",
    "items": [
      {
        "label": "Browser",
        "value": 60.2,
        "valueString": "60.20%",
        "description": "Browser sessions as a percentage of total sessions"
      },
      {
        "label": "Mobile App",
        "value": 39.8,
        "valueString": "39.80%",
        "description": "Mobile app sessions as a percentage of total sessions"
      }
    ]
  },
  {
    "label": "MONTH_CHANNEL_SALES_METER_GROUPS",
    "items": [
      {
        "label": "FBA/Flex++",
        "value": 75.3,
        "valueString": "75.30%",
        "description": "FBA Revenue as a percentage of total revenue"
      },
      {
        "label": "Merchant Fulfilled",
        "value": 24.7,
        "valueString": "24.70%",
        "description": "FBM Revenue as a percentage of total revenue"
      }
    ]
  },
  {
    "label": "MONTH_CHANNEL_PROCEEDS_METER_GROUPS",
    "items": [
      {
        "label": "FBA/Flex++",
        "value": 150000.5,
        "valueString": "₹1.50 Lacs",
        "description": "Net revenue from FBA orders after fees, returns, and adjustments"
      },
      {
        "label": "Merchant Fulfilled",
        "value": 45000.25,
        "valueString": "₹45.00 K",
        "description": "Net revenue from FBM orders after fees, returns, and adjustments"
      }
    ]
  }
]
```

## Currency Support

The system now includes comprehensive currency symbol support based on country codes:

### Supported Currencies

| Country        | Code | Symbol | Example Output |
| -------------- | ---- | ------ | -------------- |
| India          | IN   | ₹      | ₹2.50 Lacs     |
| United States  | US   | $      | $2.50 M        |
| United Kingdom | UK   | £      | £2.50 M        |
| Canada         | CA   | C$     | C$2.50 M       |
| Germany/EU     | DE   | €      | €2.50 M        |
| Japan          | JP   | ¥      | ¥2.50 M        |
| Australia      | AU   | A$     | A$2.50 M       |
| Singapore      | SG   | S$     | S$2.50 M       |
| UAE            | AE   | AED    | AED2.50 M      |
| Saudi Arabia   | SA   | SR     | SR2.50 M       |
| Turkey         | TR   | ₺      | ₺2.50 M        |
| Brazil         | BR   | R$     | R$2.50 M       |
| Mexico         | MX   | MX$    | MX$2.50 M      |
| _...and more_  |      |        |                |

### Automatic Currency Detection

Currency symbols are automatically applied to metrics marked with `isCurrency: true` in the `METRIC_DETAILS` model:

```python
# Revenue-related metrics get currency symbols
MetricDetail(metric=AnalyticsMetric.NET_REVENUE, ispercentage=False, isCurrency=True, label="Net Revenue")
MetricDetail(metric=AnalyticsMetric.AD_SPEND, ispercentage=False, isCurrency=True, label="Ad Spend")

# Non-currency metrics remain unchanged
MetricDetail(metric=AnalyticsMetric.QUANTITY, ispercentage=False, isCurrency=False, label="Total Units")
MetricDetail(metric=AnalyticsMetric.RETURN_PERCENTAGE, ispercentage=True, isCurrency=False, label="Return %")
```

### Currency-Enabled Metrics

The following metrics now include currency symbols:

- All revenue metrics (NET_REVENUE, FBA_REVENUE, FBM_REVENUE, etc.)
- All cost metrics (AD_SPEND, CPC, FEES, EXPENSES, etc.)
- All proceeds metrics (NET_PROCEEDS, FBA_NET_PROCEEDS, etc.)
- Average pricing metrics (AVERAGE_SALE_PRICE, PAYOUT_PER_UNIT, etc.)

## Number Formatting

The system automatically formats numbers based on:

### Country-specific Rules

- **India**: Uses Lacs (1,00,000) and Crores (1,00,00,000)
- **International**: Uses Millions (M) and Billions (B)

### Percentage Fields

- Formatted as "X.XX%" for metrics marked as percentages in `METRIC_DETAILS`

### Magnitude-based Formatting

- Values >= 1 Crore: "X.XX Cr" (India) or "X.XX B" (International)
- Values >= 1 Lac: "X.XX Lacs" (India) or "X.XX M" (International)
- Values >= 1K: "X.XX K"
- Others: "X.X" or exact value

## Performance Benefits

### Database-level Processing

- Calculations happen in MongoDB using native aggregation
- Reduces data transfer between database and application
- Leverages MongoDB's optimized aggregation engine

### Memory Efficiency

- No need to load raw data into Python for transformation
- Transformed results are smaller than raw analytics data
- Reduced garbage collection overhead

### Scalability

- Better performance with large datasets
- MongoDB can parallelize aggregation operations
- Reduced application server load

## Migration Strategy

### Phase 1: Complete MonthDataResponse (Current) ✅

- ✅ Implement pipeline transformation for all month schema types
- ✅ MONTH_METER_GROUPS - Complete implementation
- ✅ MONTH_BARS - Complete implementation
- ✅ MONTH_DATA - Complete implementation
- ✅ Provide drop-in replacement functions
- ✅ Maintain backward compatibility
- ✅ Complete pipeline for MonthDataResponse

### Phase 2: Extended Schema Types (Next)

- 🚧 Implement remaining schema types (Period, Comparison, State, etc.)
- 🚧 Extend to other controller methods
- 🚧 Support nested hierarchy transformations

### Phase 3: Complete Migration (Future)

- 🚧 Replace all transformData() calls across the application
- 🚧 Remove Python-based transformation code
- 🚧 Optimize pipelines further

## Testing

Test your transformations with sample data:

```python
from dzgroshared.db.date_analytics.IntegratedTransformations import replace_all_transform_data_calls
from dzgroshared.db.enums import CollateType, CountryCode

# Complete sample data for testing all transformations
test_data = [{
    "month": "Dec 2024",
    "data": {
        # For meter groups
        "browser_page_views_percentage": 65.5,
        "mobile_app_page_views_percentage": 34.5,
        "fba_revenue_percentage": 75.3,
        "fbm_net_proceeds": 150000.50,

        # For bars
        "tacos": 12.5,
        "acos": 25.8,
        "return_percentage": 3.2,
        "payout_percentage": 78.4,

        # For data
        "net_revenue": 250000.75,
        "quantity": 1250,
        "spend": 15000.25,
        "ad_sales": 58000.40,
        "roas": 3.87
    }
}]

# Transform all components at once with currency formatting
result = replace_all_transform_data_calls(test_data, CollateType.MARKETPLACE, CountryCode.INDIA)
print("MeterGroups:", len(result['meterGroups']))
print("Bars items:", len(result['bars']['items']))
print("Data items:", len(result['data']['items']))

# Example outputs with currency symbols:
# India (₹): "₹2.50 Lacs", "₹15.00 K"
# US ($): "$2.50 M", "$15.00 K"
# UK (£): "£2.50 M", "£15.00 K"

# Test individual transformations
from dzgroshared.db.date_analytics.IntegratedTransformations import (
    replace_transform_data_month_meters, replace_transform_data_month_bars, replace_transform_data_month_data
)

meters = replace_transform_data_month_meters(test_data, CollateType.MARKETPLACE, CountryCode.INDIA)
bars = replace_transform_data_month_bars(test_data, CollateType.MARKETPLACE, CountryCode.INDIA)
data = replace_transform_data_month_data(test_data, CollateType.MARKETPLACE, CountryCode.INDIA)
```

## Integration with Existing Code

The new transformations are designed to be minimally invasive:

1. **Keep existing imports** - Only add new imports where needed
2. **Maintain output format** - Results match existing `AnalyticPeriodGroup` structure
3. **Preserve error handling** - Includes proper null checking and fallbacks
4. **Support all country codes** - Handles formatting for different regions

## Troubleshooting

### Common Issues

1. **Missing fields in output**: Ensure your input data has the required metrics in the `data` field
2. **Incorrect formatting**: Check that `CountryCode` parameter matches your marketplace
3. **Pipeline errors**: Verify that derived metrics are calculated before transformation

### Debug Pipeline

To debug aggregation pipelines, use the pipeline printer:

```python
from dzgroshared.utils import mongo_pipeline_print
mongo_pipeline_print.copy_pipeline(your_pipeline)
```

## Future Enhancements

- Support for additional schema types (`MONTH_BARS`, `MONTH_DATA`, etc.)
- Caching of formatted strings for better performance
- Pipeline optimization based on usage patterns
- Integration with existing pipeline utilities
