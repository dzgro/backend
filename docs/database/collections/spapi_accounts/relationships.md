# spapi_accounts - Relationships

## Overview

This document describes how `spapi_accounts` relates to other collections in the database.

## References (Foreign Keys)

The `spapi_accounts` collection references the following collections:

### → `spapi_accounts`

- **Via Field**: `sellerid`
- **Relationship**: `spapi_accounts.sellerid` references `spapi_accounts._id`
- **Type**: Many-to-One (Many spapi_accounts → One spapi_accounts)

### → `users`

- **Via Field**: `uid`
- **Relationship**: `spapi_accounts.uid` references `users._id`
- **Type**: Many-to-One (Many spapi_accounts → One users)

## Referenced By

The `spapi_accounts` collection is referenced by:

### ← `spapi_accounts`

- **Via Field**: `spapi_accounts.sellerid`
- **Relationship**: One spapi_accounts ← Many spapi_accounts

## Data Flow

1. User adds SPAPI account → `spapi_accounts` document created
2. Marketplace uses SPAPI account for seller operations
3. Used to fetch orders, products, settlements data

