import os, asyncio
all_vars = dict(os.environ)
from dzgroshared.db.queue_messages.model import QueueMessageModelType
client=None

def getClient():
    global client
    from dzgroshared.db.enums import ENVIRONMENT
    ENV = ENVIRONMENT(os.environ.get("ENV"))
    from dzgroshared.secrets.model import DzgroSecrets
    from dzgroshared.client import DzgroSharedClient
    client = DzgroSharedClient(ENV)
    client.setSecretsClient(DzgroSecrets.model_validate(all_vars))
    return client


def handler(event, context):
    print(event)
    client = getClient()
    asyncio.run(client.functions(event, context).dzgro_reports_s3_trigger)
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }