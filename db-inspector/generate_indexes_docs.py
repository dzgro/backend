import json
import os
from pathlib import Path

# Load the database structure
with open('database_structure.json', 'r') as f:
    db_data = json.load(f)

base_dir = Path('../docs/database/collections')

def explain_index_purpose(index_name, index_keys, collection_name):
    """Generate explanation for index purpose based on fields"""
    keys = list(index_keys.keys())

    if index_name == '_id_':
        return "Primary key index for document identification. Automatically created by MongoDB."

    # Explain based on field combinations
    purposes = []

    # Check for common patterns
    if 'marketplace' in keys:
        purposes.append("Filter and query by marketplace")

    if 'date' in keys:
        purposes.append("Time-based queries and analytics")

    if 'uid' in keys:
        purposes.append("User-specific queries")

    if any('type' in k.lower() for k in keys):
        purposes.append("Category/type-based filtering")

    if len(keys) > 1:
        compound_desc = f"Compound index for efficient queries on {', '.join(keys)}"
        purposes.append(compound_desc)

    if not purposes:
        purposes.append(f"Optimize queries on {', '.join(keys)}")

    return ". ".join(purposes) + "."

def generate_query_examples(index_keys, collection_name):
    """Generate example queries that benefit from this index"""
    keys = list(index_keys.keys())

    if len(keys) == 1 and keys[0] == '_id':
        return [
            f"db.{collection_name}.findOne({{_id: ObjectId('...')}})"
        ]

    examples = []

    # Single field index
    if len(keys) == 1:
        field = keys[0]
        examples.append(f"db.{collection_name}.find({{{field}: <value>}})")
        examples.append(f"db.{collection_name}.find({{{field}: <value>}}).sort({{{field}: 1}})")

    # Compound index
    else:
        # Query using all fields
        query_parts = [f"{k}: <{k}_value>" for k in keys]
        examples.append(f"db.{collection_name}.find({{{', '.join(query_parts)}}})")

        # Query using prefix fields
        for i in range(1, len(keys)):
            prefix_keys = keys[:i]
            query_parts = [f"{k}: <{k}_value>" for k in prefix_keys]
            examples.append(f"db.{collection_name}.find({{{', '.join(query_parts)}}})")

    return examples[:3]  # Limit to 3 examples

def generate_indexes_md(collection_name, collection_data):
    """Generate indexes.md for a collection"""

    indexes = collection_data['indexes']

    md_content = f"""# {collection_name} - Indexes

## Overview

Total Indexes: **{len(indexes)}**

"""

    for idx in indexes:
        index_name = idx['name']
        index_keys = idx['keys']
        is_unique = idx.get('unique', False)
        is_sparse = idx.get('sparse', False)

        md_content += f"## {index_name}\n\n"

        # Index details
        md_content += "### Details\n\n"
        md_content += f"- **Name**: `{index_name}`\n"

        # Format keys
        keys_formatted = []
        for field, direction in index_keys.items():
            dir_str = "ascending" if direction == 1 else "descending"
            keys_formatted.append(f"`{field}` ({dir_str})")

        md_content += f"- **Fields**: {', '.join(keys_formatted)}\n"
        md_content += f"- **Type**: {'Compound' if len(index_keys) > 1 else 'Single Field'}\n"

        if is_unique:
            md_content += "- **Unique**: Yes\n"
        if is_sparse:
            md_content += "- **Sparse**: Yes\n"

        md_content += "\n"

        # Purpose
        purpose = explain_index_purpose(index_name, index_keys, collection_name)
        md_content += "### Purpose\n\n"
        md_content += f"{purpose}\n\n"

        # Query examples
        if index_name != '_id_':
            md_content += "### Example Queries\n\n"
            md_content += "This index optimizes the following query patterns:\n\n"

            examples = generate_query_examples(index_keys, collection_name)
            for example in examples:
                md_content += f"```javascript\n{example}\n```\n\n"

        md_content += "---\n\n"

    # Add index usage notes
    md_content += """## Index Usage Notes

### Compound Index Prefix Rule

For compound indexes, queries can use the index if they query on a prefix of the indexed fields. For example, an index on `(a, b, c)` can optimize queries on:
- `a`
- `a, b`
- `a, b, c`

But NOT on:
- `b`
- `c`
- `b, c`

### Index Selection

MongoDB automatically selects the most efficient index for each query. You can use `.explain()` to see which index was used:

```javascript
db.""" + collection_name + """.find({...}).explain("executionStats")
```
"""

    return md_content

# Generate indexes.md for each collection
print("Generating index documentation for all collections...")
print(f"Total collections: {db_data['total_collections']}\n")

for collection_name, collection_data in db_data['collections'].items():
    print(f"Processing: {collection_name}")

    # Generate indexes.md
    indexes_md = generate_indexes_md(collection_name, collection_data)

    # Write to file
    coll_dir = base_dir / collection_name
    indexes_file = coll_dir / 'indexes.md'
    with open(indexes_file, 'w', encoding='utf-8') as f:
        f.write(indexes_md)

    print(f"  [OK] Created {indexes_file}")

print(f"\n[OK] Successfully generated index documentation for {db_data['total_collections']} collections!")
