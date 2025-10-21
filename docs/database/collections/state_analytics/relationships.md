# state_analytics - Relationships

## Overview

This document describes how `state_analytics` relates to other collections in the database.

## References (Foreign Keys)

The `state_analytics` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `state_analytics.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many state_analytics → One marketplaces)

## Referenced By

No other collections reference `state_analytics`.

