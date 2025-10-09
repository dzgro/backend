from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import LambdaName
from dzgroshared.db.enums import ENVIRONMENT

class CognitoBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder
        
    def execute(self):
        domain = self.builder.envDomain()
        callbackUrls = [f"https://{domain}/sign-in-callback"]
        logoutUrls = [f"https://{domain}/login"]
        if self.builder.env==ENVIRONMENT.DEV:
            callbackUrls.append("http://localhost:4200/sign-in-callback")
            logoutUrls.append("http://localhost:4200/login")
        resource =  {
            "UserPool": {
              "Type": "AWS::Cognito::UserPool",
              "Properties": {
                "UserPoolName": self.builder.getUserPoolName(),
                "AutoVerifiedAttributes": ["email"],
                "LambdaConfig": {
                  "PreSignUp": { "Fn::GetAtt": [self.builder.getFunctionName(LambdaName.CognitoTrigger), "Arn"] },
                  "CustomMessage": { "Fn::GetAtt": [self.builder.getFunctionName(LambdaName.CognitoTrigger), "Arn"] },
                  "PostConfirmation": { "Fn::GetAtt": [self.builder.getFunctionName(LambdaName.CognitoTrigger), "Arn"] },
                  "PreTokenGenerationConfig": {
                    "LambdaArn": { "Fn::GetAtt": [self.builder.getFunctionName(LambdaName.CognitoTrigger), "Arn"] },
                    "LambdaVersion": "V2_0"
                  }
                },
                "EmailConfiguration": {
                  "EmailSendingAccount": "DEVELOPER",
                  "SourceArn": { "Fn::Sub": f"arn:aws:ses:${{AWS::Region}}:${{AWS::AccountId}}:identity/{self.builder.rootDomain()}" },
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
                "AutoVerifiedAttributes": ["email"]

              }
            },
            "UserPoolResourceServer": {
              "Type": "AWS::Cognito::UserPoolResourceServer",
              "Properties": {
                "Identifier": "dzgro",
                "Name": "Dzgro Resource Server",
                "UserPoolId": { "Ref": "UserPool" },
                "Scopes": [
                  {
                    "ScopeName": "read",
                    "ScopeDescription": "Read access to Dzgro data"
                  }
                ]
              }
            },
            "UserPoolClient": {
              "Type": "AWS::Cognito::UserPoolClient",
              "Properties": {
                "UserPoolId": { "Ref": "UserPool" },
                "ClientName": self.builder.getUserPoolClientName(),
                "GenerateSecret": False,
                "AllowedOAuthFlowsUserPoolClient": True,
                "AllowedOAuthFlows": ["code"],
                "AllowedOAuthScopes": [
                  "email",
                  "openid",
                  "phone",
                  "profile",
                  { "Fn::Join": [ "", [ { "Ref": "UserPoolResourceServer" }, "/read" ] ] }
                ],
                "CallbackURLs": callbackUrls,
                "LogoutURLs": logoutUrls,
                "SupportedIdentityProviders": ["COGNITO"]
              }
            },
            "LambdaInvokePermissionCognitoTrigger": {
              "Type": "AWS::Lambda::Permission",
              "Properties": {
                "FunctionName": { "Ref": self.builder.getFunctionName(LambdaName.CognitoTrigger) },
                "Action": "lambda:InvokeFunction",
                "Principal": "cognito-idp.amazonaws.com",
                "SourceArn": { "Fn::GetAtt": ["UserPool", "Arn"] }
              }
            },
            self.builder.getLambdaRoleName(LambdaName.CognitoTrigger): {
              "Type": "AWS::IAM::Role",
              "Properties": {
                "RoleName": self.builder.getLambdaRoleName(LambdaName.CognitoTrigger),
                "AssumeRolePolicyDocument": {
                  "Version": "2012-10-17",
                  "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                  }]
                },
                "ManagedPolicyArns": ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],
                "Policies": [{
                  "PolicyName": "LambdaCognitoAccess",
                  "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [{
                      "Effect": "Allow",
                      "Action": ["cognito-idp:AdminGetUser", "cognito-idp:AdminDeleteUser", "cognito-idp:ListUsers"],
                      "Resource": "*"
                    }]
                  }
                }]
              }
            }
          }
        self.builder.resources.update(resource)
