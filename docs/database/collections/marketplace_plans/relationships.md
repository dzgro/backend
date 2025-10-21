# marketplace_plans - Relationships

## Overview

This document describes how `marketplace_plans` relates to other collections in the database.

## References (Foreign Keys)

The `marketplace_plans` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `marketplace_plans.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many marketplace_plans → One marketplaces)

## Referenced By

No other collections reference `marketplace_plans`.

