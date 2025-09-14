import os, asyncio
from dzgroshared.db.enums import ENVIRONMENT
ENV = ENVIRONMENT(os.environ.get("ENV"))
from dzgroshared.client import DzgroSharedClient
client = DzgroSharedClient(ENV)
db = client.db

def handler(event, context):
    print(event)
    asyncio.run(client.functions(event, context).send_daily_report_refresh_message_to_queue)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }