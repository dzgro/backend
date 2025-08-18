📘 MongoDB Schema Extractor with Compound Index Relationships
🚀 Overview

This project provides a Python utility to automatically extract and document the schema of your MongoDB database.

Unlike traditional schema extraction, this script is designed for:

Compound Index Aware Analysis → Uses compound indexes (e.g. { uid: 1, marketplace: 1, date: 1 }) to explore data in meaningful ways.

Progressive Document Sampling → Fetches sample documents grouped by each part of compound indexes, ensuring a comprehensive picture of your data.

Relationship Discovery → Infers potential relationships across collections based on:

Single index fields (uid)

Multi-field compound prefixes (uid + marketplace)

Schema Output → Produces a JSON file summarizing:

Collections

Index definitions

Possible relationships

Representative sample documents

This schema can be used for:

Understanding large MongoDB deployments

Bootstrapping AI assistants (e.g., GitHub Copilot or ChatGPT) with your data model

Designing query builders, APIs, or migrations

📂 Features

✅ List all collections and indexes

✅ Extract sample documents using compound index fields

✅ Infer relationships between collections (based on index prefixes)

✅ Provide progress updates while running

✅ Export schema to JSON for Copilot & AI integration

⚙️ Example Relationship Extraction

For a compound index:

{ "uid": 1, "marketplace": 1, "date": 1 }

The script will generate relationships:

"relationships": [
{ "fields": ["uid"], "compound": false },
{ "fields": ["uid", "marketplace"], "compound": true },
{ "fields": ["uid", "marketplace", "date"], "compound": true }
]

This means:

Documents may relate to others by uid

Or by (uid, marketplace) pairs

Or by (uid, marketplace, date)

🛠️ Installation

Clone the repo:

git clone https://github.com/your-org/mongo-schema-extractor.git
cd mongo-schema-extractor

Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Set up environment variables in .env:

MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net
DATABASE_NAME=my_database

▶️ Usage

Run the script with environment variables:

python extract_schema.py

Or pass parameters explicitly:

python extract_schema.py \
 --mongo-uri "mongodb+srv://user:pass@cluster.mongodb.net" \
 --database my_database

📊 Output

The script generates schema.json like:

{
"collection": "orders",
"indexes": ["uid_1_marketplace_1_date_1"],
"relationships": [
{ "fields": ["uid"], "compound": false },
{ "fields": ["uid", "marketplace"], "compound": true },
{ "fields": ["uid", "marketplace", "date"], "compound": true }
],
"sample_documents": [
{
"uid": "U123",
"marketplace": "IN",
"date": "2025-08-18",
"total": 599.0
}
]
}

🔗 Next Steps

Use the schema.json with GitHub Copilot or AI tools by pasting it into their context → they will better understand your MongoDB structure.

Extend the relationship logic to support cross-collection inference (e.g., if both orders and users share uid, they’re related).

Add visual schema diagrams for quicker comprehension.

⚡ With this, you’ll have a living schema explorer for your MongoDB, always aligned with your compound indexes and relationships.
