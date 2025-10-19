from sam_deploy.config.mapping import Region, QueueName, LAMBDAS
from sam_deploy.builder.template_builder import TemplateBuilder
from dzgroshared.db.queue_messages.model import QueueMessageModelType
from sam_deploy.config.mapping import LambdaName
from dzgroshared.db.enums import ENVIRONMENT


class HttpApiBuilder:
    """
    Builds two separate HTTP APIs with different CORS configurations.

    Creates two HTTP APIs:
    1. API HTTP API - /api/{proxy+} with domain-specific CORS
    2. Webhook HTTP API - /webhook/rzrpay/{proxy+} with wildcard CORS

    This separation allows us to restrict API access to our domain while keeping webhooks open.
    """

    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def execute(self, api_certificate_arn: str, webhook_certificate_arn: str, region: Region):
        """
        Build both API and Webhook HTTP APIs.

        Args:
            api_certificate_arn: Certificate ARN for api domain
            webhook_certificate_arn: Certificate ARN for webhook domain
            region: AWS region to deploy to
        """
        self.build_api_http_api(api_certificate_arn, region)
        self.build_webhook_http_api(webhook_certificate_arn, region)

    def execute_with_multi_stage(self, all_certificates: dict, region: Region, environments: list):
        """
        Build HTTP APIs with 3 stages (dev, staging, prod) for single-stack architecture.

        Creates:
        - 1 API HttpApi resource (no StageName property)
        - 1 Webhook HttpApi resource (no StageName property)
        - 3 Stage resources per API (dev, staging, prod)
        - 3 DomainName resources per API type (api.dev.dzgro.com, api.staging.dzgro.com, api.dzgro.com)
        - 3 ApiMapping resources per API (linking domains to stages)
        - Lambda permissions for all alias invocations

        Args:
            all_certificates: Dictionary with structure {'Auth': {env: arn}, 'Api': {env: arn}, 'Webhook': {env: arn}}
            region: AWS region to deploy to
            environments: List of ENVIRONMENT enums (DEV, STAGING, PROD)
        """
        self.build_api_http_api_multi_stage(all_certificates, region, environments)
        self.build_webhook_http_api_multi_stage(all_certificates, region, environments)

    def build_api_http_api(self, api_certificate_arn: str, region: Region):
        """
        Build API HTTP API with domain-specific CORS.

        Route: /api/{proxy+} - Main API
        CORS: Restricted to application domain only
        Custom domain: api.{env}.dzgro.com (or api.dzgro.com for prod)
        Note: Lambda aliases are not used (AutoPublishAlias is commented out)

        Args:
            api_certificate_arn: Certificate ARN for custom domain
            region: AWS region
        """
        api_name = self.builder.getApiHttpApiName()
        api_function_name = self.builder.getFunctionName(LambdaName.Api)

        # Get environment-specific CORS origin
        cors_origin = f"https://{self.builder.envDomain()}"

        # Build API paths (only /api route)
        api_paths = self._build_api_paths(api_function_name)

        # Create HTTP API resource with domain-specific CORS
        # Note: We don't set StageName here because we create an explicit Stage resource below
        self.builder.resources[api_name] = {
            'Type': 'AWS::Serverless::HttpApi',
            'Properties': {
                'CorsConfiguration': {
                    'AllowOrigins': [cors_origin],  # Domain-specific for API security
                    'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                    'AllowHeaders': ['Content-Type', 'Authorization', 'Marketplace'],
                    'MaxAge': 300
                },
                'Tags': self.builder.getDictTag(),
                'DefinitionBody': {
                    'openapi': '3.0.1',
                    'info': {
                        'title': f'Dzgro {self.builder.envtextTitle} API',
                        'version': '1.0'
                    },
                    'paths': api_paths
                }
            }
        }

        # Add custom domain mapping
        self._add_api_domain_mapping(api_certificate_arn, api_name)

        # Add Lambda invoke permission
        self._add_api_lambda_permission(api_function_name, api_name)

    def build_webhook_http_api(self, webhook_certificate_arn: str, region: Region):
        """
        Build Webhook HTTP API with wildcard CORS.

        Route: /webhook/rzrpay/{proxy+} - Razorpay webhooks
        CORS: Wildcard (*) to allow external webhook calls
        Custom domain: webhook.{env}.dzgro.com (or webhook.dzgro.com for prod)

        Args:
            webhook_certificate_arn: Certificate ARN for custom domain
            region: AWS region
        """
        webhook_api_name = self.builder.getWebhookHttpApiName()
        webhook_function_name = self.builder.getFunctionName(LambdaName.RazorPayWebhook)

        # Build webhook paths
        webhook_paths = self._build_webhook_paths(webhook_function_name)

        # Create Webhook HTTP API resource with wildcard CORS
        # Note: We don't set StageName here because we create an explicit Stage resource below
        self.builder.resources[webhook_api_name] = {
            'Type': 'AWS::Serverless::HttpApi',
            'Properties': {
                'CorsConfiguration': {
                    'AllowOrigins': ['*'],  # Wildcard for external webhooks
                    'AllowMethods': ['POST'],
                    'AllowHeaders': ['Content-Type', 'X-Razorpay-Signature', 'x-razorpay-event-id'],
                    'MaxAge': 300
                },
                'Tags': self.builder.getDictTag(),
                'DefinitionBody': {
                    'openapi': '3.0.1',
                    'info': {
                        'title': f'Dzgro {self.builder.envtextTitle} Webhook API',
                        'version': '1.0'
                    },
                    'paths': webhook_paths
                }
            }
        }

        # Add custom domain mapping
        self._add_webhook_domain_mapping(webhook_certificate_arn, webhook_api_name)

        # Add Lambda invoke permission
        self._add_webhook_lambda_permission(webhook_api_name, webhook_function_name)

    def _build_api_paths(self, api_function_name: str) -> dict:
        """
        Build API route paths.

        Creates route for:
        - /api/{proxy+} - Main API

        Args:
            api_function_name: Name of the API Lambda function

        Returns:
            Dictionary of OpenAPI paths
        """
        return {
            '/api/{proxy+}': {
                'x-amazon-apigateway-any-method': {
                    'x-amazon-apigateway-integration': {
                        'type': 'aws_proxy',
                        'httpMethod': 'POST',
                        'uri': {
                            'Fn::Sub': [
                                f'arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{FunctionArn}}/invocations',
                                {
                                    'FunctionArn': {'Fn::GetAtt': [api_function_name, 'Arn']}
                                }
                            ]
                        },
                        'payloadFormatVersion': '2.0'
                    }
                }
            }
        }

    def _build_webhook_paths(self, webhook_function_name: str) -> dict:
        """
        Build webhook route paths.

        Creates route for:
        - /webhook/rzrpay/{proxy+} - Razorpay webhooks

        Args:
            webhook_function_name: Name of the RazorPayWebhook Lambda function

        Returns:
            Dictionary of OpenAPI paths
        """
        return {
            '/webhook/rzrpay/{proxy+}': {
                'post': {
                    'x-amazon-apigateway-integration': {
                        'type': 'aws_proxy',
                        'httpMethod': 'POST',
                        'uri': {
                            'Fn::Sub': [
                                f'arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{FunctionArn}}/invocations',
                                {
                                    'FunctionArn': {'Fn::GetAtt': [webhook_function_name, 'Arn']}
                                }
                            ]
                        },
                        'payloadFormatVersion': '2.0'
                    }
                }
            }
        }

    def _add_api_domain_mapping(self, certificate_arn: str, api_name: str):
        """
        Add custom domain and base path mapping for API HTTP API.

        Args:
            certificate_arn: ACM certificate ARN
            api_name: Name of the HTTP API resource
        """
        api_domain = self.builder.getApiDomainName()

        # Create API Domain
        self.builder.resources['ApiHttpApiDomain'] = {
            'Type': 'AWS::ApiGatewayV2::DomainName',
            'Properties': {
                'DomainName': api_domain,
                'DomainNameConfigurations': [
                    {
                        'CertificateArn': certificate_arn,
                        'EndpointType': 'REGIONAL'
                    }
                ],
                'Tags': self.builder.getDictTag()
            }
        }

        # Create explicit Stage resource (SAM auto-creates it but we need to reference it for ApiMapping)
        stage_name = f'{api_name}Stage'
        self.builder.resources[stage_name] = {
            'Type': 'AWS::ApiGatewayV2::Stage',
            'Properties': {
                'ApiId': {'Ref': api_name},
                'StageName': self.builder.envtextlower,
                'AutoDeploy': True
            }
        }

        # Create API Mapping
        self.builder.resources['ApiHttpApiMapping'] = {
            'Type': 'AWS::ApiGatewayV2::ApiMapping',
            'Properties': {
                'DomainName': {'Ref': 'ApiHttpApiDomain'},
                'ApiId': {'Ref': api_name},
                'Stage': {'Ref': stage_name}  # Reference the explicit stage
            }
        }

    def _add_webhook_domain_mapping(self, certificate_arn: str, webhook_api_name: str):
        """
        Add custom domain and base path mapping for Webhook HTTP API.

        Args:
            certificate_arn: ACM certificate ARN
            webhook_api_name: Name of the Webhook HTTP API resource
        """
        webhook_domain = self.builder.getWebhookDomainName()

        # Create Webhook Domain
        self.builder.resources['WebhookHttpApiDomain'] = {
            'Type': 'AWS::ApiGatewayV2::DomainName',
            'Properties': {
                'DomainName': webhook_domain,
                'DomainNameConfigurations': [
                    {
                        'CertificateArn': certificate_arn,
                        'EndpointType': 'REGIONAL'
                    }
                ],
                'Tags': self.builder.getDictTag()
            }
        }

        # Create explicit Stage resource for Webhook API
        webhook_stage_name = f'{webhook_api_name}Stage'
        self.builder.resources[webhook_stage_name] = {
            'Type': 'AWS::ApiGatewayV2::Stage',
            'Properties': {
                'ApiId': {'Ref': webhook_api_name},
                'StageName': self.builder.envtextlower,
                'AutoDeploy': True
            }
        }

        # Create Webhook Mapping
        self.builder.resources['WebhookHttpApiMapping'] = {
            'Type': 'AWS::ApiGatewayV2::ApiMapping',
            'Properties': {
                'DomainName': {'Ref': 'WebhookHttpApiDomain'},
                'ApiId': {'Ref': webhook_api_name},
                'Stage': {'Ref': webhook_stage_name}  # Reference the explicit stage
            }
        }

    def _add_api_lambda_permission(self, function_name: str, api_name: str):
        """
        Add Lambda permission for API Gateway to invoke the function.

        Args:
            function_name: Name of the Lambda function
            api_name: Name of the HTTP API
        """
        permission_name = f'ApiHttpApiInvokePermission{self.builder.envtextTitle}'

        self.builder.resources[permission_name] = {
            'Type': 'AWS::Lambda::Permission',
            'Properties': {
                'Action': 'lambda:InvokeFunction',
                'FunctionName': {'Ref': function_name},
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Sub': f'arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{{api_name}}}/*/*/*'
                }
            }
        }

    def _add_webhook_lambda_permission(self, webhook_api_name: str, function_name: str):
        """
        Add Lambda permission for Webhook API Gateway to invoke the RazorPayWebhook function.

        Args:
            webhook_api_name: Name of the Webhook HTTP API
            function_name: Name of the RazorPayWebhook Lambda function
        """
        permission_name = f'WebhookHttpApiInvokePermission{self.builder.envtextTitle}'

        self.builder.resources[permission_name] = {
            'Type': 'AWS::Lambda::Permission',
            'Properties': {
                'Action': 'lambda:InvokeFunction',
                'FunctionName': {'Ref': function_name},
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Sub': f'arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{{webhook_api_name}}}/*/*/*'
                }
            }
        }

    def build_api_http_api_multi_stage(self, all_certificates: dict, region: Region, environments: list):
        """
        Build API HTTP API with 3 stages for single-stack architecture.

        Creates:
        - 1 HTTP API with domain-specific CORS
        - 3 explicit Stage resources (dev, staging, prod)
        - 3 DomainName resources (api.dev.dzgro.com, api.staging.dzgro.com, api.dzgro.com)
        - 3 ApiMapping resources linking domains to stages
        - Lambda permissions for alias invocations

        Args:
            all_certificates: Dictionary with environment-specific certificates
            region: AWS region
            environments: List of ENVIRONMENT enums
        """
        api_name = self.builder.getApiHttpApiName()
        api_function_name = self.builder.getFunctionName(LambdaName.Api)

        # Get Api lambda configuration to check which environments are configured
        api_lambda_config = next((lc for lc in LAMBDAS if lc.name == LambdaName.Api), None)
        if not api_lambda_config:
            return

        # Build API paths (shared across all stages)
        # Lambda integration will use alias to route to correct environment
        api_paths = self._build_api_paths_with_alias(api_function_name)

        # Create HTTP API resource (no StageName property - stages created separately)
        # CORS is set to allow all environments (wildcard or specific domains)
        self.builder.resources[api_name] = {
            'Type': 'AWS::Serverless::HttpApi',
            'Properties': {
                'CorsConfiguration': {
                    'AllowOrigins': [
                        'https://dev.dzgro.com',
                        'https://staging.dzgro.com',
                        'https://dzgro.com'
                    ],
                    'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                    'AllowHeaders': ['Content-Type', 'Authorization', 'Marketplace'],
                    'MaxAge': 300
                },
                'Tags': self.builder.getDictTag(),
                'DefinitionBody': {
                    'openapi': '3.0.1',
                    'info': {
                        'title': 'Dzgro API',
                        'version': '1.0'
                    },
                    'paths': api_paths
                }
            }
        }

        # Create stages, domains, and mappings only for environments where Api lambda is configured
        for env in environments:
            # Only create stage if Api lambda is configured for this environment
            if env not in api_lambda_config.env:
                continue
            env_builder = TemplateBuilder(env)
            stage_name_value = env_builder.getApiStageName(env)
            stage_resource_name = f'{api_name}{env.value.title()}Stage'
            domain_resource_name = f'{api_name}{env.value.title()}Domain'
            mapping_resource_name = f'{api_name}{env.value.title()}Mapping'

            # Create Stage resource with stage variables for Lambda alias
            self.builder.resources[stage_resource_name] = {
                'Type': 'AWS::ApiGatewayV2::Stage',
                'Properties': {
                    'ApiId': {'Ref': api_name},
                    'StageName': stage_name_value,
                    'AutoDeploy': True,
                    'StageVariables': {
                        'lambdaAlias': env_builder.getLambdaAliasName(env)
                    }
                }
            }

            # Create DomainName resource with environment-specific certificate
            api_domain = env_builder.getApiDomainName()
            api_cert_arn = all_certificates['Api'][env.value]
            self.builder.resources[domain_resource_name] = {
                'Type': 'AWS::ApiGatewayV2::DomainName',
                'Properties': {
                    'DomainName': api_domain,
                    'DomainNameConfigurations': [
                        {
                            'CertificateArn': api_cert_arn,
                            'EndpointType': 'REGIONAL'
                        }
                    ],
                    'Tags': env_builder.getDictTag()
                }
            }

            # Create ApiMapping linking domain to stage
            self.builder.resources[mapping_resource_name] = {
                'Type': 'AWS::ApiGatewayV2::ApiMapping',
                'Properties': {
                    'DomainName': {'Ref': domain_resource_name},
                    'ApiId': {'Ref': api_name},
                    'Stage': {'Ref': stage_resource_name}
                }
            }

            # Add Lambda permission for this alias
            self._add_api_lambda_permission_for_alias(api_function_name, api_name, env)

    def build_webhook_http_api_multi_stage(self, all_certificates: dict, region: Region, environments: list):
        """
        Build Webhook HTTP API with 3 stages for single-stack architecture.

        Creates:
        - 1 HTTP API with wildcard CORS
        - 3 explicit Stage resources (dev, staging, prod)
        - 3 DomainName resources (webhook.dev.dzgro.com, webhook.staging.dzgro.com, webhook.dzgro.com)
        - 3 ApiMapping resources linking domains to stages
        - Lambda permissions for alias invocations

        Args:
            all_certificates: Dictionary with environment-specific certificates
            region: AWS region
            environments: List of ENVIRONMENT enums
        """
        webhook_api_name = self.builder.getWebhookHttpApiName()
        webhook_function_name = self.builder.getFunctionName(LambdaName.RazorPayWebhook)

        # Get RazorPayWebhook lambda configuration to check which environments are configured
        webhook_lambda_config = next((lc for lc in LAMBDAS if lc.name == LambdaName.RazorPayWebhook), None)
        if not webhook_lambda_config:
            return

        # Build webhook paths (shared across all stages)
        webhook_paths = self._build_webhook_paths_with_alias(webhook_function_name)

        # Create Webhook HTTP API resource with wildcard CORS
        self.builder.resources[webhook_api_name] = {
            'Type': 'AWS::Serverless::HttpApi',
            'Properties': {
                'CorsConfiguration': {
                    'AllowOrigins': ['*'],
                    'AllowMethods': ['POST'],
                    'AllowHeaders': ['Content-Type', 'X-Razorpay-Signature', 'x-razorpay-event-id'],
                    'MaxAge': 300
                },
                'Tags': self.builder.getDictTag(),
                'DefinitionBody': {
                    'openapi': '3.0.1',
                    'info': {
                        'title': 'Dzgro Webhook API',
                        'version': '1.0'
                    },
                    'paths': webhook_paths
                }
            }
        }

        # Create stages, domains, and mappings only for environments where RazorPayWebhook lambda is configured
        for env in environments:
            # Only create stage if RazorPayWebhook lambda is configured for this environment
            if env not in webhook_lambda_config.env:
                continue
            env_builder = TemplateBuilder(env)
            stage_name_value = env_builder.getApiStageName(env)
            stage_resource_name = f'{webhook_api_name}{env.value.title()}Stage'
            domain_resource_name = f'{webhook_api_name}{env.value.title()}Domain'
            mapping_resource_name = f'{webhook_api_name}{env.value.title()}Mapping'

            # Create Stage resource with stage variables for Lambda alias
            self.builder.resources[stage_resource_name] = {
                'Type': 'AWS::ApiGatewayV2::Stage',
                'Properties': {
                    'ApiId': {'Ref': webhook_api_name},
                    'StageName': stage_name_value,
                    'AutoDeploy': True,
                    'StageVariables': {
                        'lambdaAlias': env_builder.getLambdaAliasName(env)
                    }
                }
            }

            # Create DomainName resource with environment-specific certificate
            webhook_domain = env_builder.getWebhookDomainName()
            webhook_cert_arn = all_certificates['Webhook'][env.value]
            self.builder.resources[domain_resource_name] = {
                'Type': 'AWS::ApiGatewayV2::DomainName',
                'Properties': {
                    'DomainName': webhook_domain,
                    'DomainNameConfigurations': [
                        {
                            'CertificateArn': webhook_cert_arn,
                            'EndpointType': 'REGIONAL'
                        }
                    ],
                    'Tags': env_builder.getDictTag()
                }
            }

            # Create ApiMapping linking domain to stage
            self.builder.resources[mapping_resource_name] = {
                'Type': 'AWS::ApiGatewayV2::ApiMapping',
                'Properties': {
                    'DomainName': {'Ref': domain_resource_name},
                    'ApiId': {'Ref': webhook_api_name},
                    'Stage': {'Ref': stage_resource_name}
                }
            }

            # Add Lambda permission for this alias
            self._add_webhook_lambda_permission_for_alias(webhook_api_name, webhook_function_name, env)

    def _build_api_paths_with_alias(self, api_function_name: str) -> dict:
        """
        Build API route paths with Lambda alias support.

        Lambda integration URI will use stage variable to route to correct alias.
        Note: ${!stageVariables.lambdaAlias} uses ! to escape the $ so it's not replaced by Fn::Sub

        Args:
            api_function_name: Name of the API Lambda function (without alias)

        Returns:
            Dictionary of OpenAPI paths
        """
        return {
            '/api/{proxy+}': {
                'x-amazon-apigateway-any-method': {
                    'x-amazon-apigateway-integration': {
                        'type': 'aws_proxy',
                        'httpMethod': 'POST',
                        'uri': {
                            'Fn::Sub': [
                                f'arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{FunctionArn}}:${{!stageVariables.lambdaAlias}}/invocations',
                                {
                                    'FunctionArn': {'Fn::GetAtt': [api_function_name, 'Arn']}
                                }
                            ]
                        },
                        'payloadFormatVersion': '2.0'
                    }
                }
            }
        }

    def _build_webhook_paths_with_alias(self, webhook_function_name: str) -> dict:
        """
        Build webhook route paths with Lambda alias support.

        Lambda integration URI will use stage variable to route to correct alias.
        Note: ${!stageVariables.lambdaAlias} uses ! to escape the $ so it's not replaced by Fn::Sub

        Args:
            webhook_function_name: Name of the RazorPayWebhook Lambda function (without alias)

        Returns:
            Dictionary of OpenAPI paths
        """
        return {
            '/webhook/rzrpay/{proxy+}': {
                'post': {
                    'x-amazon-apigateway-integration': {
                        'type': 'aws_proxy',
                        'httpMethod': 'POST',
                        'uri': {
                            'Fn::Sub': [
                                f'arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{FunctionArn}}:${{!stageVariables.lambdaAlias}}/invocations',
                                {
                                    'FunctionArn': {'Fn::GetAtt': [webhook_function_name, 'Arn']}
                                }
                            ]
                        },
                        'payloadFormatVersion': '2.0'
                    }
                }
            }
        }

    def _add_api_lambda_permission_for_alias(self, function_name: str, api_name: str, env: ENVIRONMENT):
        """
        Add Lambda permission for API Gateway to invoke a specific alias.

        Args:
            function_name: Name of the Lambda function
            api_name: Name of the HTTP API
            env: Environment (for alias name)
        """
        env_builder = TemplateBuilder(env)
        alias_name = env_builder.getLambdaAliasName(env)
        alias_resource_name = f'{function_name}Alias{env.value.title()}'
        permission_name = f'ApiHttpApiInvokePermission{env.value.title()}'

        self.builder.resources[permission_name] = {
            'Type': 'AWS::Lambda::Permission',
            'Properties': {
                'Action': 'lambda:InvokeFunction',
                'FunctionName': {'Ref': alias_resource_name},
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Sub': f'arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{{api_name}}}/*/*/*'
                }
            }
        }

    def _add_webhook_lambda_permission_for_alias(self, webhook_api_name: str, function_name: str, env: ENVIRONMENT):
        """
        Add Lambda permission for Webhook API Gateway to invoke a specific alias.

        Args:
            webhook_api_name: Name of the Webhook HTTP API
            function_name: Name of the RazorPayWebhook Lambda function
            env: Environment (for alias name)
        """
        env_builder = TemplateBuilder(env)
        alias_name = env_builder.getLambdaAliasName(env)
        alias_resource_name = f'{function_name}Alias{env.value.title()}'
        permission_name = f'WebhookHttpApiInvokePermission{env.value.title()}'

        self.builder.resources[permission_name] = {
            'Type': 'AWS::Lambda::Permission',
            'Properties': {
                'Action': 'lambda:InvokeFunction',
                'FunctionName': {'Ref': alias_resource_name},
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Sub': f'arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{{webhook_api_name}}}/*/*/*'
                }
            }
        }
