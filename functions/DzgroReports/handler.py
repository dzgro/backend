import os
from dzgroshared.models.enums import ENVIRONMENT
ENV = ENVIRONMENT(os.environ.get("ENV"))

def handler(event, context):
    print(event)
    import asyncio
    from dzgroshared.client import DzgroSharedClient
    asyncio.run(DzgroSharedClient(ENV).functions(event, context).dzgro_reports)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }