from deploy.TemplateBuilder.Builder import TemplateBuilder


class CognitoCertBuilder:

    def __init__(self, builder: TemplateBuilder):
        self.builder = builder


    def execute(self):
        domain = self.builder.getDomain()
        self.builder.resources.update({
            'AuthCertificate': {
                "Type": "AWS::CertificateManager::Certificate",
                "Properties": {
                    "DomainName": f"auth.{domain}",
                    "ValidationMethod": "DNS"
                }
            },
            "AuthDomain": {
                "Type": "AWS::Cognito::UserPoolDomain",
                "Properties": {
                    "Domain": f"auth.{domain}",
                    "UserPoolId": { "Ref": "UserPool" },
                    "CustomDomainConfig": {
                    "CertificateArn": { "Ref": "AuthCertificate" }
                    }
                },
                "DependsOn": ["AuthCertificate"]
            },
        })