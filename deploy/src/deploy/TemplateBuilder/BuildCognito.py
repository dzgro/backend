from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import LambdaName
from dzgroshared.db.enums import ENVIRONMENT

class CognitoBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder
        
    def execute(self):
        domain = self.builder.envDomain()
        resource =  {
            "UserPool": {
              "Type": "AWS::Cognito::UserPool",
              "Properties": {
                "UserPoolName": self.builder.getUserPoolName(),
                "AutoVerifiedAttributes": ["email"],
                "LambdaConfig": {
                  "CustomMessage": { "Fn::GetAtt": [self.builder.getFunctionName(LambdaName.CognitoCustomMessage), "Arn"] },
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
                "CallbackURLs": [
                    f"https://{domain}/sign-in-callback"
                ],
                "LogoutURLs": [
                    f"https://{domain}/logout"
                ],
                "SupportedIdentityProviders": ["COGNITO"]
              }
            },
            "LambdaInvokePermissionCustomMessage": {
              "Type": "AWS::Lambda::Permission",
              "Properties": {
                "FunctionName": { "Ref": self.builder.getFunctionName(LambdaName.CognitoCustomMessage) },
                "Action": "lambda:InvokeFunction",
                "Principal": "cognito-idp.amazonaws.com",
                "SourceArn": { "Fn::GetAtt": ["UserPool", "Arn"] }
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
            }
          }
        self.builder.resources.update(resource)
