import json
from boto3.session import Session
from .model import DzgroSecrets
from ..db.enums import ENVIRONMENT

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
        key = f'dzgro/prod'
        secrets = json.loads(client.get_secret_value(SecretId=key)['SecretString'])
        self.secrets = DzgroSecrets(**secrets)
        MONGO_DB_FED_CONNECT_URI = self.secrets.MONGO_DB_FED_CONNECT_URI.replace('fed', f'fed-{env.value.lower()}')
        self.secrets.MONGO_DB_FED_CONNECT_URI = MONGO_DB_FED_CONNECT_URI

