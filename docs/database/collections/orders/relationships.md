# orders - Relationships

## Overview

This document describes how `orders` relates to other collections in the database.

## References (Foreign Keys)

The `orders` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `orders.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many orders → One marketplaces)

## Referenced By

The `orders` collection is referenced by:

### ← `settlements`

- **Via Field**: `settlements.orderid`
- **Relationship**: One orders ← Many settlements

### ← `order_items`

- **Via Field**: `order_items.order`
- **Relationship**: One orders ← Many order_items

