# date_analytics - Relationships

## Overview

This document describes how `date_analytics` relates to other collections in the database.

## References (Foreign Keys)

The `date_analytics` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `date_analytics.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many date_analytics → One marketplaces)

## Referenced By

No other collections reference `date_analytics`.

