# performance_period_results - Relationships

## Overview

This document describes how `performance_period_results` relates to other collections in the database.

## References (Foreign Keys)

The `performance_period_results` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `performance_period_results.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many performance_period_results → One marketplaces)

## Referenced By

No other collections reference `performance_period_results`.

