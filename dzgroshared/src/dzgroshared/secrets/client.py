from .model import DzgroSecrets

class SecretManager:
    secrets: DzgroSecrets

    def __getattr__(self, item):
        return None

    def __init__(self, context=None):
        # Import SecretManager from dzgro_secrets project
        from dzgro_secrets.client import SecretManager as SecretsClient

        # Get secrets as dict from dzgro_secrets project
        secrets_client = SecretsClient(context)
        secrets_dict = secrets_client.secrets

        # Cast to DzgroSecrets model and set to self
        self.secrets = DzgroSecrets(**secrets_dict)
\