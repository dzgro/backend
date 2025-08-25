import json
from boto3.session import Session
from dzgroshared.models.model import DzgroSecrets
from dzgroshared.models.enums import ENVIRONMENT

class SecretManager:

    secrets: DzgroSecrets

    def __getattr__(self, item):
        return None

    def __init__(self, env: ENVIRONMENT):
        client = Session().client(
            service_name='secretsmanager',
            region_name='ap-south-1'
        )
        key = f'dzgro/prod' if env == ENVIRONMENT.PROD else f'dzgro/test'
        secrets = json.loads(client.get_secret_value(SecretId=key)['SecretString'])
        self.secrets = DzgroSecrets(**secrets)
