# dzgro_reports - Relationships

## Overview

This document describes how `dzgro_reports` relates to other collections in the database.

## References (Foreign Keys)

The `dzgro_reports` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `dzgro_reports.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many dzgro_reports → One marketplaces)

## Referenced By

No other collections reference `dzgro_reports`.

