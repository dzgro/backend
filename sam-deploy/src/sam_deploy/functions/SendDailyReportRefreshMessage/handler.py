import os, asyncio
all_vars = dict(os.environ)
client=None

def getClient():
    global client
    if client: return client
    from dzgroshared.client import DzgroSharedClient
    client = DzgroSharedClient()
    return client

def handler(event, context):
    print(event)
    asyncio.run(getClient().functions(event, context).send_daily_report_refresh_message_to_queue)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }