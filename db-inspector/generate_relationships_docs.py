import json
import os
from pathlib import Path
from collections import defaultdict

# Load the database structure
with open('database_structure.json', 'r') as f:
    db_data = json.load(f)

base_dir = Path('../docs/database/collections')

# Build relationship maps
relationships = defaultdict(lambda: {'references': [], 'referenced_by': []})

def infer_target_collection(field_name):
    """Infer target collection from field name"""
    # Remove common suffixes
    field_lower = field_name.lower()

    # Direct matches
    if field_lower == 'marketplace' or field_lower == 'marketplaceid':
        return 'marketplaces'
    if field_lower == 'uid' or field_lower == 'userid':
        return 'users'
    if field_lower == 'orderid':
        return 'orders'
    if field_lower == 'order':
        return 'orders'
    if field_lower == 'productid':
        return 'products'
    if field_lower == 'sku':
        return 'products'
    if field_lower == 'asin':
        return 'products'
    if 'spapi' in field_lower and 'account' in field_lower:
        return 'spapi_accounts'
    if 'advertising' in field_lower or ('adv' in field_lower and 'account' in field_lower):
        return 'advertising_accounts'
    if 'profile' in field_lower:
        return 'advertising_accounts'  # advertising profiles
    if field_lower == 'seller':
        return 'spapi_accounts'
    if field_lower == 'ad':
        return 'advertising_accounts'
    if field_lower == 'sellerid':
        return 'spapi_accounts'
    if field_lower == 'profileid':
        return 'advertising_accounts'

    # Pattern matching for *id fields
    if field_name.endswith('id') or field_name.endswith('Id'):
        # Remove 'id' or 'Id' suffix
        if field_name.endswith('Id'):
            base_name = field_name[:-2]
        else:
            base_name = field_name[:-2]

        # Try plural form first
        possible_collection = base_name.lower() + 's'
        if possible_collection in db_data['collections']:
            return possible_collection

        # Try singular form
        possible_collection = base_name.lower()
        if possible_collection in db_data['collections']:
            return possible_collection

    # Check if field name matches a collection name
    if field_lower in db_data['collections']:
        return field_lower
    if field_lower + 's' in db_data['collections']:
        return field_lower + 's'

    return None

def extract_fields_from_indexes(collection_data):
    """Extract all fields mentioned in compound indexes"""
    fields = set()
    indexes = collection_data.get('indexes', [])

    for index in indexes:
        keys = index.get('keys', {})
        for field_name in keys.keys():
            # Skip _id
            if field_name != '_id':
                fields.add(field_name)

    return fields

# Analyze all collections to build relationship map
print("Analyzing relationships across collections...\n")
print("Looking at reference fields and compound indexes...\n")

for collection_name, collection_data in db_data['collections'].items():
    # Get reference fields
    reference_fields = set(collection_data.get('reference_fields', []))

    # Also get fields from compound indexes
    index_fields = extract_fields_from_indexes(collection_data)

    # Combine both sets
    all_potential_refs = reference_fields.union(index_fields)

    for field_name in all_potential_refs:
        # Skip _id field
        if field_name == '_id':
            continue

        # Infer target collection
        target_collection = infer_target_collection(field_name)

        if target_collection and target_collection in db_data['collections']:
            # Check if we already have this relationship
            existing = [r for r in relationships[collection_name]['references']
                       if r['field'] == field_name and r['target'] == target_collection]

            if not existing:
                # This collection references target_collection
                relationships[collection_name]['references'].append({
                    'field': field_name,
                    'target': target_collection
                })

                # Target collection is referenced by this collection
                relationships[target_collection]['referenced_by'].append({
                    'field': field_name,
                    'source': collection_name
                })

def generate_relationships_md(collection_name):
    """Generate relationships.md for a collection"""

    rel_data = relationships[collection_name]

    md_content = f"""# {collection_name} - Relationships

## Overview

This document describes how `{collection_name}` relates to other collections in the database.

"""

    # References (Foreign Keys - What this collection points to)
    if rel_data['references']:
        md_content += "## References (Foreign Keys)\n\n"
        md_content += f"The `{collection_name}` collection references the following collections:\n\n"

        for ref in rel_data['references']:
            md_content += f"### → `{ref['target']}`\n\n"
            md_content += f"- **Via Field**: `{ref['field']}`\n"
            md_content += f"- **Relationship**: `{collection_name}.{ref['field']}` references `{ref['target']}._id`\n"
            md_content += f"- **Type**: Many-to-One (Many {collection_name} → One {ref['target']})\n\n"
    else:
        md_content += "## References (Foreign Keys)\n\n"
        md_content += f"The `{collection_name}` collection does not reference other collections.\n\n"

    # Referenced By (What points to this collection)
    if rel_data['referenced_by']:
        md_content += "## Referenced By\n\n"
        md_content += f"The `{collection_name}` collection is referenced by:\n\n"

        for ref in rel_data['referenced_by']:
            md_content += f"### ← `{ref['source']}`\n\n"
            md_content += f"- **Via Field**: `{ref['source']}.{ref['field']}`\n"
            md_content += f"- **Relationship**: One {collection_name} ← Many {ref['source']}\n\n"
    else:
        md_content += "## Referenced By\n\n"
        md_content += f"No other collections reference `{collection_name}`.\n\n"

    # Add data flow section for key collections
    if collection_name == 'users':
        md_content += """## Data Flow

1. User creates an account → `users` document created
2. User adds SPAPI accounts → references via `spapi_accounts.uid`
3. User adds advertising accounts → references via `advertising_accounts.uid`
4. User creates marketplaces → references via `marketplaces.uid`

"""
    elif collection_name == 'marketplaces':
        md_content += """## Data Flow

1. User creates marketplace → `marketplaces` document created with `uid` reference
2. All operational data (orders, products, analytics) references this marketplace
3. Marketplace connects SPAPI account and advertising profile

"""
    elif collection_name == 'spapi_accounts':
        md_content += """## Data Flow

1. User adds SPAPI account → `spapi_accounts` document created
2. Marketplace uses SPAPI account for seller operations
3. Used to fetch orders, products, settlements data

"""
    elif collection_name == 'advertising_accounts':
        md_content += """## Data Flow

1. User adds advertising account → `advertising_accounts` document created
2. Marketplace connects to advertising profile
3. Used to fetch advertising performance data

"""

    return md_content

# Generate relationships.md for each collection
print("Generating relationship documentation for all collections...")
print(f"Total collections: {db_data['total_collections']}\n")

for collection_name in db_data['collections'].keys():
    print(f"Processing: {collection_name}")

    # Generate relationships.md
    relationships_md = generate_relationships_md(collection_name)

    # Write to file
    coll_dir = base_dir / collection_name
    relationships_file = coll_dir / 'relationships.md'
    with open(relationships_file, 'w', encoding='utf-8') as f:
        f.write(relationships_md)

    print(f"  [OK] Created {relationships_file}")

print(f"\n[OK] Successfully generated relationship documentation for {db_data['total_collections']} collections!")

# Print summary
print("\n" + "="*60)
print("RELATIONSHIP SUMMARY")
print("="*60)
for collection_name, rel_data in sorted(relationships.items()):
    if rel_data['references'] or rel_data['referenced_by']:
        print(f"\n{collection_name}:")
        if rel_data['references']:
            print(f"  References: {', '.join([r['target'] for r in rel_data['references']])}")
        if rel_data['referenced_by']:
            print(f"  Referenced by: {', '.join([r['source'] for r in rel_data['referenced_by']])}")
