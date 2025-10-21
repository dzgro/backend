from sam_deploy.config.mapping import LambdaName, ENVIRONMENT, LambdaProperty, LAMBDAS, Region, QueueProperty, QueueRole, S3Property, S3Role
from sam_deploy.builder.template_builder import TemplateBuilder
from typing import Dict


class LambdaBuilder:
    builder: TemplateBuilder
    environment_secrets: Dict[str, Dict[str, str]]

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

        # Pre-load secrets for all environments to avoid repeated SecretManager calls
        # Secrets are environment-specific (e.g., different DB credentials per environment)
        self.environment_secrets = {}
        print(f"[SECRETS] Pre-loading secrets for all environments...")

        from dzgroshared.secrets.client import SecretManager
        for env in [ENVIRONMENT.DEV, ENVIRONMENT.STAGING, ENVIRONMENT.PROD]:
            try:
                secrets = SecretManager(env).secrets.model_dump(mode="json")
                self.environment_secrets[env.value] = secrets
                print(f"  [OK] Loaded {len(secrets)} secrets for {env.value}")
            except Exception as e:
                print(f"  [WARNING] Failed to load secrets for {env.value}: {e}")
                self.environment_secrets[env.value] = {}

    def build_lambda_with_aliases(self, lambda_config: LambdaProperty, layer_arns: Dict, region: Region) -> None:
        """
        Build a Lambda function with three aliases (dev, staging, prod).

        The Lambda function is created WITHOUT environment suffix and includes:
        - Base Lambda function with AutoPublishAlias: "dev"
        - Three aliases: dev ($LATEST), staging (published version), prod (published version)
        - IAM role shared across all aliases (no env suffix)
        - Environment variables per lambda_config
        - Permissions for each alias
        """
        # Get Lambda region configuration
        lambda_region = next((lr for lr in lambda_config.regions if lr.region == region), None)
        if not lambda_region:
            return

        # Load secrets for environment variables
        from dzgroshared.secrets.client import SecretManager
        secrets = SecretManager(self.builder.env).secrets.model_dump(mode="json")

        # Function name WITHOUT environment suffix (e.g., "ApiFunction")
        fn_name = self.builder.getFunctionName(lambda_config.name)

        # Build environment variables
        env_variables = {"ENV": self.builder.env.value, **secrets}

        # Base Lambda function properties
        properties = {
            'FunctionName': fn_name,
            'Handler': 'handler.handler',
            'Runtime': 'python3.12',
            'Architectures': ['x86_64'],
            'CodeUri': f'functions/{lambda_config.name.value}',
            'Description': f'{lambda_config.description}',
            'Timeout': lambda_config.timeout,
            'MemorySize': lambda_config.memorySize,
            'Role': {'Fn::GetAtt': [self.builder.getLambdaRoleName(lambda_config.name), 'Arn']},
            'Tags': self.builder.getDictTag(),
            'Environment': {'Variables': env_variables}
        }

        # Add layers if specified
        if lambda_config.layers:
            properties['Layers'] = [layer_arns[name] for name in lambda_config.layers]

        # Add S3 event triggers if configured
        for s3 in lambda_region.s3:
            if s3.trigger:
                event = {
                    'Bucket': {'Ref': self.builder.getBucketResourceName(s3.name)},
                    'Events': s3.trigger.eventName
                }
                if s3.trigger.filter:
                    event['Filter'] = s3.trigger.filter
                properties['Events'] = {
                    'S3UploadEvent': {
                        'Type': 'S3',
                        'Properties': event
                    }
                }

        # Create Lambda function resource
        self.builder.resources[fn_name] = {
            'Type': 'AWS::Serverless::Function',
            'Properties': properties
        }

        # Create aliases only if AutoPublishAlias is enabled
        # TODO: Re-enable when AutoPublishAlias is fixed
        # self._create_lambda_aliases(fn_name, lambda_config.name)

        # Create IAM role for Lambda (shared across all aliases)
        if self.builder.env != ENVIRONMENT.DEV:
            self._create_lambda_role(lambda_config, lambda_region)

    def _create_lambda_aliases(self, fn_name: str, lambda_name: LambdaName) -> None:
        """
        Create two Lambda aliases for staging and prod.

        - dev: Created automatically by AutoPublishAlias (not manual)
        - staging: points to published version (!GetAtt Function.Version)
        - prod: points to published version (!GetAtt Function.Version)
        """
        # NOTE: Dev alias is created automatically by AutoPublishAlias property in Lambda function
        # No need to manually create it here

        # Staging alias - points to published version
        staging_alias_name = f'{fn_name}AliasStaging'
        self.builder.resources[staging_alias_name] = {
            'Type': 'AWS::Lambda::Alias',
            'Properties': {
                'FunctionName': {'Ref': fn_name},
                'FunctionVersion': {'Fn::GetAtt': [fn_name, 'Version']},
                'Name': 'staging'
            }
        }

        # Prod alias - points to published version
        prod_alias_name = f'{fn_name}AliasProd'
        self.builder.resources[prod_alias_name] = {
            'Type': 'AWS::Lambda::Alias',
            'Properties': {
                'FunctionName': {'Ref': fn_name},
                'FunctionVersion': {'Fn::GetAtt': [fn_name, 'Version']},
                'Name': 'prod'
            }
        }

    def _create_lambda_role(self, lambda_config: LambdaProperty, lambda_region) -> None:
        """
        Create IAM role for Lambda function.

        Role is shared across all aliases and does NOT include environment suffix.
        Includes permissions for SQS queues and S3 buckets as configured.
        """
        role_name = self.builder.getLambdaRoleName(lambda_config.name)

        role = {
            'Type': 'AWS::IAM::Role',
            'Properties': {
                'RoleName': role_name,
                'AssumeRolePolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Principal': {'Service': 'lambda.amazonaws.com'},
                            'Action': 'sts:AssumeRole'
                        }
                    ]
                },
                'ManagedPolicyArns': [
                    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                ]
            }
        }

        # Add inline policies for SQS, S3, and Cognito access
        if lambda_config.name == LambdaName.CognitoTrigger:
            # Add Cognito-specific permissions for CognitoTrigger Lambda
            role['Properties']['Policies'] = [{
                'PolicyName': 'LambdaCognitoAccess',
                'PolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [{
                        'Effect': 'Allow',
                        'Action': [
                            'cognito-idp:AdminGetUser',
                            'cognito-idp:AdminDeleteUser',
                            'cognito-idp:ListUsers'
                        ],
                        'Resource': '*'
                    }]
                }
            }]
        else:
            # Collect queue and bucket configurations
            queue_names = {
                self.builder.getQueueName(q.name, 'Q'): q.roles
                for q in lambda_region.queue
            }
            bucket_names = {
                self.builder.getBucketName(s3.name): s3.roles
                for s3 in lambda_region.s3
            }

            if queue_names or bucket_names:
                role['Properties']['Policies'] = []

            # Add SQS permissions
            if queue_names:
                role['Properties']['Policies'].append({
                    'PolicyName': 'LambdaSQSAccess',
                    'PolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Action': [x.value for x in QueueRole.all()],
                                'Resource': [{'Fn::GetAtt': [k, 'Arn']}]
                            } for k, v in queue_names.items()
                        ]
                    }
                })

            # Add S3 permissions
            if bucket_names:
                role['Properties']['Policies'].append({
                    'PolicyName': 'LambdaS3Access',
                    'PolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Action': [
                                    x.value for x in [
                                        S3Role.GetObject,
                                        S3Role.PutObject,
                                        S3Role.DeleteObject
                                    ]
                                ],
                                'Resource': [
                                    {'Fn::Sub': f'arn:aws:s3:::{k}/*'}
                                    for k in bucket_names.keys()
                                ]
                            },
                            {
                                'Effect': 'Allow',
                                'Action': [x.value for x in [S3Role.ListBucket]],
                                'Resource': [
                                    {'Fn::Sub': f'arn:aws:s3:::{k}'}
                                    for k in bucket_names.keys()
                                ]
                            }
                        ]
                    }
                })

        self.builder.resources[role_name] = role

    def execute(self, region: Region, layer_arns: Dict) -> None:
        """
        Build all Lambda functions with aliases for the given region.

        Args:
            region: AWS region to build Lambdas for
            layer_arns: Dictionary mapping LAYER_NAME to ARN strings
        """
        for lambda_config in LAMBDAS:
            # Check if this lambda is configured for this region
            if any(lr.region == region for lr in lambda_config.regions):
                self.build_lambda_with_aliases(lambda_config, layer_arns, region)

    def execute_with_aliases(self, region: Region, layer_arns: Dict, environments: list) -> None:
        """
        Build all Lambda functions with explicit aliases (dev, staging, prod) for single-stack architecture.

        Creates:
        - 1 Lambda function per lambda type (no environment suffix)
        - 3 aliases per function: dev, staging, prod (all pointing to $LATEST initially)
        - 1 IAM role per function (with permissions for ALL environment queues/buckets)

        Important: Lambda function does NOT include environment-specific secrets.
        Lambda code should detect which alias invoked it (via context.invoked_function_arn)
        and fetch appropriate secrets from AWS Secrets Manager based on the alias name.

        Args:
            region: AWS region to build Lambdas for
            layer_arns: Dictionary mapping LAYER_NAME to ARN strings
            environments: List of ENVIRONMENT enums (DEV, STAGING, PROD)
        """
        for lambda_config in LAMBDAS:
            # Check if this lambda is configured for this region
            lambda_region = next((lr for lr in lambda_config.regions if lr.region == region), None)
            if not lambda_region:
                continue

            # Function name WITHOUT environment suffix
            fn_name = self.builder.getFunctionName(lambda_config.name)

            # Build environment variables with ALL environment secrets (prefixed by environment)
            # Lambda code should detect which alias invoked it (via context.invoked_function_arn)
            # and use the appropriate environment-prefixed variables
            #
            # Example: If invoked via 'dev' alias, use DEV_DATABASE_URL
            #          If invoked via 'staging' alias, use STAGING_DATABASE_URL
            env_variables = {}

            # Add environment-specific secrets with prefixes
            for env in environments:
                if env not in lambda_config.env:
                    continue

                env_prefix = env.value.upper()
                env_secrets = self.environment_secrets.get(env.value, {})

                # Add each secret with environment prefix
                for key, value in env_secrets.items():
                    prefixed_key = f"{env_prefix}_{key}"
                    env_variables[prefixed_key] = value

            # Base Lambda function properties
            properties = {
                'FunctionName': fn_name,
                'Handler': 'handler.handler',
                'Runtime': 'python3.12',
                'Architectures': ['x86_64'],
                'CodeUri': f'functions/{lambda_config.name.value}',
                'Description': f'{lambda_config.description}',
                'Timeout': lambda_config.timeout,
                'MemorySize': lambda_config.memorySize,
                'Role': {'Fn::GetAtt': [self.builder.getLambdaRoleName(lambda_config.name), 'Arn']},
                'Tags': self.builder.getDictTag(),
                'Environment': {'Variables': env_variables},
                'AutoPublishAlias': 'live'  # Auto-publish to 'live' alias (required for versioning)
            }

            # Add layers if specified
            if lambda_config.layers:
                properties['Layers'] = [layer_arns[name] for name in lambda_config.layers]

            # Add S3 event triggers if configured (skip dev buckets, use staging instead)
            for s3 in lambda_region.s3:
                if s3.trigger:
                    event = {
                        'Bucket': {'Ref': f'{s3.name.value.replace("-", " ").title().replace(" ", "")}StagingBucket'},
                        'Events': s3.trigger.eventName
                    }
                    if s3.trigger.filter:
                        event['Filter'] = s3.trigger.filter
                    properties['Events'] = {
                        'S3UploadEvent': {
                            'Type': 'S3',
                            'Properties': event
                        }
                    }

            # Create Lambda function resource
            self.builder.resources[fn_name] = {
                'Type': 'AWS::Serverless::Function',
                'Properties': properties
            }

            # Create aliases only for environments where this lambda is configured
            for env in environments:
                # Only create alias if lambda is configured for this environment
                if env not in lambda_config.env:
                    continue

                alias_name = f'{fn_name}Alias{env.value.title()}'
                self.builder.resources[alias_name] = {
                    'Type': 'AWS::Lambda::Alias',
                    'Properties': {
                        'FunctionName': {'Ref': fn_name},
                        'FunctionVersion': '$LATEST',
                        'Name': env.value.lower()
                    }
                }

            # Create IAM role for Lambda (with permissions for ALL environment resources)
            self._create_lambda_role_multi_env(lambda_config, lambda_region, environments)

    def _create_lambda_role_multi_env(self, lambda_config: LambdaProperty, lambda_region, environments: list) -> None:
        """
        Create IAM role for Lambda function with permissions for ALL environment resources.

        Role includes:
        - Cognito permissions for CognitoTrigger Lambda
        - SQS permissions for dev, staging, AND prod queues (if configured)
        - S3 permissions for dev, staging, AND prod buckets (if configured)

        Args:
            lambda_config: Lambda configuration
            lambda_region: Lambda region configuration
            environments: List of ENVIRONMENT enums
        """
        role_name = self.builder.getLambdaRoleName(lambda_config.name)

        role = {
            'Type': 'AWS::IAM::Role',
            'Properties': {
                'RoleName': role_name,
                'AssumeRolePolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Principal': {'Service': 'lambda.amazonaws.com'},
                            'Action': 'sts:AssumeRole'
                        }
                    ]
                },
                'ManagedPolicyArns': [
                    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                ]
            }
        }

        # Add inline policies for SQS, S3, and Cognito access
        if lambda_config.name == LambdaName.CognitoTrigger:
            # Add Cognito-specific permissions for CognitoTrigger Lambda
            role['Properties']['Policies'] = [{
                'PolicyName': 'LambdaCognitoAccess',
                'PolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [{
                        'Effect': 'Allow',
                        'Action': [
                            'cognito-idp:AdminGetUser',
                            'cognito-idp:AdminDeleteUser',
                            'cognito-idp:ListUsers'
                        ],
                        'Resource': '*'
                    }]
                }
            }]
        else:
            # Collect queue and bucket ARNs for environments where this lambda is configured
            queue_arns = []
            bucket_names = []

            for env in environments:
                # Only add permissions for environments where this lambda is configured
                if env not in lambda_config.env:
                    continue

                env_builder = TemplateBuilder(env)

                # Add queue ARNs
                for q in lambda_region.queue:
                    queue_resource_name = env_builder.getQueueName(q.name, 'Q')
                    queue_arns.append({'Fn::GetAtt': [queue_resource_name, 'Arn']})

                # Add bucket names
                for s3 in lambda_region.s3:
                    bucket_names.append(env_builder.getBucketName(s3.name))

            # Add policies if we have queues or buckets
            if queue_arns or bucket_names:
                role['Properties']['Policies'] = []

            # Add SQS permissions
            if queue_arns:
                role['Properties']['Policies'].append({
                    'PolicyName': 'LambdaSQSAccess',
                    'PolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [{
                            'Effect': 'Allow',
                            'Action': [x.value for x in QueueRole.all()],
                            'Resource': queue_arns
                        }]
                    }
                })

            # Add S3 permissions
            if bucket_names:
                role['Properties']['Policies'].append({
                    'PolicyName': 'LambdaS3Access',
                    'PolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Action': [x.value for x in [S3Role.GetObject, S3Role.PutObject, S3Role.DeleteObject]],
                                'Resource': [{'Fn::Sub': f'arn:aws:s3:::{bucket}/*'} for bucket in bucket_names]
                            },
                            {
                                'Effect': 'Allow',
                                'Action': [S3Role.ListBucket.value],
                                'Resource': [{'Fn::Sub': f'arn:aws:s3:::{bucket}'} for bucket in bucket_names]
                            }
                        ]
                    }
                })

        self.builder.resources[role_name] = role
