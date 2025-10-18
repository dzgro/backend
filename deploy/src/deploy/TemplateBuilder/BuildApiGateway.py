
from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import LambdaName


class ApiGatewayBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def execute(self, apiCertificateArn: str):
        self.createApiGatewayRole()
        self.createRawApiGateway()
        self.addCertificateAndBaseMapping(apiCertificateArn)

    def addCertificateAndBaseMapping(self, ApiCertificateArn: str):
        apiDomain = self.builder.getApiDomainName()
        self.builder.resources.update(
            {
            'ApiDomain': {
                "Type": "AWS::ApiGateway::DomainName",
                "Properties": {
                    "DomainName": apiDomain,
                    "RegionalCertificateArn": ApiCertificateArn,
                    "EndpointConfiguration": {
                        "Types": ["REGIONAL"]
                    }
                }
            },
            "MyBasePathMapping": {
                "Type": "AWS::ApiGateway::BasePathMapping",
                "Properties": {
                    "DomainName": { "Ref": "ApiDomain" },
                    "RestApiId": { "Ref": self.builder.getApiGatewayName() },
                    "Stage": {"Ref": f'{self.builder.getApiGatewayName()}.Stage' }
                }
            }
            }
      )


    def createApiGatewayRole(self):
        rolename: str = self.builder.getApiGatewayRoleName()
        role = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": rolename,
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": { "Service": "apigateway.amazonaws.com" },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                },
                "Policies": [
                    {
                        "PolicyName": f"ApiGateway{self.builder.env.value}SQSAccess",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "sqs:SendMessage",
                                    "Resource": { "Fn::Sub": f"arn:aws:sqs:${{AWS::Region}}:${{AWS::AccountId}}:*{self.builder.env.value.title()}Q" }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.builder.resources[rolename] = role
        apiGatewayName = self.builder.getApiGatewayName()
        self.builder.resources[f'ApiGatewayInvokePermission{self.builder.env.value}'] = {
            "Type": "AWS::Lambda::Permission",
            "Properties": {
                "Action": "lambda:InvokeFunction",
                "FunctionName": {
                    "Ref": self.builder.getFunctionName(LambdaName.Api)
                },
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Join": [
                    "",
                    [
                        "arn:aws:execute-api:",
                        { "Ref": "AWS::Region" },
                        ":",
                        { "Ref": "AWS::AccountId" },
                        ":",
                        { "Ref": apiGatewayName },
                        "/*/*/*"
                    ]
                    ]
                },
            }
        }

    def createRawApiGateway(self):
        self.builder.resources[self.builder.getApiGatewayName()] = {
            'Type': 'AWS::Serverless::Api', 
            'Properties': { 
                'StageName': self.builder.envtextlower,
                "Cors": {
                    "AllowMethods": "'OPTIONS,GET,POST,PUT,DELETE'",
                    "AllowHeaders": "'Content-Type,Authorization,Marketplace'",
                    "AllowOrigin": "'*'"
                },
                'EndpointConfiguration': 'REGIONAL',
                'Tags': self.builder.getDictTag(),
                'DefinitionBody': { 
                    'openapi': '3.0.1', 
                    'info': {
                        'title': f'Dzgro {self.builder.env.value} API', 'version': '1.0'
                    }, 
                    'paths': {} 
                } 
            } 
        }