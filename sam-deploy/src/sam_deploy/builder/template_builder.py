from typing import Literal
from dzgroshared.sqs.model import QueueName
from dzgroshared.storage.model import S3Bucket
from sam_deploy.config.mapping import Region, LambdaName, Tag
from dzgroshared.db.enums import ENVIRONMENT
import os, boto3


class TemplateBuilder:
    env: ENVIRONMENT
    envtextlower: str
    envtextTitle: str
    resources: dict[str, dict] = {}
    is_default_region: bool
    lambdaRoleName: str = 'DzgroLambdaRole'
    apigateway: dict

    def __init__(self, env: ENVIRONMENT = None) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        from dzgroshared.db.enums import ENVIRONMENT, CountryCode
        # Allow env to be passed in, otherwise read from ENV variable
        if env is None:
            env = ENVIRONMENT(os.getenv("ENV", None))
            if not env: raise ValueError("ENV environment variable not set")
        self.env = env
        self.envtextlower = env.value
        self.envtextTitle = env.value.title()

    def getWildCardCertificateArn(self, type: Literal['Auth', 'Api', 'Webhook']) -> str:
        """Create/retrieve certificate ARN via boto3
        - Auth: us-east-1 (Cognito requirement)
        - Api: region-specific
        - Webhook: region-specific
        """
        region = 'us-east-1' if type == 'Auth' else Region.DEFAULT.value
        acm = boto3.client("acm", region_name=region)
        certificates = acm.list_certificates(CertificateStatuses=['PENDING_VALIDATION', 'ISSUED', 'INACTIVE', 'EXPIRED', 'VALIDATION_TIMED_OUT', 'REVOKED', 'FAILED'])
        domain = self.getDomainNameByType(type)
        status, arn = None, None
        for cert in certificates['CertificateSummaryList']:
            if cert['DomainName'] == domain:
                status, arn = cert['Status'], cert['CertificateArn']
        if not arn:
            certificate = acm.request_certificate(
                DomainName=domain,
                ValidationMethod="DNS",
                Tags=self.getListTag()
            )
            status, arn = 'PENDING_VALIDATION', certificate['CertificateArn']
        while status!='ISSUED':
            print(f"Current status of {type} Certificate for {domain} is {status}")
            import time
            time.sleep(15)
            detail = acm.describe_certificate(CertificateArn=arn)
            status = detail['Certificate']['Status']
            if status!='PENDING_VALIDATION' and status!='ISSUED':
                raise Exception(f"Certificate {arn} for {type} in {region} failed with status {status}")
        return arn

    def getAssets(self):
        import base64
        import os
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        def file_to_bytes(filename):
            with open(os.path.join(images_dir, filename), 'rb') as f:
                return f.read()

        assets = [
            {
                'Category': 'PAGE_HEADER_LOGO',
                'ColorMode': 'LIGHT',
                'Extension': 'PNG',
                'Bytes': file_to_bytes('dzgro-logo.png'),
            },
            {
                'Category': 'FAVICON_ICO',
                'ColorMode': 'LIGHT',
                'Extension': 'ICO',
                'Bytes': file_to_bytes('dzgro-ico.ico'),
            },
            {
                'Category': 'PAGE_HEADER_BACKGROUND',
                'ColorMode': 'LIGHT',
                'Extension': 'PNG',
                'Bytes': file_to_bytes('cognito-bg.png'),
            },
        ]
        return assets

    def createUserPoolDomain(self, region: Region, authCertificateArn: str):
        idp = boto3.client("cognito-idp", region_name=region.value)
        from botocore.exceptions import ClientError
        domain = self.getAuthDomainName()
        userPools = idp.list_user_pools(MaxResults=60)
        userPoolId = None
        for pool in userPools['UserPools']:
            if pool['Name'] == self.getUserPoolName():
                userPoolId = pool['Id']
        if userPoolId:
            try:
                desc = idp.describe_user_pool_domain(Domain=domain)
                if desc['DomainDescription']:
                    state = desc['DomainDescription']['Status']
                    print('*' * 30)
                    print(desc['DomainDescription']['CloudFrontDistribution'])
                    print(state)
                    print(f"Create CNAME entry in your DNS for the following domain: {domain.replace(f'.{self.envDomain()}','')}")
                    print('*' * 30)
                else:
                    response = idp.create_user_pool_domain(
                        Domain=domain,
                        UserPoolId=userPoolId,
                        ManagedLoginVersion=2,
                        CustomDomainConfig={
                            "CertificateArn": authCertificateArn
                        }
                    )
                    state = 'CREATING'
                    print('*' * 30)
                    print(f"Created User Pool Domain {domain} with CloudFrontDistribution {response['CloudFrontDomain']}")
                    print('*' * 30)
                while state=='CREATING' or state!='ACTIVE':
                    import time
                    time.sleep(15)
                    desc = idp.describe_user_pool_domain(Domain=domain)
                    state = desc['DomainDescription']['Status']
                    print(f"Current status of User Pool Domain {domain} is {state}")
                    # print(f'Current State: {state}')
                if state=='ACTIVE':
                    response = idp.list_user_pool_clients(
                        UserPoolId=userPoolId,
                        MaxResults=10,
                    )
                    clientId = next((client['ClientId'] for client in response['UserPoolClients'] if client['ClientName']==self.getUserPoolClientName()), None)
                    if not clientId: raise Exception(f"User Pool Client {self.getUserPoolClientName()} not found in User Pool {self.getUserPoolName()}")


                    try:
                        response = idp.describe_managed_login_branding_by_client(
                            UserPoolId=userPoolId,
                            ClientId=clientId,
                            ReturnMergedResources=True
                        )
                        print(f"Managed Login Branding already exists as {response['ManagedLoginBranding']['ManagedLoginBrandingId']}")
                        response = idp.update_managed_login_branding(
                            UserPoolId=userPoolId,
                            ManagedLoginBrandingId=response['ManagedLoginBranding']['ManagedLoginBrandingId'],
                            UseCognitoProvidedValues=True,
                            Assets=self.getAssets()
                        )
                    except idp.exceptions.ResourceNotFoundException:
                        response = idp.create_managed_login_branding(
                            UserPoolId=userPoolId,
                            ClientId=clientId,
                            UseCognitoProvidedValues=True,
                            Assets=self.getAssets()
                        )
                    print(f"Created Managed Login Branding as {response['ManagedLoginBranding']['ManagedLoginBrandingId']}")



            except ClientError as e:
                print(f"Error creating User Pool Domain {domain}: {e}")
                raise e
            except Exception as e:
                print(f"Unexpected error creating User Pool Domain {domain}: {e}")
                raise e
        else:
            raise Exception(f"User Pool {self.getUserPoolName()} not found in {region.value}")

    def getUserPoolClientName(self):
        return f"Dzgro{self.envtextTitle}Client"

    def rootDomain(self):
        return "dzgro.com"

    def envDomain(self):
        if self.env==ENVIRONMENT.PROD: return self.rootDomain()
        return f'{self.envtextlower}.{self.rootDomain()}'

    def getDomainNameByType(self, type: Literal['Auth', 'Api', 'Webhook']):
        """Generate domain name based on type and environment"""
        prefix = type.lower()
        if self.env == ENVIRONMENT.PROD:
            return f"{prefix}.dzgro.com"
        else:
            return f"{prefix}.{self.envtextlower}.dzgro.com"

    def getAuthDomainName(self):
        return self.getDomainNameByType('Auth')

    def getApiDomainName(self):
        return self.getDomainNameByType('Api')

    def getWebhookDomainName(self) -> str:
        """Returns webhook.{env}.dzgro.com"""
        return self.getDomainNameByType('Webhook')

    def getLambdaRoleName(self, name: LambdaName):
        """Returns Lambda role name WITHOUT environment suffix"""
        return f'{name.value}LambdaRole'

    def getUserPoolName(self):
        return f'DzgroUserPool{self.envtextTitle}'

    def getApiGatewayRoleName(self):
        return f'ApiGatewayRole{self.envtextTitle}'

    def getApiGatewayName(self):
        """Returns API Gateway name WITHOUT environment suffix"""
        return 'ApiGateway'

    def getBucketName(self, name: S3Bucket):
        return f'{name.value}-{self.envtextlower}'

    def getBucketResourceName(self, name: S3Bucket):
        return f'{name.value.replace("-", " ").title().replace(" ", "")}{self.envtextTitle}Bucket'

    def getFunctionName(self, name: LambdaName):
        """Returns Lambda function name WITHOUT environment suffix"""
        return f'{name.value}Function'

    def getQueueName(self, name: QueueName, type: Literal['Q','DLQ','EventSourceMapping']):
        return f'{name.value}{self.envtextTitle}{type}'

    def getDictTag(self):
        return {k:v for k,v in Tag(Environment=self.env).model_dump(mode="json").items() }

    def getListTag(self):
        return [{"Key": k, "Value": v} for k, v in Tag(Environment=self.env).model_dump(mode="json").items()]

    def createDLQ(self, name:str):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'Tags': self.getListTag() } }

    def createQ(self, name:str, dlq: str):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'RedrivePolicy': { 'deadLetterTargetArn': {'Fn::GetAtt': [dlq, 'Arn']}, 'maxReceiveCount': 1 }, 'Tags': self.getListTag() } }

    def createQEventMapping(self, q:str, functionName: str):
        return { 'Type': 'AWS::Lambda::EventSourceMapping', 'Properties': { 'EventSourceArn': {'Fn::GetAtt': [q, 'Arn']}, 'FunctionName': {'Ref': functionName} } }

    def getLambdaAliasName(self, env: ENVIRONMENT) -> str:
        """Returns alias name: 'dev', 'staging', 'prod'"""
        return env.value.lower()

    def getApiStageName(self, env: ENVIRONMENT) -> str:
        """Returns stage name: 'dev', 'staging', 'prod'"""
        return env.value.lower()

    def getLambdaArnWithAlias(self, function_name: str, alias: str) -> dict:
        """Helper for Lambda ARN with alias"""
        return {'Fn::Sub': f'${{{{{AWS::AccountId}}}}}/${{{{{AWS::Region}}}}}/functions/{function_name}:{alias}'}

    def getApiHttpApiName(self) -> str:
        """Name for API HTTP API"""
        return 'ApiHttpApi'

    def getWebhookHttpApiName(self) -> str:
        """Name for Webhook HTTP API"""
        return 'WebhookHttpApi'
