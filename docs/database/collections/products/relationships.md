# products - Relationships

## Overview

This document describes how `products` relates to other collections in the database.

## References (Foreign Keys)

The `products` collection references the following collections:

### → `products`

- **Via Field**: `sku`
- **Relationship**: `products.sku` references `products._id`
- **Type**: Many-to-One (Many products → One products)

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `products.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many products → One marketplaces)

### → `products`

- **Via Field**: `asin`
- **Relationship**: `products.asin` references `products._id`
- **Type**: Many-to-One (Many products → One products)

## Referenced By

The `products` collection is referenced by:

### ← `traffic`

- **Via Field**: `traffic.asin`
- **Relationship**: One products ← Many traffic

### ← `products`

- **Via Field**: `products.sku`
- **Relationship**: One products ← Many products

### ← `products`

- **Via Field**: `products.asin`
- **Relationship**: One products ← Many products

