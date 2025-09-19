from deploy.TemplateBuilder.Builder import TemplateBuilder
from dzgroshared.db.enums import ENVIRONMENT


class CertificateBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def execute(self, AuthCertificateArn: str):
        authDomain = self.builder.getAuthDomainName()
        apiDomain = self.builder.getApiDomainName()
        resource: dict = {
            'ApiDomain': {
                "Type": "AWS::ApiGateway::DomainName",
                "Properties": {
                    "DomainName": apiDomain,
                    "RegionalCertificateArn": { "Ref": "ApiCertificate" },
                    "EndpointConfiguration": {
                        "Types": ["REGIONAL"]
                    }
                }
            },
            "AuthDomain": {
                "Type": "AWS::Cognito::UserPoolDomain",
                "Properties": {
                    "Domain": authDomain,
                    "UserPoolId": { "Ref": "UserPool" },
                    "CustomDomainConfig": {
                    "CertificateArn": AuthCertificateArn
                    }
                }
            },
            "MyBasePathMapping": {
                "Type": "AWS::ApiGateway::BasePathMapping",
                "Properties": {
                    "DomainName": { "Ref": "ApiDomain" },
                    "RestApiId": { "Ref": self.builder.getApiGatewayName() },
                    "Stage": self.builder.envtextlower
                }
            }
        }
        self.builder.resources.update(resource)