import json
import os
from typing import Dict

class SecretManager:

    def __getattr__(self, item):
        return None

    def __init__(self):
        pass

    def load_secrets_with_env(self, context=None) -> Dict[str, str]:
        """
        Load secrets based on execution environment.

        - In Lambda: Load from environment variables. ENV is determined from Lambda alias in context
          or from environment variable if context is not provided.
        - Locally: Load from .env file.

        Args:
            context: Lambda context (optional). If provided and running in Lambda,
                    extracts ENV from invoked_function_arn alias.

        Returns:
            Dictionary containing all secrets including ENV variable.
        """
        is_lambda = 'AWS_LAMBDA_FUNCTION_NAME' in os.environ or 'AWS_EXECUTION_ENV' in os.environ

        if is_lambda:
            # Running in Lambda - load from environment variables
            secrets = dict(os.environ)

            # Determine ENV from Lambda alias if context is provided
            if context and hasattr(context, 'invoked_function_arn'):
                # Extract alias from ARN: arn:aws:lambda:region:account:function:name:alias
                arn_parts = context.invoked_function_arn.split(':')
                if len(arn_parts) >= 8:
                    alias = arn_parts[7]  # The alias name (dev, staging, prod)
                    secrets['ENV'] = alias
                elif 'ENV' not in secrets:
                    # Fallback to 'dev' if no alias found
                    secrets['ENV'] = 'dev'
            elif 'ENV' not in secrets:
                # If no context provided, ENV should already be in environment variables
                # Fallback to 'dev' if not found
                secrets['ENV'] = 'dev'

            return secrets
        else:
            # Running locally - load from .env file
            try:
                from dotenv import dotenv_values
                # Load .env file from current working directory
                env_path = os.path.join(os.getcwd(), '.env')
                if os.path.exists(env_path):
                    # Filter out None values from dotenv_values
                    secrets = {k: v for k, v in dotenv_values(env_path).items() if v is not None}
                    # Ensure ENV is present
                    if 'ENV' not in secrets:
                        secrets['ENV'] = 'dev'
                    return secrets
                else:
                    # .env file not found, return empty dict with default ENV
                    return {'ENV': 'dev'}
            except ImportError:
                # python-dotenv not installed, try to load from os.environ
                secrets = dict(os.environ)
                if 'ENV' not in secrets:
                    secrets['ENV'] = 'dev'
                return secrets
    
    def build(self, context=None):
        secrets = self.load_secrets_with_env(context)
        if not secrets: raise ValueError("No Secrets Found")
        if secrets['ENV']== 'prod': secrets = {k[:-5]:v for k,v in secrets.items() if k.endswith('_PROD')}
        else: secrets['AUTH_REDIRECT_URL'] = secrets['AUTH_REDIRECT_URL'].replace("https://", f"https://{secrets['ENV']}")
        secrets['MONGO_DB_CONNECT_URI'] = self.build_mongo_uri(secrets)
        secrets['MONGO_DB_FED_CONNECT_URI'] = self.build_fed_uri(secrets)
        envname = 'dev'
        secrets['COGNITO_USER_POOL_ID'] = secrets[f'COGNITO_USER_POOL_ID_{envname}']
        secrets['COGNITO_APP_CLIENT_ID'] = secrets[f'COGNITO_APP_CLIENT_ID_{envname}']
        return secrets
        

    def build_mongo_uri(self, secrets: dict):
        from urllib.parse import quote_plus
        MONGO_USER = f'{secrets['ENV']}-user'
        username = quote_plus(MONGO_USER)
        password = quote_plus(secrets['MONGO_PASSWORD'])
        dbname = f'dzgro-{secrets['ENV']}'
        uri = f"mongodb+srv://{username}:{password}@{secrets['MONGO_CLUSTER_URL']}/{dbname}?retryWrites=true&w=majority&appName=dzgro"
        return uri

    def build_fed_uri(self, secrets: dict):
        from urllib.parse import quote_plus
        MONGO_USER = f'{secrets['ENV']}-user'
        username = quote_plus(MONGO_USER)
        password = quote_plus(secrets['MONGO_PASSWORD'])
        dbname = f'dzgro-{secrets['ENV']}'
        uri = f"mongodb://{username}:{password}@{secrets['MONGO_FED_URL']}/{dbname}?retryWrites=true&w=majority&ssl=true&authSource=admin&appName=fed-dzgro"
        uri = uri.replace('fed', f'fed-{secrets['ENV']}')
        return uri

