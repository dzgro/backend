from dzgroshared.models.enums import ENVIRONMENT

def handler(event, context):
    import asyncio
    from dzgroshared.client import DzgroSharedClient
    asyncio.run(DzgroSharedClient(ENVIRONMENT.PROD).functions(event, context).ams_change)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }