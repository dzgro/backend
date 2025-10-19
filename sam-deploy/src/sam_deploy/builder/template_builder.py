from typing import Literal, Optional
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

    def __init__(self, env: Optional[ENVIRONMENT] = None) -> None:
        from dzgroshared.db.enums import ENVIRONMENT, CountryCode

        # Only load .env if env is not provided
        if env is None:
            from dotenv import load_dotenv
            load_dotenv()
            env = ENVIRONMENT(os.getenv("ENV", None))
            if not env:
                raise ValueError("ENV environment variable not set")

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

    @staticmethod
    def getWildCardCertificateArnsForAllEnvironments(environments: list, region = None) -> dict:
        """
        Create/retrieve certificates for all environments simultaneously.

        This method:
        1. Creates certificate requests for all environments (dev, staging, prod) at once
        2. Polls all certificates together until ALL are issued
        3. Logs status of all certificates during polling

        Args:
            environments: List of ENVIRONMENT enums (e.g., [DEV, STAGING, PROD])
            region: AWS region for API and Webhook certificates (default: ap-south-1)

        Returns:
            Dictionary with structure:
            {
                'Auth': {'dev': arn, 'staging': arn, 'prod': arn},
                'Api': {'dev': arn, 'staging': arn, 'prod': arn},
                'Webhook': {'dev': arn, 'staging': arn, 'prod': arn}
            }
        """
        import time

        # Handle default region
        if region is None:
            region = Region.DEFAULT

        # Initialize ACM clients for different regions
        acm_us_east_1 = boto3.client("acm", region_name="us-east-1")  # For Auth
        acm_region = boto3.client("acm", region_name=region.value)     # For API and Webhook

        # Certificate tracking: {(type, env): {'domain': str, 'arn': str, 'status': str, 'region': str, 'client': acm_client}}
        cert_tracker = {}

        # Step 1: List existing certificates and request new ones if needed
        print("\n[CERT] Step 1: Checking existing certificates and requesting new ones if needed...")

        for env in environments:
            # Create temporary builder for this environment to get domain names
            temp_builder = TemplateBuilder(env)

            # Iterate over certificate types with proper typing
            cert_types: list[Literal['Auth', 'Api', 'Webhook']] = ['Auth', 'Api', 'Webhook']
            for cert_type in cert_types:
                domain = temp_builder.getDomainNameByType(cert_type)
                acm_client = acm_us_east_1 if cert_type == 'Auth' else acm_region
                cert_region = 'us-east-1' if cert_type == 'Auth' else region.value

                # List existing certificates
                certificates = acm_client.list_certificates(
                    CertificateStatuses=['PENDING_VALIDATION', 'ISSUED', 'INACTIVE', 'EXPIRED', 'VALIDATION_TIMED_OUT', 'REVOKED', 'FAILED']
                )

                status, arn = None, None
                for cert in certificates['CertificateSummaryList']:
                    if cert['DomainName'] == domain:
                        status, arn = cert['Status'], cert['CertificateArn']
                        break

                # Request new certificate if not found
                if not arn:
                    print(f"  [NEW] Requesting certificate for {domain} in {cert_region}")
                    certificate = acm_client.request_certificate(
                        DomainName=domain,
                        ValidationMethod="DNS",
                        Tags=temp_builder.getListTag()
                    )
                    status, arn = 'PENDING_VALIDATION', certificate['CertificateArn']
                else:
                    print(f"  [FOUND] Certificate for {domain} in {cert_region}: {status}")

                # Track this certificate
                cert_tracker[(cert_type, env.value)] = {
                    'domain': domain,
                    'arn': arn,
                    'status': status,
                    'region': cert_region,
                    'client': acm_client
                }

        # Step 2: Wait for all certificates to be issued
        print(f"\n[CERT] Step 2: Waiting for all {len(cert_tracker)} certificates to be issued...")

        # Check if all certificates are already issued
        all_issued = all(cert_info['status'] == 'ISSUED' for cert_info in cert_tracker.values())

        if all_issued:
            print(f"  [OK] All {len(cert_tracker)} certificates are already ISSUED - skipping polling")

        check_count = 0

        while not all_issued:
            check_count += 1
            print(f"\n[CERT] Check #{check_count} - Certificate Status:")
            print("=" * 100)

            all_issued = True
            pending_count = 0
            issued_count = 0
            failed_certs = []

            # Check status of all certificates
            for (cert_type, env_val), cert_info in cert_tracker.items():
                # Get current status
                detail = cert_info['client'].describe_certificate(CertificateArn=cert_info['arn'])
                current_status = detail['Certificate']['Status']
                cert_info['status'] = current_status

                # Log status
                status_emoji = "✓" if current_status == 'ISSUED' else "⏳" if current_status == 'PENDING_VALIDATION' else "✗"
                print(f"  {status_emoji} {cert_type:8} | {env_val:8} | {cert_info['domain']:30} | {current_status:20} | {cert_info['region']}")

                # Check if all are issued
                if current_status == 'ISSUED':
                    issued_count += 1
                elif current_status == 'PENDING_VALIDATION':
                    pending_count += 1
                    all_issued = False
                else:
                    # Failed status
                    all_issued = False
                    failed_certs.append((cert_type, env_val, cert_info['domain'], current_status))

            print("=" * 100)
            print(f"  Summary: {issued_count} issued, {pending_count} pending")

            # Check for failed certificates
            if failed_certs:
                error_msg = "The following certificates failed validation:\n"
                for cert_type, env_val, domain, status in failed_certs:
                    error_msg += f"  - {cert_type} ({env_val}): {domain} - Status: {status}\n"
                raise Exception(error_msg)

            # Wait before next check if not all issued
            if not all_issued:
                print(f"\n[CERT] Waiting 15 seconds before next check...")
                time.sleep(15)

        print(f"\n[CERT] ✓ All {len(cert_tracker)} certificates are ISSUED!")

        # Step 3: Build result dictionary
        result = {
            'Auth': {},
            'Api': {},
            'Webhook': {}
        }

        for (cert_type, env_val), cert_info in cert_tracker.items():
            result[cert_type][env_val] = cert_info['arn']

        return result

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
            print(f"WARNING: User Pool {self.getUserPoolName()} not found in {region.value} - skipping domain creation")
            return

    def getUserPoolClientName(self):
        return f"Dzgro{self.envtextTitle}Client"

    def rootDomain(self):
        return "dzgro.com"

    def envDomain(self):
        if self.env==ENVIRONMENT.PROD: return self.rootDomain()
        return f'{self.envtextlower}.{self.rootDomain()}'

    def getDomainNameByType(self, type: Literal['Auth', 'Api', 'Webhook']):
        """Generate domain name based on type and environment"""
        return f"{type.lower()}.{self.envtextlower}.dzgro.com"

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
        return {'Fn::Sub': f'arn:aws:lambda:${{AWS::Region}}:${{AWS::AccountId}}:function:{function_name}:{alias}'}

    def getApiHttpApiName(self) -> str:
        """Name for API HTTP API"""
        return 'ApiHttpApi'

    def getWebhookHttpApiName(self) -> str:
        """Name for Webhook HTTP API"""
        return 'WebhookHttpApi'
