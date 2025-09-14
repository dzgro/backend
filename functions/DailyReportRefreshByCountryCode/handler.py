import os
from dzgroshared.db.enums import ENVIRONMENT
ENV = ENVIRONMENT(os.environ.get("ENV"))
from dzgroshared.client import DzgroSharedClient
client = DzgroSharedClient(ENV)
db = client.db

def handler(event, context):
    print(event)
    import asyncio
    asyncio.run(client.functions(event, context).daily_report_refresh)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }