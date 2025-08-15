     
def handler(event, context):
    import asyncio
    from dzgroshared.client import DzgroSharedClient
    asyncio.run(DzgroSharedClient().functions(event, context).dzgro_reports_s3_trigger)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }