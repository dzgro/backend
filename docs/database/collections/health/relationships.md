# health - Relationships

## Overview

This document describes how `health` relates to other collections in the database.

## References (Foreign Keys)

The `health` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `health.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many health → One marketplaces)

## Referenced By

No other collections reference `health`.

