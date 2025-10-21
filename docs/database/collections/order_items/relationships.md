# order_items - Relationships

## Overview

This document describes how `order_items` relates to other collections in the database.

## References (Foreign Keys)

The `order_items` collection references the following collections:

### → `orders`

- **Via Field**: `order`
- **Relationship**: `order_items.order` references `orders._id`
- **Type**: Many-to-One (Many order_items → One orders)

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `order_items.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many order_items → One marketplaces)

## Referenced By

No other collections reference `order_items`.

