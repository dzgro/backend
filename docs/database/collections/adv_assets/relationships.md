# adv_assets - Relationships

## Overview

This document describes how `adv_assets` relates to other collections in the database.

## References (Foreign Keys)

The `adv_assets` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `adv_assets.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many adv_assets → One marketplaces)

## Referenced By

No other collections reference `adv_assets`.

