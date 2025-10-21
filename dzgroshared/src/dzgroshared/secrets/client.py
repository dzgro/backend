import json
from boto3.session import Session
from .model import DzgroSecrets
from ..db.enums import ENVIRONMENT

class SecretManager:

    secrets: DzgroSecrets

    def __getattr__(self, item):
        return None

    def __init__(self, env: ENVIRONMENT, secrets: dict = {}):
        if not secrets:
            client = Session().client( service_name='secretsmanager', region_name='ap-south-1' )
            key = f'dzgro/prod'
            secrets = json.loads(client.get_secret_value(SecretId=key)['SecretString'])
        if env== ENVIRONMENT.PROD: secrets = {k[:-5]:v for k,v in secrets.items() if k.endswith('_PROD')}
        else: secrets['AUTH_REDIRECT_URL'] = secrets['AUTH_REDIRECT_URL'].replace("https://", f"https://{env.value}")
        secrets['MONGO_DB_CONNECT_URI'] = self.build_mongo_uri(env, secrets)
        secrets['MONGO_DB_FED_CONNECT_URI'] = self.build_fed_uri(env, secrets)
        envname = ENVIRONMENT.DEV.name
        secrets['COGNITO_USER_POOL_ID'] = secrets[f'COGNITO_USER_POOL_ID_{envname}']
        secrets['COGNITO_APP_CLIENT_ID'] = secrets[f'COGNITO_APP_CLIENT_ID_{envname}']
        self.secrets = DzgroSecrets(**secrets)

    def build_mongo_uri(self, env: ENVIRONMENT, secrets: dict):
        from urllib.parse import quote_plus
        MONGO_USER = f'{env.value}-user'
        username = quote_plus(MONGO_USER)
        password = quote_plus(secrets['MONGO_PASSWORD'])
        dbname = f'dzgro-{env.value}'
        uri = f"mongodb+srv://{username}:{password}@{secrets['MONGO_CLUSTER_URL']}/{dbname}?retryWrites=true&w=majority&appName=dzgro"
        return uri

    def build_fed_uri(self, env: ENVIRONMENT, secrets: dict):
        from urllib.parse import quote_plus
        MONGO_USER = f'{env.value}-user'
        username = quote_plus(MONGO_USER)
        password = quote_plus(secrets['MONGO_PASSWORD'])
        dbname = f'dzgro-{env.value}'
        uri = f"mongodb://{username}:{password}@{secrets['MONGO_FED_URL']}/{dbname}?retryWrites=true&w=majority&ssl=true&authSource=admin&appName=fed-dzgro"
        uri = uri.replace('fed', f'fed-{env.value}')
        return uri

