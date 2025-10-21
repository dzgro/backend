# settlements - Relationships

## Overview

This document describes how `settlements` relates to other collections in the database.

## References (Foreign Keys)

The `settlements` collection references the following collections:

### → `orders`

- **Via Field**: `orderid`
- **Relationship**: `settlements.orderid` references `orders._id`
- **Type**: Many-to-One (Many settlements → One orders)

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `settlements.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many settlements → One marketplaces)

## Referenced By

No other collections reference `settlements`.

