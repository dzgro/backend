from typing import Literal
from pydantic import BaseModel
import yaml

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True
    
class Tag(BaseModel):
    Project: str = 'Dzgro'
    Environment: Literal['Prod', 'Test', 'Dev']

Bucket = Literal['dzgro-report-data', 'dzgro-amz-data', 'dzgro-invoices']

import mapping
class TemplateBuilder:
    region: str
    api_gateway_role: str
    lambda_role: str
    layer_arn: str
    resources: dict
    is_default_region: bool
    tags: list[Tag] = [Tag(Environment='Prod')]

    def __init__(self, region: str, api_gateway_role: str, lambda_role: str, layer_arn: str) -> None:
        self.region = region
        self.api_gateway_role = api_gateway_role
        self.lambda_role = lambda_role
        self.layer_arn = layer_arn
        self.is_default_region = (region == mapping.DEFAULT_REGION)
        if self.is_default_region:
            self.tags.append(Tag(Environment='Test'))
            self.tags.append(Tag(Environment='Dev'))
        self.resources = {}

    def deploy(self):
        self.createResources()
        template = {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Transform': 'AWS::Serverless-2016-10-31',
            'Description': f'SAM template for region {self.region}',
            'Resources': self.resources
        }
        import os
        filename = os.path.join(f'sam-template-{self.region}.yaml')
        with open(filename, 'w') as f:
            yaml.dump(template, f, sort_keys=False, Dumper=NoAliasDumper)
        print(f"SAM template for region {self.region} saved to {filename}")
        self.build_deploy_sam_template()

    def createResources(self):
        if self.region==mapping.DEFAULT_REGION:
            for tag in self.tags:
                self.addbuckets(tag)
                self.build_api_resource(tag)
        self.addFunctions()
        self.addQueues()
            

    def getDictTag(self, tag: Tag):
        return {k:v for k,v in tag.model_dump().items() }

    def getListTag(self, tag: Tag):
        return [{"Key": k, "Value": v} for k, v in tag.model_dump().items()]

    def createFunction(self, name:str, path:str, desc:str, tag: Tag, event: dict|None = None):
        resource = { 'Type': 'AWS::Serverless::Function', 'Properties': { 'FunctionName': name, 'Handler': 'handler.handler', 'Runtime': 'python3.12', 'Architectures': ['x86_64'], 'CodeUri': path, 'Description': desc, 'Timeout': 900, 'Layers': [self.layer_arn], 'Role': self.lambda_role, 'Tags': self.getDictTag(tag), "Environment": {"Variables": {"ENV": tag.Environment}} } }
        if event:
            resource['Properties']['Events'] = event
        return resource

    def addFunctions(self):
        for func_key, func in mapping.FUNCTIONS_MAP.items():
            if self.region in func.get('region', []):
                for tag in self.tags:
                    if tag.Environment!='Dev':
                        resource_name = f'{func_key}{tag.Environment}Function'
                        event:dict|None=None
                        if func_key == 'DzgroReportsS3Trigger':
                            event = { "S3UploadEvent": { "Type": "S3", "Properties": { "Bucket": { "Ref": self.getBucketName('dzgro-report-data', tag) }, "Events": "s3:ObjectCreated:*", "Filter": { "S3Key": { "Rules": [ { "Name": "suffix", "Value": ".parquet" } ] } } } } }
                        self.resources[resource_name] = self.createFunction(f'{func_key}{tag.Environment}', func['path'], func.get('description', ''), tag, event)

    def getBucketName(self, name: Bucket, tag: Tag):
        return f'{name.replace("-", " ").title().replace(" ", "")}{tag.Environment}Bucket'

    def addbuckets(self, tag: Tag):
        for bucket in Bucket.__args__:
            resource_name = self.getBucketName(bucket, tag)
            self.resources[resource_name] = {
                'Type': 'AWS::S3::Bucket',
                'Properties': {
                    'BucketName': f'{bucket}-{tag.Environment.lower()}',
                    'Tags': self.getListTag(tag)
                }
            }

    def createDLQ(self, name:str, tag: Tag):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'Tags': self.getListTag(tag) } }

    def createQ(self, name:str, dlq: str, tag: Tag):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'RedrivePolicy': { 'deadLetterTargetArn': {'Fn::GetAtt': [dlq, 'Arn']}, 'maxReceiveCount': 1 }, 'Tags': self.getListTag(tag) } }

    def createQEventMapping(self, q:str, functionName: str):
        return { 'Type': 'AWS::Lambda::EventSourceMapping', 'Properties': { 'EventSourceArn': {'Fn::GetAtt': [q, 'Arn']}, 'FunctionName': {'Ref': functionName} } }

    def addQueues(self):
        for queue_key, queue in mapping.QUEUES_MAP.items():
            if self.region in queue.get('region', []):
                for tag in self.tags:
                    if tag.Environment == 'Test' and not queue.get('test', False) and not self.is_default_region:
                        continue
                    main_queue_name = f'{queue_key}{tag.Environment}Q'
                    dlq_name = f'{queue_key}{tag.Environment}DLQ'
                    self.resources[main_queue_name] = self.createQ(main_queue_name, dlq_name, tag)
                    self.resources[dlq_name] = self.createDLQ(dlq_name, tag)
                    if queue_key == 'AmsPerformance':
                        policy = mapping.getAMSPerformancePolicy(self.region)
                        self.resources['AmsPerformancePolicy'] = policy
                    if queue_key == 'AmsChange':
                        policy = mapping.getAMSChangeSetPolicy(self.region)
                        self.resources['AmsChangePolicy'] = policy
                    # Event source mapping for Lambda trigger
                    if 'function' in queue and tag.Environment!='Dev':
                        event_mapping_name = f'{queue_key}EventSourceMapping'
                        self.resources[event_mapping_name] = self.createQEventMapping(main_queue_name, f"{queue['function']}{tag.Environment}Function")

    def build_api_resource(self, tag: Tag):
        apigateway = { 'Type': 'AWS::Serverless::Api', 'Properties': { 'StageName': tag.Environment, 'EndpointConfiguration': 'REGIONAL', 'Tags': self.getDictTag(tag), 'DefinitionBody': { 'openapi': '3.0.1', 'info': {'title': 'Dzgro API', 'version': '1.0'}, 'paths': {} } } }
        api_paths = {}
        for queue_key, queue in mapping.QUEUES_MAP.items():
            if 'routes' in queue:
                for idx, route in enumerate(queue['routes']):
                    path = route['path']
                    method = route['method'].lower()
                    destination = route['destination']
                    headers = route.get('headers', [])
                    integration = {}
                    if destination.lower() == 'lambda':
                        integration = {
                            'x-amazon-apigateway-integration': {
                                'type': 'aws',
                                'httpMethod': 'POST',
                                'uri': f"arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{LambdaFunctionArn}}/invocations",
                                'credentials': self.api_gateway_role,
                                'requestTemplates': { 'application/json': '{ "body": $input.json(\'$\') }' }
                            }
                        }
                    elif destination.lower() == 'sqs':
                        uri = { "Fn::Sub": [ "arn:aws:apigateway:${AWS::Region}:sqs:path/${AWS::AccountId}/${QueueName}", { "QueueName": { "Fn::GetAtt": [f'{queue_key}{tag.Environment}Q', "QueueName"] } } ] }
                        request_template = "Action=SendMessage&MessageBody=$input.body"
                        if headers:
                            for i, header in enumerate(headers, 1):
                                request_template += f"&MessageAttribute.{i}.Name={header}" \
                                    f"&MessageAttribute.{i}.Value.StringValue=$input.params().header.get('{header}')" \
                                    f"&MessageAttribute.{i}.Value.DataType=String"
                        integration = {
                            'x-amazon-apigateway-integration': {
                                'type': 'aws',
                                'httpMethod': 'POST',
                                'uri': uri,
                                'credentials': self.api_gateway_role,
                                'requestParameters': { 'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'" },
                                'requestTemplates': { 'application/x-www-form-urlencoded': request_template }
                            }
                        }
                    # Add to OpenAPI paths
        if path not in api_paths: api_paths[path] = {}
        api_paths[path][method] = { 'responses': {'200': {'description': 'Success'}}, **integration }
        apigateway['Properties']['DefinitionBody']['paths'] = api_paths
        self.resources[f'ApiGateway{tag.Environment}'] = apigateway

    def build_deploy_sam_template(self):
        """
        Builds and deploys the SAM template for the given region using AWS SAM CLI.
        """
        import subprocess
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        template_file = os.path.join(f'sam-template-{self.region}.yaml')
        built_template_file = os.path.join(project_root, '.aws-sam', 'build', 'template.yaml')
        s3_bucket = f'dzgro-sam-{self.region}'

        # Check if dzgro-sam bucket exists in the region, create if not
        import boto3
        s3 = boto3.client('s3', region_name=self.region)
        try:
            s3.head_bucket(Bucket=s3_bucket)
        except Exception:
            print(f"Bucket {s3_bucket} does not exist in region {self.region}, creating...")
            if self.region == "us-east-1":
                s3.create_bucket(Bucket=s3_bucket)
            else:
                s3.create_bucket(Bucket=s3_bucket, CreateBucketConfiguration={'LocationConstraint': self.region})
            print(f"Bucket {s3_bucket} created in region {self.region}.")

        build_command = [
            'sam', 'build',
            '--template-file', template_file
        ]
        deploy_command = [
            'sam', 'deploy',
            '--template-file', built_template_file,  # Use built template from .aws-sam/build
            '--region', self.region,
            '--no-confirm-changeset',
            '--stack-name', f"dzgro-sam-{self.region}",
            '--s3-bucket', s3_bucket, '--force-upload'
        ]
        
        try:
            subprocess.run(build_command, check=True, shell=True)
            subprocess.run(deploy_command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error building or deploying SAM template for region {self.region}: {e.stderr}")
