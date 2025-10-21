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
    client = getClient()
    asyncio.run(client.functions(event, context).dzgro_reports_s3_trigger)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }