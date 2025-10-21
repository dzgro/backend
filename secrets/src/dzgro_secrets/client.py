import json
import os
from typing import Dict

class SecretManager:
    secrets: dict

    def __init__(self, context=None):
        secrets = self.load_secrets_with_env(context)
        if not secrets: raise ValueError("No Secrets Found")
        if secrets['ENV']== 'prod': secrets = {k[:-5]:v for k,v in secrets.items() if k.endswith('_PROD')}
        else: secrets['AUTH_REDIRECT_URL'] = secrets['AUTH_REDIRECT_URL'].replace("https://", f"https://{secrets['ENV']}")
        secrets['MONGO_DB_CONNECT_URI'] = self.build_mongo_uri(secrets)
        secrets['MONGO_DB_FED_CONNECT_URI'] = self.build_fed_uri(secrets)
        secrets['COGNITO_USER_POOL_ID'] = secrets[f'COGNITO_USER_POOL_ID_{secrets['ENV'].upper()}']
        secrets['COGNITO_APP_CLIENT_ID'] = secrets[f'COGNITO_APP_CLIENT_ID_{secrets['ENV'].upper()}']
        self.secrets = secrets

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
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                secrets = {}
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if not line or line.startswith('#'):
                            continue
                        # Parse key=value pairs
                        if '=' in line:
                            key, value = line.split('=', 1)
                            secrets[key.strip()] = value.strip()
                # Ensure ENV is present
                if 'ENV' not in secrets:
                    secrets['ENV'] = 'dev'
                return secrets
            else:
                # .env file not found, try os.environ as fallback
                secrets = dict(os.environ)
                if 'ENV' not in secrets:
                    secrets['ENV'] = 'dev'
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

    # Properties for each secret key from DzgroSecrets
    @property
    def COGNITO_APP_CLIENT_ID(self) -> str:
        if 'COGNITO_APP_CLIENT_ID' not in self.secrets:
            raise KeyError("COGNITO_APP_CLIENT_ID not found in secrets")
        return self.secrets['COGNITO_APP_CLIENT_ID']

    @property
    def COGNITO_USER_POOL_ID(self) -> str:
        if 'COGNITO_USER_POOL_ID' not in self.secrets:
            raise KeyError("COGNITO_USER_POOL_ID not found in secrets")
        return self.secrets['COGNITO_USER_POOL_ID']

    @property
    def RAZORPAY_CLIENT_ID(self) -> str:
        if 'RAZORPAY_CLIENT_ID' not in self.secrets:
            raise KeyError("RAZORPAY_CLIENT_ID not found in secrets")
        return self.secrets['RAZORPAY_CLIENT_ID']

    @property
    def RAZORPAY_CLIENT_SECRET(self) -> str:
        if 'RAZORPAY_CLIENT_SECRET' not in self.secrets:
            raise KeyError("RAZORPAY_CLIENT_SECRET not found in secrets")
        return self.secrets['RAZORPAY_CLIENT_SECRET']

    @property
    def RAZORPAY_WEBHOOK_SECRET(self) -> str:
        if 'RAZORPAY_WEBHOOK_SECRET' not in self.secrets:
            raise KeyError("RAZORPAY_WEBHOOK_SECRET not found in secrets")
        return self.secrets['RAZORPAY_WEBHOOK_SECRET']

    @property
    def SPAPI_CLIENT_ID(self) -> str:
        if 'SPAPI_CLIENT_ID' not in self.secrets:
            raise KeyError("SPAPI_CLIENT_ID not found in secrets")
        return self.secrets['SPAPI_CLIENT_ID']

    @property
    def SPAPI_CLIENT_SECRET(self) -> str:
        if 'SPAPI_CLIENT_SECRET' not in self.secrets:
            raise KeyError("SPAPI_CLIENT_SECRET not found in secrets")
        return self.secrets['SPAPI_CLIENT_SECRET']

    @property
    def SPAPI_APPLICATION_ID(self) -> str:
        if 'SPAPI_APPLICATION_ID' not in self.secrets:
            raise KeyError("SPAPI_APPLICATION_ID not found in secrets")
        return self.secrets['SPAPI_APPLICATION_ID']

    @property
    def ADS_CLIENT_ID(self) -> str:
        if 'ADS_CLIENT_ID' not in self.secrets:
            raise KeyError("ADS_CLIENT_ID not found in secrets")
        return self.secrets['ADS_CLIENT_ID']

    @property
    def ADS_CLIENT_SECRET(self) -> str:
        if 'ADS_CLIENT_SECRET' not in self.secrets:
            raise KeyError("ADS_CLIENT_SECRET not found in secrets")
        return self.secrets['ADS_CLIENT_SECRET']

    @property
    def MONGO_DB_CONNECT_URI(self) -> str:
        if 'MONGO_DB_CONNECT_URI' not in self.secrets:
            raise KeyError("MONGO_DB_CONNECT_URI not found in secrets")
        return self.secrets['MONGO_DB_CONNECT_URI']

    @property
    def MONGO_DB_FED_CONNECT_URI(self) -> str:
        if 'MONGO_DB_FED_CONNECT_URI' not in self.secrets:
            raise KeyError("MONGO_DB_FED_CONNECT_URI not found in secrets")
        return self.secrets['MONGO_DB_FED_CONNECT_URI']

    @property
    def USER_DUMMY_PASSWORD(self) -> str:
        if 'USER_DUMMY_PASSWORD' not in self.secrets:
            raise KeyError("USER_DUMMY_PASSWORD not found in secrets")
        return self.secrets['USER_DUMMY_PASSWORD']

    @property
    def AUTH_REDIRECT_URL(self) -> str:
        if 'AUTH_REDIRECT_URL' not in self.secrets:
            raise KeyError("AUTH_REDIRECT_URL not found in secrets")
        return self.secrets['AUTH_REDIRECT_URL']

    @property
    def DB_NAME(self) -> str:
        if 'env' not in self.secrets:
            raise KeyError("Env not found in secrets")
        return f"dzgro-{self.secrets['ENV']}"

