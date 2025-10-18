from sam_deploy.config.mapping import ENVIRONMENT, Region, QueueName
from sam_deploy.builder.template_builder import TemplateBuilder
from dzgroshared.db.queue_messages.model import QueueMessageModelType
from sam_deploy.config.mapping import LambdaName


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
