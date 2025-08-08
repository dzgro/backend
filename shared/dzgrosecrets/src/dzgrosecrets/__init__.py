import json
from boto3.session import Session
from pydantic import BaseModel


class DzgroSecrets(BaseModel):
    COGNITO_APP_CLIENT_ID: str
    COGNITO_USER_POOL_ID: str
    RAZORPAY_CLIENT_ID: str
    RAZORPAY_PLAN_ID: str
    RAZORPAY_CLIENT_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str
    SPAPI_CLIENT_ID: str
    SPAPI_CLIENT_SECRET: str
    SPAPI_APPLICATION_ID: str
    ADS_CLIENT_ID: str
    ADS_CLIENT_SECRET: str
    MONGO_DB_CONNECT_URI: str
    MONGO_DB_FED_CONNECT_URI: str

class SecretManager(DzgroSecrets):

    def __getattr__(self, item):
        return None

    def __init__(self):
        client = Session().client(
            service_name='secretsmanager',
            region_name='ap-south-1'
        )
        global_secrets = json.loads(client.get_secret_value(SecretId='dzgro/main')['SecretString'])
        stage_secrets = json.loads(client.get_secret_value(SecretId='dzgro/test')['SecretString'])
        json_value = {**global_secrets, **stage_secrets}
        self.__dict__.update(DzgroSecrets(**json_value).__dict__)
