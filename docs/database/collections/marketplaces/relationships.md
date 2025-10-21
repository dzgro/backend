# marketplaces - Relationships

## Overview

This document describes how `marketplaces` relates to other collections in the database.

## References (Foreign Keys)

The `marketplaces` collection references the following collections:

### → `users`

- **Via Field**: `uid`
- **Relationship**: `marketplaces.uid` references `users._id`
- **Type**: Many-to-One (Many marketplaces → One users)

### → `marketplaces`

- **Via Field**: `marketplaceid`
- **Relationship**: `marketplaces.marketplaceid` references `marketplaces._id`
- **Type**: Many-to-One (Many marketplaces → One marketplaces)

## Referenced By

The `marketplaces` collection is referenced by:

### ← `state_analytics`

- **Via Field**: `state_analytics.marketplace`
- **Relationship**: One marketplaces ← Many state_analytics

### ← `traffic`

- **Via Field**: `traffic.marketplace`
- **Relationship**: One marketplaces ← Many traffic

### ← `performance_period_results`

- **Via Field**: `performance_period_results.marketplace`
- **Relationship**: One marketplaces ← Many performance_period_results

### ← `country_details`

- **Via Field**: `country_details.marketplaceId`
- **Relationship**: One marketplaces ← Many country_details

### ← `adv_performance`

- **Via Field**: `adv_performance.marketplace`
- **Relationship**: One marketplaces ← Many adv_performance

### ← `dzgro_reports`

- **Via Field**: `dzgro_reports.marketplace`
- **Relationship**: One marketplaces ← Many dzgro_reports

### ← `date_analytics`

- **Via Field**: `date_analytics.marketplace`
- **Relationship**: One marketplaces ← Many date_analytics

### ← `amazon_child_reports_group`

- **Via Field**: `amazon_child_reports_group.marketplace`
- **Relationship**: One marketplaces ← Many amazon_child_reports_group

### ← `marketplace_plans`

- **Via Field**: `marketplace_plans.marketplace`
- **Relationship**: One marketplaces ← Many marketplace_plans

### ← `pg_orders`

- **Via Field**: `pg_orders.marketplace`
- **Relationship**: One marketplaces ← Many pg_orders

### ← `settlements`

- **Via Field**: `settlements.marketplace`
- **Relationship**: One marketplaces ← Many settlements

### ← `products`

- **Via Field**: `products.marketplace`
- **Relationship**: One marketplaces ← Many products

### ← `marketplaces`

- **Via Field**: `marketplaces.marketplaceid`
- **Relationship**: One marketplaces ← Many marketplaces

### ← `marketplace_gstin`

- **Via Field**: `marketplace_gstin.marketplace`
- **Relationship**: One marketplaces ← Many marketplace_gstin

### ← `order_items`

- **Via Field**: `order_items.marketplace`
- **Relationship**: One marketplaces ← Many order_items

### ← `adv_assets`

- **Via Field**: `adv_assets.marketplace`
- **Relationship**: One marketplaces ← Many adv_assets

### ← `health`

- **Via Field**: `health.marketplace`
- **Relationship**: One marketplaces ← Many health

### ← `orders`

- **Via Field**: `orders.marketplace`
- **Relationship**: One marketplaces ← Many orders

### ← `performance_periods`

- **Via Field**: `performance_periods.marketplace`
- **Relationship**: One marketplaces ← Many performance_periods

## Data Flow

1. User creates marketplace → `marketplaces` document created with `uid` reference
2. All operational data (orders, products, analytics) references this marketplace
3. Marketplace connects SPAPI account and advertising profile

