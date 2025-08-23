from typing import Literal
import yaml
from rolecreator import RoleCreator
import mapping
from mapping import LambdaRegion, Region, S3Property, QueueProperty, LambdaName, S3Bucket, QueueName, Tag, Environment, LambdaProperty, QueueRole, S3Role

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True
    

class TemplateBuilder:
    env: Environment
    envtextlower: str
    resources: dict[str, dict] = {}
    is_default_region: bool
    lambdaRoleName: str = 'DzgroLambdaRole'
    roleCreator: RoleCreator
    apigateway: dict

    def __init__(self, env: Environment) -> None:
        self.env = env
        self.envtextlower = env.value.lower()
        self.roleCreator = RoleCreator()

    def deploy(self):
        # import layer_builder as LayerBuilder
        # LayerBuilder.build_layer_zip_clean()
        for region in Region.all():
            self.resources = {}
            # LayerBuilder.deploy_layer(region, self.env)
            LayerArn = f"arn:aws:lambda:{region.value}:522814698847:layer:dzgroshared_layer:7"
            self.createCertificateAndLinkApi(region)
            self.createResources(region, LayerArn)
            template = {
                'AWSTemplateFormatVersion': '2010-09-09',
                'Transform': 'AWS::Serverless-2016-10-31',
                'Description': f'SAM {self.env.value} template for region {region.value}',
                'Resources': self.resources
            }
            import os
            name = f'dzgro-sam-{region.value}-{self.envtextlower}'
            filename = os.path.join(f'{name}.yaml')
            with open(filename, 'w') as f:
                yaml.dump(template, f, sort_keys=False, Dumper=NoAliasDumper)

            self.validate(filename, region)
            print(f"SAM template for region {region.value} saved to {filename}")
            self.build_deploy_sam_template(name, region)

    def createCertificateAndLinkApi(self, region: Region):
        api = f"api-{self.envtextlower}.dzgro.com"
        resource: dict = {
            'MyCertificate': {
                "Type": "AWS::CertificateManager::Certificate",
                "Properties": {
                    "DomainName": api,
                    "SubjectAlternativeNames": [f"www.{api}"],
                    "ValidationMethod": "DNS"
                }
            },
            'MyCustomDomain': {
                "Type": "AWS::ApiGateway::DomainName",
                "Properties": {
                    "DomainName": api,
                    "RegionalCertificateArn": { "Ref": "MyCertificate" },
                    "EndpointConfiguration": {
                        "Types": ["REGIONAL"]
                    }
                }
            },
            "MyBasePathMapping": {
                "Type": "AWS::ApiGateway::BasePathMapping",
                "Properties": {
                    "DomainName": { "Ref": "MyCustomDomain" },
                    "RestApiId": { "Ref": self.getApiGatewayName() },
                    "Stage": self.env.value
                }
            }
        }
        self.resources.update(resource)

    def getLambdaRoleName(self, name: LambdaName):
        return f'{name.value}LambdaRole{self.env.value}'

    def getApiGatewayRoleName(self):
        return f'ApiGatewayRole{self.env.value}'

    def getApiGatewayName(self):
        return f'ApiGateway{self.env.value}'

    def getBucketName(self, name: S3Bucket):
        return f'{name.value}-{self.envtextlower}'

    def getBucketResourceName(self, name: S3Bucket):
        return f'{name.value.replace("-", " ").title().replace(" ", "")}{self.env.value}Bucket'

    def getFunctionName(self, name: LambdaName):
        return f'{name.value}{self.env.value}Function'

    def getQueueName(self, name: QueueName, type: Literal['Q','DLQ','EventSourceMapping']):
        return f'{name.value}{self.env.value}{type}'

    def getDictTag(self):
        return {k:v for k,v in Tag(Environment=self.env).model_dump(mode="json").items() }

    def getListTag(self):
        return [{"Key": k, "Value": v} for k, v in Tag(Environment=self.env).model_dump(mode="json").items()]

    def createLambdaRole(self, _lambda: LambdaProperty, region: Region):
        rolename: str = self.getLambdaRoleName(_lambda.name)
        parameter = (Environment.Prod if self.env == Environment.Prod else Environment.Test).value.lower()
        secretsarn = f"arn:aws:secretsmanager:{region.value}:${{AWS::AccountId}}:secret:dzgro/{parameter}"
        role = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": rolename,
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                            # "Condition": { "ArnEquals": { "aws:SourceArn": [{"Fn::GetAtt": [self.getFunctionName(_lambda.name), "Arn"]}] } }
                        }
                    ]
                },
                "Policies": [
                    {
                        "PolicyName": "LambdaLogging",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [ { "Effect": "Allow", "Action": [ "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents" ], "Resource": "*" } ]
                        }
                    },
                    {
                        "PolicyName": "SSMParameterRead",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [ { "Effect": "Allow", "Action": [ "secretsmanager:GetSecretValue" ], "Resource": {"Fn::Sub": secretsarn} } ]
                        }
                    }
                ]
            }
        }
        queueNames: dict[str, list[QueueRole]] = {self.getQueueName(region.queue.name, 'Q'): region.queue.roles for region in _lambda.regions if region.queue}
        bucketnames: dict[str, list[S3Role]] = {self.getBucketName(region.s3.name): region.s3.roles for region in _lambda.regions if region.s3 and not region.s3.trigger}
        
        for k,v in queueNames.items() :
            role["Properties"]["Policies"].append({
                "PolicyName": f"LambdaSQSAccess{k}",
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [ { "Effect": "Allow", "Action": [x.value for x in v], "Resource": [ {"Fn::GetAtt": [k, "Arn"]}] }]
                }
            })

        for k,v in bucketnames.items() :
            role["Properties"]["Policies"].append({
                "PolicyName": f"LambdaS3Access{k}",
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [ { "Effect": "Allow", "Action": [x.value for x in v], "Resource": [ {"Fn::Sub": f"arn:aws:s3:::{k}/*"} ] } ]
                }
            })

        self.resources[rolename] = role


    def createApiGatewayRole(self, region: Region):
        rolename: str = self.getApiGatewayRoleName()
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
                        "PolicyName": "ApiGatewayLambdaInvoke",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "lambda:InvokeFunction",
                                    "Resource": { "Fn::Sub": f"arn:aws:lambda:${{AWS::Region}}:${{AWS::AccountId}}:function:*{self.env.value}" }
                                }
                            ]
                        }
                    },
                    {
                        "PolicyName": "ApiGatewaySQSAccess",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "sqs:SendMessage",
                                    "Resource": { "Fn::Sub": f"arn:aws:sqs:${{AWS::Region}}:${{AWS::AccountId}}:*{self.env.value}" }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.resources[rolename] = role



    def createResources(self, region: Region, LayerArn: str):
        for _lambda in mapping.LAMBDAS:
            for _lambdaRegion in _lambda.regions:
                if _lambdaRegion.region == region:
                    if region==Region.DEFAULT:
                        self.createRawApiGateway(region)
                        self.createApiGatewayRole(region)
                    self.createLambdaRole(_lambda, region)
                    if _lambdaRegion.s3: self.addBucket(region, _lambdaRegion.s3)
                    if _lambdaRegion.queue: 
                        self.addQueue(region, _lambdaRegion.queue, _lambda.name)
                    self.createFunction(_lambda.name, _lambdaRegion, LayerArn)
                

    def createRawApiGateway(self, region: Region):
        self.resources[self.getApiGatewayName()] = { 'Type': 'AWS::Serverless::Api', 'Properties': { 'StageName': self.env.value, 'EndpointConfiguration': 'REGIONAL', 'Tags': self.getDictTag(), 'DefinitionBody': { 'openapi': '3.0.1', 'info': {'title': 'Dzgro API', 'version': '1.0'}, 'paths': {} } } }

    def createFunction(self, name: LambdaName,  _lambda: LambdaRegion, layer_arn: str):
        fnName = self.getFunctionName(name)
        resource = { 'Type': 'AWS::Serverless::Function', 'Properties': { 
            'FunctionName': fnName,
            'Handler': 'handler.handler',
            'Runtime': 'python3.12',
            'Architectures': ['x86_64'],
            'CodeUri': f"functions/{name.value}",
            'Description': _lambda.description,
            'Timeout': 900,
            'Layers': [layer_arn],
            'Role': {"Fn::GetAtt": [self.getLambdaRoleName(name), "Arn"]},
            'Tags': self.getDictTag(),
            "Environment": {"Variables": {"ENV": self.env.value}}
        }}
        if _lambda.s3 and _lambda.s3.trigger:
            event = { "Bucket": { "Ref": self.getBucketResourceName(_lambda.s3.name) }, "Events": _lambda.s3.trigger.eventName }
            if _lambda.s3.trigger.filter:
                event["Filter"] = { "S3Key": { "Rules": [ { "Name": "suffix", "Value": ".parquet" } ] } }
            resource['Properties']['Events'] = { "S3UploadEvent": { "Type": "S3", "Properties": event } }
        self.resources[fnName] = resource

    def addBucket(self, region: Region, s3: S3Property):
        resource_name = self.getBucketResourceName(s3.name)
        self.resources[resource_name] = {
            'Type': 'AWS::S3::Bucket',
            'Properties': {
                'BucketName': self.getBucketName(s3.name),
                'Tags': self.getListTag()
            }
        }

    def createDLQ(self, name:str):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'Tags': self.getListTag() } }

    def createQ(self, name:str, dlq: str):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'RedrivePolicy': { 'deadLetterTargetArn': {'Fn::GetAtt': [dlq, 'Arn']}, 'maxReceiveCount': 1 }, 'Tags': self.getListTag() } }

    def createQEventMapping(self, q:str, functionName: str):
        return { 'Type': 'AWS::Lambda::EventSourceMapping', 'Properties': { 'EventSourceArn': {'Fn::GetAtt': [q, 'Arn']}, 'FunctionName': {'Ref': functionName} } }

    def addQueue(self, region: Region, sqs: QueueProperty, functionName: LambdaName):
        resource = {}
        main_queue_name = self.getQueueName(sqs.name, 'Q')
        dlq_name = self.getQueueName(sqs.name, 'DLQ')
        resource[main_queue_name] = self.createQ(main_queue_name, dlq_name)
        resource[dlq_name] = self.createDLQ(dlq_name)
        if sqs.policy: resource[f'{sqs.name.value}Policy'] = sqs.policy
        if sqs.apiTrigger:
            paths = self.addSQSPathToApiGateway(sqs)
            self.resources[self.getApiGatewayName()]['Properties']['DefinitionBody']['paths'] = paths
        else:
            eventName = self.getQueueName(sqs.name, 'EventSourceMapping')
            resource[eventName] = self.createQEventMapping(main_queue_name, self.getFunctionName(functionName))
        self.resources.update(resource)

    def addSQSPathToApiGateway(self, sqs: QueueProperty):
        api_paths = {}
        for route in (sqs.apiTrigger or []):
            queuename = self.getQueueName(sqs.name, 'Q')
            uri = { "Fn::Sub": [ "arn:aws:apigateway:${AWS::Region}:sqs:path/${AWS::AccountId}/${QueueName}", { "QueueName": { "Fn::GetAtt": [queuename, "QueueName"] } } ] }
            request_template = "Action=SendMessage&MessageBody=$input.body"
            if route.headers:
                for i, header in enumerate(route.headers, 1):
                    request_template += f"&MessageAttribute.{i}.Name={header}" \
                        f"&MessageAttribute.{i}.Value.StringValue=$input.params().header.get('{header}')" \
                        f"&MessageAttribute.{i}.Value.DataType=String"
            integration = {
                'x-amazon-apigateway-integration': {
                    'type': 'aws',
                    'httpMethod': 'POST',
                    'uri': uri,
                    'credentials': {"Fn::GetAtt": [self.getApiGatewayRoleName(), "Arn"]},
                    'requestParameters': { 'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'" },
                    'requestTemplates': { 'application/x-www-form-urlencoded': request_template }
                }
            }
            api_paths[route.path] = {route.method.lower(): { 'responses': {'200': {'description': 'Success'}}, **integration }}
        return api_paths

    def validate(self, template_file:str, region: Region):
        import subprocess
        validate_command = ['sam', 'validate','--template-file', template_file]
        try:
            print(f"Validating SAM template for region {region.value} and environment {self.env.value}...")
            subprocess.run(validate_command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error validating, building, or deploying SAM template for region {region.value} for {self.env.value}: {e.stderr}")

    def build_deploy_sam_template(self, name:str,region: Region):
        """
        Builds and deploys the SAM template for the given region using AWS SAM CLI.
        """
        import subprocess
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        template_file = os.path.join(f'{name}.yaml')
        built_template_file = os.path.join(project_root, '.aws-sam', 'build', 'template.yaml')

        # Check if dzgro-sam bucket exists in the region, create if not
        import boto3
        s3 = boto3.client('s3', region_name=region.value)
        try:
            s3.head_bucket(Bucket=name)
        except Exception:
            print(f"Bucket {name} does not exist in region {region.value}, creating...")
            if region.value == "us-east-1":
                s3.create_bucket(Bucket=name)
            else:
                s3.create_bucket(Bucket=name, CreateBucketConfiguration={'LocationConstraint': region.value})
            print(f"Bucket {name} created in region {region.value}.")

        build_command = [
            'sam', 'build',
            '--template-file', template_file
        ]
        deploy_command = [
            'sam', 'deploy',
            '--template-file', built_template_file,  # Use built template from .aws-sam/build
            '--region', region.value,
            '--no-confirm-changeset',
            '--capabilities', 'CAPABILITY_NAMED_IAM',
            '--stack-name', name,
            '--s3-bucket', name, '--force-upload'
        ]
        
        try:
            subprocess.run(build_command, check=True, shell=True)
            subprocess.run(deploy_command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error building or deploying SAM template for region {region.value} for {self.env.value}: {e.stderr}")
