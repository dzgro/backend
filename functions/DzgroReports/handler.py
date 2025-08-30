import os, asyncio
from dzgroshared.models.enums import ENVIRONMENT
ENV = ENVIRONMENT(os.environ.get("ENV"))
from dzgroshared.client import DzgroSharedClient
client = DzgroSharedClient(ENV)
db = client.db

def handler(event, context):
    print(event)
    asyncio.run(client.functions(event, context).dzgro_reports)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }