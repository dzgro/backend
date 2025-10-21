import json
from pathlib import Path
from collections import defaultdict

# Load the database structure
with open('database_structure.json', 'r') as f:
    db_data = json.load(f)

base_dir = Path('../docs/database')

# Categorize collections
categories = {
    'User Management': ['users', 'spapi_accounts', 'advertising_accounts', 'marketplaces'],
    'Payments & Billing': ['payments', 'pricing', 'pg_orders', 'marketplace_plans', 'gstin', 'marketplace_gstin', 'invoice_number', 'credits'],
    'Products & Inventory': ['products', 'health'],
    'Orders & Fulfillment': ['orders', 'order_items', 'settlements'],
    'Analytics & Reporting': [
        'date_analytics', 'state_analytics', 'performance_periods',
        'performance_period_results', 'analytics_calculation', 'traffic'
    ],
    'Advertising': [
        'adv_assets', 'adv_ads', 'adv_performance', 'adv_rules',
        'adv_rule_runs', 'adv_rule_results', 'adv_rule_run_results',
        'adv_rule_criteria_groups', 'adv_structure_rules', 'adv_ad_group_mapping'
    ],
    'Reports': [
        'dzgro_reports', 'dzgro_report_types', 'dzgro_report_data',
        'amazon_child_reports', 'amazon_child_reports_group'
    ],
    'System & Configuration': [
        'defaults', 'country_details', 'state_names', 'queue_messages'
    ]
}

# Reverse mapping
collection_to_category = {}
for category, collections in categories.items():
    for coll in collections:
        collection_to_category[coll] = category

# Add any uncategorized collections
all_collections = list(db_data['collections'].keys())
for coll in all_collections:
    if coll not in collection_to_category:
        collection_to_category[coll] = 'Other'

md_content = """# Database Documentation

## Overview

**Database Name**: `dzgro-dev`
**Total Collections**: 40
**Database Type**: MongoDB Atlas

This database powers the Dzgro platform, managing users, marketplaces, Amazon SP-API integrations, advertising data, analytics, and reporting.

## Quick Stats

| Metric | Value |
|--------|-------|
"""

# Calculate total stats
total_docs = sum(c['stats']['count'] for c in db_data['collections'].values())
total_size = sum(c['stats']['size'] for c in db_data['collections'].values())

md_content += f"| Total Documents | {total_docs:,} |\n"
md_content += f"| Total Size | {total_size / (1024*1024):.2f} MB |\n"
md_content += f"| Collections | {len(all_collections)} |\n\n"

md_content += """## Database Architecture

### Core Entities

The database is organized around these core entities:

1. **User** - System users who own accounts and marketplaces
2. **SPAPI Account** - Amazon Seller Partner API credentials
3. **Advertising Account** - Amazon Advertising API credentials
4. **Marketplace** - Connection between user, SPAPI account, and advertising profile

### Data Flow

```
User
 ├─> SPAPI Accounts (multiple)
 ├─> Advertising Accounts (multiple)
 └─> Marketplaces (multiple)
      ├─> Products
      ├─> Orders & Order Items
      ├─> Settlements
      ├─> Analytics (Date, State, Performance)
      ├─> Advertising (Assets, Ads, Performance)
      ├─> Traffic Data
      └─> Reports
```

## Collections by Category

"""

# Sort categories to show User Management first
category_order = [
    'User Management',
    'Products & Inventory',
    'Orders & Fulfillment',
    'Analytics & Reporting',
    'Advertising',
    'Reports',
    'Payments & Billing',
    'System & Configuration',
    'Other'
]

for category in category_order:
    collections_in_cat = [c for c, cat in collection_to_category.items() if cat == category]
    if not collections_in_cat:
        continue

    md_content += f"### {category}\n\n"

    for coll_name in sorted(collections_in_cat):
        if coll_name not in db_data['collections']:
            continue

        coll_data = db_data['collections'][coll_name]
        doc_count = coll_data['stats']['count']

        md_content += f"#### [{coll_name}](./collections/{coll_name}/structure.md)\n\n"
        md_content += f"- **Documents**: {doc_count:,}\n"
        md_content += f"- [Structure](./collections/{coll_name}/structure.md) | "
        md_content += f"[Relationships](./collections/{coll_name}/relationships.md) | "
        md_content += f"[Indexes](./collections/{coll_name}/indexes.md)\n\n"

md_content += """## Key Relationships

### User → Accounts → Marketplace

```
users (uid)
  ↓
  ├─> spapi_accounts (uid) - User's Amazon Seller accounts
  ├─> advertising_accounts (uid) - User's Amazon Advertising accounts
  └─> marketplaces (uid) - User's marketplace configurations
       └─> marketplace (marketplaceId)
            ├─> products (marketplace)
            ├─> orders (marketplace)
            ├─> settlements (marketplace)
            ├─> date_analytics (marketplace)
            ├─> state_analytics (marketplace)
            ├─> adv_assets (marketplace)
            └─> ... (all operational data)
```

### Marketplace-Centric Model

Almost all operational data is tied to a `marketplace`:
- Products, Orders, Settlements
- Analytics (Date, State, Performance)
- Advertising data (Assets, Ads, Performance)
- Reports and Traffic

This allows users to have multiple marketplaces, each with isolated data.

## Index Strategy

### Common Index Patterns

1. **User Scoping**: `uid_1` - Filter by user
2. **Marketplace Scoping**: `marketplace_1` - Filter by marketplace
3. **Time-Series**: `marketplace_1_date_1` - Time-based queries
4. **Compound Filters**: `marketplace_1_field_1_date_1` - Complex queries

### Performance Optimizations

Most collections use compound indexes starting with `marketplace` to enable efficient marketplace-scoped queries, which are the most common access pattern.

## Collection Size Distribution

| Collection | Documents | Avg Size | Total Size |
|------------|-----------|----------|------------|
"""

# Sort by document count descending
sorted_collections = sorted(
    db_data['collections'].items(),
    key=lambda x: x[1]['stats']['count'],
    reverse=True
)[:10]  # Top 10

for coll_name, coll_data in sorted_collections:
    stats = coll_data['stats']
    md_content += f"| {coll_name} | {stats['count']:,} | {stats['avgObjSize']} B | {stats['size']:,} B |\n"

md_content += """
## Usage Guidelines

### For Claude Code

When working with this database:

1. **Always scope queries by marketplace** for operational data
2. **Use existing indexes** - check the indexes documentation before adding new ones
3. **Follow relationship patterns** - understand the data flow from user → marketplace → data
4. **Reference field types** from structure docs to ensure type safety
5. **Check enum values** when working with categorical fields

### Common Query Patterns

```javascript
// Get all products for a marketplace
db.products.find({ marketplace: ObjectId('...') })

// Get analytics for a date range
db.date_analytics.find({
  marketplace: ObjectId('...'),
  date: { $gte: ISODate('2024-01-01'), $lte: ISODate('2024-01-31') }
})

// Get user's marketplaces
db.marketplaces.find({ uid: 'user-cognito-id' })
```

## Documentation Structure

Each collection has three documentation files:

- **structure.md** - Field definitions, types, sample documents, enum values
- **relationships.md** - Foreign keys and references to/from other collections
- **indexes.md** - All indexes with purposes and query examples

Navigate using the links in the [Collections by Category](#collections-by-category) section above.

---

*Last Updated: Generated from live database on 2025-10-21*
"""

# Write the master DATABASE.md
output_file = base_dir / 'DATABASE.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"[OK] Created master documentation: {output_file}")
print(f"\nDatabase documentation complete!")
print(f"  - Master file: docs/database/DATABASE.md")
print(f"  - Collection docs: docs/database/collections/<collection_name>/")
print(f"  - Total files generated: {len(all_collections) * 3 + 1}")
