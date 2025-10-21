# traffic - Relationships

## Overview

This document describes how `traffic` relates to other collections in the database.

## References (Foreign Keys)

The `traffic` collection references the following collections:

### → `products`

- **Via Field**: `asin`
- **Relationship**: `traffic.asin` references `products._id`
- **Type**: Many-to-One (Many traffic → One products)

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `traffic.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many traffic → One marketplaces)

## Referenced By

No other collections reference `traffic`.

