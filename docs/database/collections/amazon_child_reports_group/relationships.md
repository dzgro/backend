# amazon_child_reports_group - Relationships

## Overview

This document describes how `amazon_child_reports_group` relates to other collections in the database.

## References (Foreign Keys)

The `amazon_child_reports_group` collection references the following collections:

### → `marketplaces`

- **Via Field**: `marketplace`
- **Relationship**: `amazon_child_reports_group.marketplace` references `marketplaces._id`
- **Type**: Many-to-One (Many amazon_child_reports_group → One marketplaces)

## Referenced By

No other collections reference `amazon_child_reports_group`.

