from sam_deploy.config.mapping import ENVIRONMENT, Region, LambdaName
from sam_deploy.builder.template_builder import TemplateBuilder


class CognitoBuilder:
    """
    Builder for AWS Cognito User Pool resources.

    Creates Cognito User Pools with:
    - Lambda triggers for custom authentication flows
    - Custom domain with ACM certificate
    - OAuth 2.0 and hosted UI configuration
    - Resource server with scopes
    - User pool client for application integration

    Note: User Pool Domain creation is handled separately via boto3
    in TemplateBuilder.createUserPoolDomain() (not in SAM template).
    """

    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        """
        Initialize CognitoBuilder with TemplateBuilder instance.

        Args:
            builder: TemplateBuilder instance containing environment configuration
        """
        self.builder = builder

    def build_user_pool(self, auth_certificate_arn: str) -> None:
        """
        Build Cognito User Pool with Lambda triggers and email configuration.

        Creates a User Pool with:
        - Auto-verified email attributes
        - Lambda triggers for PreSignUp, CustomMessage, PostConfirmation, PreTokenGeneration
        - SES email configuration using the root domain
        - Schema for email, phone_number, and name attributes
        - Email-based username authentication

        Args:
            auth_certificate_arn: ARN of ACM certificate for custom domain (us-east-1)
        """
        # Use environment-specific resource names
        user_pool_resource_name = f"UserPool{self.builder.envtextTitle}"
        cognito_trigger_function_name = self.builder.getFunctionName(LambdaName.CognitoTrigger)
        # For multi-env setup, use environment-specific aliases
        cognito_trigger_alias_name = f"{cognito_trigger_function_name}Alias{self.builder.envtextTitle}"

        resource = {
            user_pool_resource_name: {
                "Type": "AWS::Cognito::UserPool",
                "Properties": {
                    "UserPoolName": self.builder.getUserPoolName(),
                    "AutoVerifiedAttributes": ["email"],
                    "LambdaConfig": {
                        "PreSignUp": {"Ref": cognito_trigger_alias_name},
                        "CustomMessage": {"Ref": cognito_trigger_alias_name},
                        "PostConfirmation": {"Ref": cognito_trigger_alias_name},
                        "PreTokenGenerationConfig": {
                            "LambdaArn": {"Ref": cognito_trigger_alias_name},
                            "LambdaVersion": "V2_0"
                        }
                    },
                    "EmailConfiguration": {
                        "EmailSendingAccount": "DEVELOPER",
                        "SourceArn": {"Fn::Sub": f"arn:aws:ses:${{AWS::Region}}:${{AWS::AccountId}}:identity/{self.builder.rootDomain()}"},
                        "From": f"onboarding@{self.builder.rootDomain()}"
                    },
                    "Schema": [
                        {
                            "Name": "email",
                            "AttributeDataType": "String",
                            "Required": True
                        },
                        {
                            "Name": "phone_number",
                            "AttributeDataType": "String",
                            "Required": True
                        },
                        {
                            "Name": "name",
                            "AttributeDataType": "String",
                            "Required": True
                        },
                    ],
                    "UsernameAttributes": ["email"],
                }
            },
            f"LambdaInvokePermissionCognitoTrigger{self.builder.envtextTitle}": {
                "Type": "AWS::Lambda::Permission",
                "Properties": {
                    "FunctionName": {"Ref": cognito_trigger_alias_name},
                    "Action": "lambda:InvokeFunction",
                    "Principal": "cognito-idp.amazonaws.com",
                    "SourceArn": {"Fn::GetAtt": [user_pool_resource_name, "Arn"]}
                }
            }
            # Note: IAM role is created by Lambda builder
            # Cognito-specific permissions are added via managed policy in Lambda builder's _create_lambda_role
        }
        self.builder.resources.update(resource)

    def build_user_pool_client(self) -> None:
        """
        Build Cognito User Pool Client for application integration.

        Creates a User Pool Client with:
        - OAuth 2.0 authorization code flow
        - OpenID Connect scopes (email, openid, phone, profile)
        - Custom resource server scopes
        - Callback and logout URLs for hosted UI
        - DEV environment includes localhost URLs for local development
        """
        domain = self.builder.envDomain()
        callback_urls = [f"https://{domain}/sign-in-callback"]
        logout_urls = [f"https://{domain}/login"]

        # Add localhost URLs for DEV environment
        if self.builder.env == ENVIRONMENT.DEV:
            callback_urls.append("http://localhost:4200/sign-in-callback")
            logout_urls.append("http://localhost:4200/login")

        # Use environment-specific resource names
        user_pool_resource_name = f"UserPool{self.builder.envtextTitle}"
        user_pool_client_resource_name = f"UserPoolClient{self.builder.envtextTitle}"
        resource_server_resource_name = f"UserPoolResourceServer{self.builder.envtextTitle}"

        resource = {
            user_pool_client_resource_name: {
                "Type": "AWS::Cognito::UserPoolClient",
                "Properties": {
                    "UserPoolId": {"Ref": user_pool_resource_name},
                    "ClientName": self.builder.getUserPoolClientName(),
                    "GenerateSecret": False,
                    "AllowedOAuthFlowsUserPoolClient": True,
                    "AllowedOAuthFlows": ["code"],
                    "AllowedOAuthScopes": [
                        "email",
                        "openid",
                        "phone",
                        "profile",
                        {"Fn::Join": ["", [{"Ref": resource_server_resource_name}, "/read"]]}
                    ],
                    "CallbackURLs": callback_urls,
                    "LogoutURLs": logout_urls,
                    "SupportedIdentityProviders": ["COGNITO"]
                }
            }
        }
        self.builder.resources.update(resource)

    def build_user_pool_resource_server(self) -> None:
        """
        Build Cognito User Pool Resource Server with custom scopes.

        Creates a resource server with:
        - Identifier: 'dzgro'
        - Custom scope: 'read' for read access to Dzgro data

        These scopes can be used in OAuth 2.0 flows for fine-grained access control.
        """
        # Use environment-specific resource names
        user_pool_resource_name = f"UserPool{self.builder.envtextTitle}"
        resource_server_resource_name = f"UserPoolResourceServer{self.builder.envtextTitle}"

        resource = {
            resource_server_resource_name: {
                "Type": "AWS::Cognito::UserPoolResourceServer",
                "Properties": {
                    "Identifier": "dzgro",
                    "Name": "Dzgro Resource Server",
                    "UserPoolId": {"Ref": user_pool_resource_name},
                    "Scopes": [
                        {
                            "ScopeName": "read",
                            "ScopeDescription": "Read access to Dzgro data"
                        }
                    ]
                }
            }
        }
        self.builder.resources.update(resource)

    def execute(self, auth_certificate_arn: str) -> None:
        """
        Build complete Cognito User Pool setup.

        Creates all Cognito resources in the correct order:
        1. User Pool with Lambda triggers and email configuration
        2. Resource Server with custom scopes
        3. User Pool Client with OAuth configuration

        Note: User Pool Domain creation is handled separately via boto3
        in TemplateBuilder.createUserPoolDomain() after SAM deployment.

        Skips Cognito setup for LOCAL environment as it's not needed
        for local development.

        Args:
            auth_certificate_arn: ARN of ACM certificate in us-east-1 for custom domain
        """
        if self.builder.env == ENVIRONMENT.LOCAL:
            return  # Skip Cognito for LOCAL environment

        self.build_user_pool(auth_certificate_arn)
        self.build_user_pool_resource_server()
        self.build_user_pool_client()
