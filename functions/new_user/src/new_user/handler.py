from db import DbClient
from dzgrosecrets.helper import SecretManager
MONGO_DB_URI = SecretManager().secrets.MONGO_DB_CONNECT_URI
import json, asyncio

async def handler(event: dict, context):
    asyncio.run(addUser(event, context))

async def addUser(event, context):
    body = json.loads(event['Records'][0]['body'])
    id, details = body['id'], body['details']
    try:
        await DbClient(MONGO_DB_URI).user(id).addUserToDb(details)
    except Exception as e:
        pass