import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Any, Dict, List

# Add parent directory to path to import from secrets
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Change working directory to parent to find .env
os.chdir(parent_dir)

from dzgro_secrets.client import SecretManager


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB types"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class DatabaseInspector:
    def __init__(self):
        self.secrets = SecretManager().secrets
        self.client = None
        self.db = None
        self.db_name = "dzgro-dev"

    async def connect(self):
        """Connect to MongoDB"""
        print(f"Connecting to MongoDB database: {self.db_name}...")
        self.client = AsyncIOMotorClient(self.secrets['MONGO_DB_CONNECT_URI'])
        self.db = self.client[self.db_name]
        print("Connected successfully!")

    async def list_collections(self) -> List[str]:
        """List all collections in the database"""
        print("\n=== Listing all collections ===")
        collections = await self.db.list_collection_names()
        print(f"Found {len(collections)} collections:")
        for i, coll in enumerate(collections, 1):
            print(f"{i}. {coll}")
        return collections

    async def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        stats = await self.db.command("collStats", collection_name)
        return {
            "count": stats.get("count", 0),
            "size": stats.get("size", 0),
            "avgObjSize": stats.get("avgObjSize", 0),
            "storageSize": stats.get("storageSize", 0),
        }

    async def get_indexes(self, collection_name: str) -> List[Dict]:
        """Get all indexes for a collection"""
        collection = self.db[collection_name]
        indexes = await collection.list_indexes().to_list(None)
        return indexes

    async def sample_documents(self, collection_name: str, limit: int = 50) -> List[Dict]:
        """Sample documents from a collection"""
        collection = self.db[collection_name]
        # Get all documents to analyze structure
        cursor = collection.find().limit(limit)
        docs = await cursor.to_list(length=limit)
        return docs

    def analyze_document_structure(self, docs: List[Dict]) -> Dict:
        """Analyze the structure of documents to find all possible fields"""
        all_fields = {}

        def extract_fields(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    field_path = f"{prefix}.{key}" if prefix else key

                    if field_path not in all_fields:
                        all_fields[field_path] = {
                            "type": set(),
                            "sample_values": [],
                            "is_array": False,
                            "nested_fields": {}
                        }

                    value_type = type(value).__name__
                    all_fields[field_path]["type"].add(value_type)

                    if isinstance(value, (str, int, float, bool)) and len(all_fields[field_path]["sample_values"]) < 3:
                        all_fields[field_path]["sample_values"].append(value)
                    elif isinstance(value, ObjectId):
                        all_fields[field_path]["sample_values"].append(str(value))
                    elif isinstance(value, list):
                        all_fields[field_path]["is_array"] = True
                        if value and isinstance(value[0], dict):
                            extract_fields(value[0], field_path)
                    elif isinstance(value, dict):
                        extract_fields(value, field_path)

        for doc in docs:
            extract_fields(doc)

        # Convert sets to lists for JSON serialization
        for field_info in all_fields.values():
            field_info["type"] = list(field_info["type"])

        return all_fields

    def find_reference_fields(self, fields: Dict) -> List[str]:
        """Find fields that likely reference other collections"""
        reference_fields = []

        for field_name, field_info in fields.items():
            # Look for fields ending with Id or _id that are ObjectId type
            if (field_name.endswith('Id') or field_name.endswith('_id')) and 'ObjectId' in field_info['type']:
                reference_fields.append(field_name)
            # Look for fields with 'account' or 'marketplace' in the name
            elif any(keyword in field_name.lower() for keyword in ['account', 'marketplace', 'user', 'profile']):
                if 'ObjectId' in field_info['type'] or 'str' in field_info['type']:
                    reference_fields.append(field_name)

        return reference_fields

    async def inspect_all(self):
        """Inspect all collections and gather comprehensive information"""
        await self.connect()

        collections = await self.list_collections()

        all_data = {
            "database": self.db_name,
            "total_collections": len(collections),
            "collections": {}
        }

        for collection_name in collections:
            print(f"\n{'='*60}")
            print(f"Inspecting collection: {collection_name}")
            print('='*60)

            # Get stats
            stats = await self.get_collection_stats(collection_name)
            print(f"Documents count: {stats['count']}")
            print(f"Average document size: {stats['avgObjSize']} bytes")

            # Get indexes
            indexes = await self.get_indexes(collection_name)
            print(f"\nIndexes ({len(indexes)}):")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx.get('key', {})}")

            # Sample documents
            print(f"\nSampling up to 50 documents...")
            docs = await self.sample_documents(collection_name, limit=50)

            # Analyze structure
            fields = self.analyze_document_structure(docs)
            print(f"Found {len(fields)} unique fields")

            # Find references
            references = self.find_reference_fields(fields)
            if references:
                print(f"\nPotential reference fields: {', '.join(references)}")

            # Store data
            all_data["collections"][collection_name] = {
                "stats": stats,
                "indexes": [
                    {
                        "name": idx['name'],
                        "keys": idx.get('key', {}),
                        "unique": idx.get('unique', False),
                        "sparse": idx.get('sparse', False)
                    }
                    for idx in indexes
                ],
                "fields": fields,
                "reference_fields": references,
                "sample_documents": docs[:3]  # Store first 3 documents as samples
            }

        # Save to JSON file
        output_file = "db-inspector/database_structure.json"
        with open(output_file, 'w') as f:
            json.dump(all_data, f, indent=2, cls=JSONEncoder)

        print(f"\n{'='*60}")
        print(f"Inspection complete! Data saved to {output_file}")
        print('='*60)

        return all_data

    async def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()


async def main():
    inspector = DatabaseInspector()
    try:
        await inspector.inspect_all()
    finally:
        await inspector.close()


if __name__ == "__main__":
    asyncio.run(main())
