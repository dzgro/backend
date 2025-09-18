
from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import LambdaName


class ApiGatewayBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def execute(self):
        self.createApiGatewayRole()
        self.createRawApiGateway()


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
                                    "Resource": { "Fn::Sub": f"arn:aws:sqs:${{AWS::Region}}:${{AWS::AccountId}}:*{self.builder.env.value}Q" }
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
                    "Fn::Sub": f"arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:{apiGatewayName}/*/*/*"
                }
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