# country_details - Relationships

## Overview

This document describes how `country_details` relates to other collections in the database.

## References (Foreign Keys)

The `country_details` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplaceId`
- **Relationship**: `country_details.marketplaceId` references `marketplaces._id`
- **Type**: Many-to-One (Many country_details → One marketplaces)

## Referenced By

No other collections reference `country_details`.

