# pg_orders - Relationships

## Overview

This document describes how `pg_orders` relates to other collections in the database.

## References (Foreign Keys)

The `pg_orders` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `pg_orders.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many pg_orders → One marketplaces)

## Referenced By

No other collections reference `pg_orders`.

