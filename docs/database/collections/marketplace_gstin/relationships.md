# marketplace_gstin - Relationships

## Overview

This document describes how `marketplace_gstin` relates to other collections in the database.

## References (Foreign Keys)

The `marketplace_gstin` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `marketplace_gstin.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many marketplace_gstin → One marketplaces)

## Referenced By

No other collections reference `marketplace_gstin`.

