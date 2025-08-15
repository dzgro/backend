     
def handler(event, context):
    import asyncio
    from dzgroshared.client import DzgroSharedClient
    asyncio.run(DzgroSharedClient().functions(event, context).amazon_daily_report)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }