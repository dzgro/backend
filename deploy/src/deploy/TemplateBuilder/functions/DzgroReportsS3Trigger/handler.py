import os, asyncio
all_vars = dict(os.environ)
client=None

def getClient():
    global client
    if client: return client
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