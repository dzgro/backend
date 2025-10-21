# adv_performance - Relationships

## Overview

This document describes how `adv_performance` relates to other collections in the database.

## References (Foreign Keys)

The `adv_performance` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `adv_performance.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many adv_performance → One marketplaces)

## Referenced By

No other collections reference `adv_performance`.

