# users - Relationships

## Overview

This document describes how `users` relates to other collections in the database.

## References (Foreign Keys)

The `users` collection does not reference other collections.

## Referenced By

The `users` collection is referenced by:

### ← `spapi_accounts`

- **Via Field**: `spapi_accounts.uid`
- **Relationship**: One users ← Many spapi_accounts

### ← `gstin`

- **Via Field**: `gstin.uid`
- **Relationship**: One users ← Many gstin

### ← `advertising_accounts`

- **Via Field**: `advertising_accounts.uid`
- **Relationship**: One users ← Many advertising_accounts

### ← `marketplaces`

- **Via Field**: `marketplaces.uid`
- **Relationship**: One users ← Many marketplaces

## Data Flow

1. User creates an account → `users` document created
2. User adds SPAPI accounts → references via `spapi_accounts.uid`
3. User adds advertising accounts → references via `advertising_accounts.uid`
4. User creates marketplaces → references via `marketplaces.uid`

