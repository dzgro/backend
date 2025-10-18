from sam_deploy.config.mapping import LambdaName, ENVIRONMENT, LambdaProperty, LAMBDAS, Region, QueueProperty, QueueRole, S3Property, S3Role
from sam_deploy.builder.template_builder import TemplateBuilder
from typing import Dict


class LambdaBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

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
            # 'AutoPublishAlias': 'dev'  # Auto-publish to DEV alias - TODO: Fix and re-enable later
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
        if self.builder.env != ENVIRONMENT.LOCAL:
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

        # Add inline policies for SQS and S3 access
        if lambda_config.name != LambdaName.CognitoTrigger:
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
