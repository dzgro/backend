import json
from boto3.session import Session
from dzgroshared.models.model import DzgroSecrets

class SecretManager:

    secrets: DzgroSecrets

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
        self.secrets = DzgroSecrets(**json_value)
