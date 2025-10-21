# performance_periods - Relationships

## Overview

This document describes how `performance_periods` relates to other collections in the database.

## References (Foreign Keys)

The `performance_periods` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `performance_periods.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many performance_periods → One marketplaces)

## Referenced By

No other collections reference `performance_periods`.

