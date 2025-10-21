import json
import os
from pathlib import Path
from collections import defaultdict

# Load the database structure
with open('database_structure.json', 'r') as f:
    db_data = json.load(f)

# Create base directory
base_dir = Path('../docs/database/collections')
base_dir.mkdir(parents=True, exist_ok=True)

def detect_enum_values(field_name, field_info, all_samples):
    """Detect if a field appears to be an enum based on sample values"""
    if not field_info['sample_values']:
        return None

    # Only detect enums for likely categorical fields
    categorical_keywords = [
        'status', 'type', 'state', 'role', 'category', 'kind',
        'mode', 'level', 'priority', 'stage', 'phase', 'environment',
        'method', 'action', 'event', 'collatetype', 'assettype',
        'amounttype', 'producttype', 'reporttype'
    ]

    # Skip fields that are clearly not enums
    skip_keywords = [
        'id', 'email', 'name', 'phone', 'url', 'uri', 'code',
        'number', 'description', 'text', 'note', 'message',
        'seller', 'buyer', 'customer', 'user', 'account'
    ]

    field_lower = field_name.lower()

    # Skip if field name suggests it's not an enum
    if any(skip in field_lower for skip in skip_keywords):
        return None

    # Check for boolean-like fields
    if 'bool' in field_info['type']:
        return ['true', 'false']

    # Only consider string fields with categorical names
    if 'str' in field_info['type']:
        is_categorical = any(keyword in field_lower for keyword in categorical_keywords)

        if is_categorical:
            unique_values = list(set(field_info['sample_values']))
            # Consider it enum if we have 2-9 unique string values
            if 2 <= len(unique_values) <= 9:
                return sorted(unique_values)

    return None

def format_field_type(types):
    """Format field types nicely"""
    if not types:
        return "unknown"
    if len(types) == 1:
        return types[0]
    return " | ".join(types)

def generate_structure_md(collection_name, collection_data):
    """Generate structure.md for a collection"""

    stats = collection_data['stats']
    fields = collection_data['fields']
    samples = collection_data.get('sample_documents', [])

    md_content = f"""# {collection_name} - Structure

## Overview
- **Collection**: `{collection_name}`
- **Document Count**: {stats['count']:,}
- **Average Document Size**: {stats['avgObjSize']} bytes
- **Total Size**: {stats['size']:,} bytes

## Fields

"""

    # Sort fields: _id first, then alphabetically
    sorted_fields = sorted(fields.items(), key=lambda x: ('0' if x[0] == '_id' else '1' + x[0]))

    for field_name, field_info in sorted_fields:
        field_type = format_field_type(field_info['type'])
        is_array = field_info.get('is_array', False)
        array_marker = '[]' if is_array else ''

        md_content += f"### `{field_name}`\n\n"
        md_content += f"- **Type**: `{field_type}{array_marker}`\n"

        # Check for enum values
        enum_values = detect_enum_values(field_name, field_info, samples)
        if enum_values:
            md_content += f"- **Enum Values**: {', '.join([f'`{v}`' for v in enum_values])}\n"

        # Add sample values if available
        if field_info['sample_values'] and not enum_values:
            sample_vals = field_info['sample_values'][:3]
            if field_type == 'ObjectId':
                md_content += f"- **Sample Values**: {', '.join([f'`{v}`' for v in sample_vals])}\n"
            elif field_type in ['str', 'int', 'float']:
                md_content += f"- **Sample Values**: {', '.join([f'`{v}`' for v in sample_vals])}\n"

        md_content += "\n"

    # Add sample documents section
    if samples:
        md_content += "\n## Sample Documents\n\n"
        for i, sample in enumerate(samples[:2], 1):
            md_content += f"### Sample {i}\n\n```json\n"
            md_content += json.dumps(sample, indent=2, default=str)
            md_content += "\n```\n\n"

    return md_content

# Generate structure.md for each collection
print("Generating structure documentation for all collections...")
print(f"Total collections: {db_data['total_collections']}\n")

for collection_name, collection_data in db_data['collections'].items():
    print(f"Processing: {collection_name}")

    # Create collection directory
    coll_dir = base_dir / collection_name
    coll_dir.mkdir(exist_ok=True)

    # Generate structure.md
    structure_md = generate_structure_md(collection_name, collection_data)

    # Write to file
    structure_file = coll_dir / 'structure.md'
    with open(structure_file, 'w', encoding='utf-8') as f:
        f.write(structure_md)

    print(f"  [OK] Created {structure_file}")

print(f"\n[OK] Successfully generated structure documentation for {db_data['total_collections']} collections!")
