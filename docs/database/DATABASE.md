# Database Documentation

## Overview

**Database Name**: `dzgro-dev`
**Total Collections**: 40
**Database Type**: MongoDB Atlas

This database powers the Dzgro platform, managing users, marketplaces, Amazon SP-API integrations, advertising data, analytics, and reporting.

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Documents | 312,158 |
| Total Size | 176.90 MB |
| Collections | 40 |

## Database Architecture

### Core Entities

The database is organized around these core entities:

1. **User** - System users who own accounts and marketplaces
2. **SPAPI Account** - Amazon Seller Partner API credentials
3. **Advertising Account** - Amazon Advertising API credentials
4. **Marketplace** - Connection between user, SPAPI account, and advertising profile

### Data Flow

```
User
 ├─> SPAPI Accounts (multiple)
 ├─> Advertising Accounts (multiple)
 └─> Marketplaces (multiple)
      ├─> Products
      ├─> Orders & Order Items
      ├─> Settlements
      ├─> Analytics (Date, State, Performance)
      ├─> Advertising (Assets, Ads, Performance)
      ├─> Traffic Data
      └─> Reports
```

## Collections by Category

### User Management

#### [advertising_accounts](./collections/advertising_accounts/structure.md)

- **Documents**: 1
- [Structure](./collections/advertising_accounts/structure.md) | [Relationships](./collections/advertising_accounts/relationships.md) | [Indexes](./collections/advertising_accounts/indexes.md)

#### [marketplaces](./collections/marketplaces/structure.md)

- **Documents**: 1
- [Structure](./collections/marketplaces/structure.md) | [Relationships](./collections/marketplaces/relationships.md) | [Indexes](./collections/marketplaces/indexes.md)

#### [spapi_accounts](./collections/spapi_accounts/structure.md)

- **Documents**: 1
- [Structure](./collections/spapi_accounts/structure.md) | [Relationships](./collections/spapi_accounts/relationships.md) | [Indexes](./collections/spapi_accounts/indexes.md)

#### [users](./collections/users/structure.md)

- **Documents**: 2
- [Structure](./collections/users/structure.md) | [Relationships](./collections/users/relationships.md) | [Indexes](./collections/users/indexes.md)

### Products & Inventory

#### [health](./collections/health/structure.md)

- **Documents**: 1
- [Structure](./collections/health/structure.md) | [Relationships](./collections/health/relationships.md) | [Indexes](./collections/health/indexes.md)

#### [products](./collections/products/structure.md)

- **Documents**: 22,437
- [Structure](./collections/products/structure.md) | [Relationships](./collections/products/relationships.md) | [Indexes](./collections/products/indexes.md)

### Orders & Fulfillment

#### [order_items](./collections/order_items/structure.md)

- **Documents**: 2,524
- [Structure](./collections/order_items/structure.md) | [Relationships](./collections/order_items/relationships.md) | [Indexes](./collections/order_items/indexes.md)

#### [orders](./collections/orders/structure.md)

- **Documents**: 2,424
- [Structure](./collections/orders/structure.md) | [Relationships](./collections/orders/relationships.md) | [Indexes](./collections/orders/indexes.md)

#### [settlements](./collections/settlements/structure.md)

- **Documents**: 22,246
- [Structure](./collections/settlements/structure.md) | [Relationships](./collections/settlements/relationships.md) | [Indexes](./collections/settlements/indexes.md)

### Analytics & Reporting

#### [analytics_calculation](./collections/analytics_calculation/structure.md)

- **Documents**: 3
- [Structure](./collections/analytics_calculation/structure.md) | [Relationships](./collections/analytics_calculation/relationships.md) | [Indexes](./collections/analytics_calculation/indexes.md)

#### [date_analytics](./collections/date_analytics/structure.md)

- **Documents**: 81,420
- [Structure](./collections/date_analytics/structure.md) | [Relationships](./collections/date_analytics/relationships.md) | [Indexes](./collections/date_analytics/indexes.md)

#### [performance_period_results](./collections/performance_period_results/structure.md)

- **Documents**: 24,930
- [Structure](./collections/performance_period_results/structure.md) | [Relationships](./collections/performance_period_results/relationships.md) | [Indexes](./collections/performance_period_results/indexes.md)

#### [performance_periods](./collections/performance_periods/structure.md)

- **Documents**: 0
- [Structure](./collections/performance_periods/structure.md) | [Relationships](./collections/performance_periods/relationships.md) | [Indexes](./collections/performance_periods/indexes.md)

#### [state_analytics](./collections/state_analytics/structure.md)

- **Documents**: 8,691
- [Structure](./collections/state_analytics/structure.md) | [Relationships](./collections/state_analytics/relationships.md) | [Indexes](./collections/state_analytics/indexes.md)

#### [traffic](./collections/traffic/structure.md)

- **Documents**: 52,119
- [Structure](./collections/traffic/structure.md) | [Relationships](./collections/traffic/relationships.md) | [Indexes](./collections/traffic/indexes.md)

### Advertising

#### [adv_ads](./collections/adv_ads/structure.md)

- **Documents**: 244
- [Structure](./collections/adv_ads/structure.md) | [Relationships](./collections/adv_ads/relationships.md) | [Indexes](./collections/adv_ads/indexes.md)

#### [adv_assets](./collections/adv_assets/structure.md)

- **Documents**: 50,847
- [Structure](./collections/adv_assets/structure.md) | [Relationships](./collections/adv_assets/relationships.md) | [Indexes](./collections/adv_assets/indexes.md)

#### [adv_performance](./collections/adv_performance/structure.md)

- **Documents**: 43,933
- [Structure](./collections/adv_performance/structure.md) | [Relationships](./collections/adv_performance/relationships.md) | [Indexes](./collections/adv_performance/indexes.md)

#### [adv_rule_criteria_groups](./collections/adv_rule_criteria_groups/structure.md)

- **Documents**: 3
- [Structure](./collections/adv_rule_criteria_groups/structure.md) | [Relationships](./collections/adv_rule_criteria_groups/relationships.md) | [Indexes](./collections/adv_rule_criteria_groups/indexes.md)

#### [adv_rule_run_results](./collections/adv_rule_run_results/structure.md)

- **Documents**: 0
- [Structure](./collections/adv_rule_run_results/structure.md) | [Relationships](./collections/adv_rule_run_results/relationships.md) | [Indexes](./collections/adv_rule_run_results/indexes.md)

#### [adv_rule_runs](./collections/adv_rule_runs/structure.md)

- **Documents**: 0
- [Structure](./collections/adv_rule_runs/structure.md) | [Relationships](./collections/adv_rule_runs/relationships.md) | [Indexes](./collections/adv_rule_runs/indexes.md)

#### [adv_rules](./collections/adv_rules/structure.md)

- **Documents**: 1
- [Structure](./collections/adv_rules/structure.md) | [Relationships](./collections/adv_rules/relationships.md) | [Indexes](./collections/adv_rules/indexes.md)

#### [adv_structure_rules](./collections/adv_structure_rules/structure.md)

- **Documents**: 5
- [Structure](./collections/adv_structure_rules/structure.md) | [Relationships](./collections/adv_structure_rules/relationships.md) | [Indexes](./collections/adv_structure_rules/indexes.md)

### Reports

#### [amazon_child_reports](./collections/amazon_child_reports/structure.md)

- **Documents**: 0
- [Structure](./collections/amazon_child_reports/structure.md) | [Relationships](./collections/amazon_child_reports/relationships.md) | [Indexes](./collections/amazon_child_reports/indexes.md)

#### [amazon_child_reports_group](./collections/amazon_child_reports_group/structure.md)

- **Documents**: 1
- [Structure](./collections/amazon_child_reports_group/structure.md) | [Relationships](./collections/amazon_child_reports_group/relationships.md) | [Indexes](./collections/amazon_child_reports_group/indexes.md)

#### [dzgro_report_data](./collections/dzgro_report_data/structure.md)

- **Documents**: 261
- [Structure](./collections/dzgro_report_data/structure.md) | [Relationships](./collections/dzgro_report_data/relationships.md) | [Indexes](./collections/dzgro_report_data/indexes.md)

#### [dzgro_report_types](./collections/dzgro_report_types/structure.md)

- **Documents**: 7
- [Structure](./collections/dzgro_report_types/structure.md) | [Relationships](./collections/dzgro_report_types/relationships.md) | [Indexes](./collections/dzgro_report_types/indexes.md)

#### [dzgro_reports](./collections/dzgro_reports/structure.md)

- **Documents**: 2
- [Structure](./collections/dzgro_reports/structure.md) | [Relationships](./collections/dzgro_reports/relationships.md) | [Indexes](./collections/dzgro_reports/indexes.md)

### Payments & Billing

#### [credits](./collections/credits/structure.md)

- **Documents**: 0
- [Structure](./collections/credits/structure.md) | [Relationships](./collections/credits/relationships.md) | [Indexes](./collections/credits/indexes.md)

#### [gstin](./collections/gstin/structure.md)

- **Documents**: 3
- [Structure](./collections/gstin/structure.md) | [Relationships](./collections/gstin/relationships.md) | [Indexes](./collections/gstin/indexes.md)

#### [invoice_number](./collections/invoice_number/structure.md)

- **Documents**: 1
- [Structure](./collections/invoice_number/structure.md) | [Relationships](./collections/invoice_number/relationships.md) | [Indexes](./collections/invoice_number/indexes.md)

#### [marketplace_gstin](./collections/marketplace_gstin/structure.md)

- **Documents**: 2
- [Structure](./collections/marketplace_gstin/structure.md) | [Relationships](./collections/marketplace_gstin/relationships.md) | [Indexes](./collections/marketplace_gstin/indexes.md)

#### [marketplace_plans](./collections/marketplace_plans/structure.md)

- **Documents**: 3
- [Structure](./collections/marketplace_plans/structure.md) | [Relationships](./collections/marketplace_plans/relationships.md) | [Indexes](./collections/marketplace_plans/indexes.md)

#### [payments](./collections/payments/structure.md)

- **Documents**: 4
- [Structure](./collections/payments/structure.md) | [Relationships](./collections/payments/relationships.md) | [Indexes](./collections/payments/indexes.md)

#### [pg_orders](./collections/pg_orders/structure.md)

- **Documents**: 2
- [Structure](./collections/pg_orders/structure.md) | [Relationships](./collections/pg_orders/relationships.md) | [Indexes](./collections/pg_orders/indexes.md)

#### [pricing](./collections/pricing/structure.md)

- **Documents**: 2
- [Structure](./collections/pricing/structure.md) | [Relationships](./collections/pricing/relationships.md) | [Indexes](./collections/pricing/indexes.md)

### System & Configuration

#### [country_details](./collections/country_details/structure.md)

- **Documents**: 22
- [Structure](./collections/country_details/structure.md) | [Relationships](./collections/country_details/relationships.md) | [Indexes](./collections/country_details/indexes.md)

#### [defaults](./collections/defaults/structure.md)

- **Documents**: 2
- [Structure](./collections/defaults/structure.md) | [Relationships](./collections/defaults/relationships.md) | [Indexes](./collections/defaults/indexes.md)

#### [queue_messages](./collections/queue_messages/structure.md)

- **Documents**: 7
- [Structure](./collections/queue_messages/structure.md) | [Relationships](./collections/queue_messages/relationships.md) | [Indexes](./collections/queue_messages/indexes.md)

#### [state_names](./collections/state_names/structure.md)

- **Documents**: 6
- [Structure](./collections/state_names/structure.md) | [Relationships](./collections/state_names/relationships.md) | [Indexes](./collections/state_names/indexes.md)

## Key Relationships

### User → Accounts → Marketplace

```
users (uid)
  ↓
  ├─> spapi_accounts (uid) - User's Amazon Seller accounts
  ├─> advertising_accounts (uid) - User's Amazon Advertising accounts
  └─> marketplaces (uid) - User's marketplace configurations
       └─> marketplace (marketplaceId)
            ├─> products (marketplace)
            ├─> orders (marketplace)
            ├─> settlements (marketplace)
            ├─> date_analytics (marketplace)
            ├─> state_analytics (marketplace)
            ├─> adv_assets (marketplace)
            └─> ... (all operational data)
```

### Marketplace-Centric Model

Almost all operational data is tied to a `marketplace`:
- Products, Orders, Settlements
- Analytics (Date, State, Performance)
- Advertising data (Assets, Ads, Performance)
- Reports and Traffic

This allows users to have multiple marketplaces, each with isolated data.

## Index Strategy

### Common Index Patterns

1. **User Scoping**: `uid_1` - Filter by user
2. **Marketplace Scoping**: `marketplace_1` - Filter by marketplace
3. **Time-Series**: `marketplace_1_date_1` - Time-based queries
4. **Compound Filters**: `marketplace_1_field_1_date_1` - Complex queries

### Performance Optimizations

Most collections use compound indexes starting with `marketplace` to enable efficient marketplace-scoped queries, which are the most common access pattern.

## Collection Size Distribution

| Collection | Documents | Avg Size | Total Size |
|------------|-----------|----------|------------|
| date_analytics | 81,420 | 271 B | 22,128,917 B |
| traffic | 52,119 | 375 B | 19,554,473 B |
| adv_assets | 50,847 | 312 B | 15,888,309 B |
| adv_performance | 43,933 | 344 B | 15,135,925 B |
| performance_period_results | 24,930 | 3071 B | 76,563,642 B |
| products | 22,437 | 1098 B | 24,644,630 B |
| settlements | 22,246 | 326 B | 7,261,461 B |
| state_analytics | 8,691 | 284 B | 2,469,444 B |
| order_items | 2,524 | 289 B | 731,554 B |
| orders | 2,424 | 362 B | 878,815 B |

## Usage Guidelines

### For Claude Code

When working with this database:

1. **Always scope queries by marketplace** for operational data
2. **Use existing indexes** - check the indexes documentation before adding new ones
3. **Follow relationship patterns** - understand the data flow from user → marketplace → data
4. **Reference field types** from structure docs to ensure type safety
5. **Check enum values** when working with categorical fields

### Common Query Patterns

```javascript
// Get all products for a marketplace
db.products.find({ marketplace: ObjectId('...') })

// Get analytics for a date range
db.date_analytics.find({
  marketplace: ObjectId('...'),
  date: { $gte: ISODate('2024-01-01'), $lte: ISODate('2024-01-31') }
})

// Get user's marketplaces
db.marketplaces.find({ uid: 'user-cognito-id' })
```

## Documentation Structure

Each collection has three documentation files:

- **structure.md** - Field definitions, types, sample documents, enum values
- **relationships.md** - Foreign keys and references to/from other collections
- **indexes.md** - All indexes with purposes and query examples

Navigate using the links in the [Collections by Category](#collections-by-category) section above.

---

*Last Updated: Generated from live database on 2025-10-21*
