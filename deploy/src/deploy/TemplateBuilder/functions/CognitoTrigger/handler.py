import os
import json
import boto3
from pymongo import MongoClient

secrets_client = boto3.client("secretsmanager")

def get_mongo_client():
    secret_name = "dzgro/prod"
    secret_value = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(secret_value["SecretString"])
    mongo_uri = secret["MONGO_DB_CONNECT_URI"]
    db_name = f"dzgro-dev"
    return MongoClient(mongo_uri)[db_name]

db = None

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    global db
    if db is None:  # lazy init so cold start only
        db = get_mongo_client()
    username = event.get("userName",None)
    print(f"👤 User {username}")
    if username:
        if event["triggerSource"] == "PostConfirmation_ConfirmSignUp":
            attrs = event["request"]["userAttributes"]
            user_doc = { "_id": username, "name": attrs.get("name"), "email": attrs.get("email"), "phone_number": attrs.get("phone_number"), "status": "new" }
            try:
                db.users.update_one( {"_id": username}, {"$setOnInsert": user_doc}, upsert=True )
                print(f"✅ User {username} inserted in {db.name}")
            except Exception as e:
                print(f"❌ DB insert failed: {e}")
        elif event["triggerSource"] == "TokenGeneration_HostedAuth":
            status = "unknown"
            doc = db.users.find_one({"_id": username}, {"status": 1})
            if doc and "status" in doc:
                status = doc["status"]
            print(f"🔑 status: {status}")
            event['response'] = {
                'claimsAndScopeOverrideDetails': {
                    'idTokenGeneration': {
                        'claimsToAddOrOverride': {
                            'status': status
                        }
                    },
                    'accessTokenGeneration': {
                        'claimsToAddOrOverride': {
                            'status': status
                        },
                        'scopesToAdd': ['dzgro/read']
                    }
                }
            }
        

    return event
