# gstin - Relationships

## Overview

This document describes how `gstin` relates to other collections in the database.

## References (Foreign Keys)

The `gstin` collection references the following collections:

### → `users`

- **Via Field**: `uid`
- **Relationship**: `gstin.uid` references `users._id`
- **Type**: Many-to-One (Many gstin → One users)

## Referenced By

No other collections reference `gstin`.

