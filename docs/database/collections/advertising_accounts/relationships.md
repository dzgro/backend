# advertising_accounts - Relationships

## Overview

This document describes how `advertising_accounts` relates to other collections in the database.

## References (Foreign Keys)

The `advertising_accounts` collection references the following collections:

### → `users`

- **Via Field**: `uid`
- **Relationship**: `advertising_accounts.uid` references `users._id`
- **Type**: Many-to-One (Many advertising_accounts → One users)

## Referenced By

No other collections reference `advertising_accounts`.

## Data Flow

1. User adds advertising account → `advertising_accounts` document created
2. Marketplace connects to advertising profile
3. Used to fetch advertising performance data

