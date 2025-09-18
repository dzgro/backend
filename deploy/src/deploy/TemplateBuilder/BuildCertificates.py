from deploy.TemplateBuilder.Builder import TemplateBuilder
from dzgroshared.db.enums import ENVIRONMENT


class CertificateBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def execute(self):
        domain = self.builder.getDomain()
        resource: dict = {
            'ApiCertificate': {
                "Type": "AWS::CertificateManager::Certificate",
                "Properties": {
                    "DomainName": f"api.{domain}",
                    "ValidationMethod": "DNS"
                }
            },
            'ApiDomain': {
                "Type": "AWS::ApiGateway::DomainName",
                "Properties": {
                    "DomainName": f'api.{domain}',
                    "RegionalCertificateArn": { "Ref": "ApiCertificate" },
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
                    "Stage": self.builder.envtextlower
                }
            }
        }
        self.builder.resources.update(resource)