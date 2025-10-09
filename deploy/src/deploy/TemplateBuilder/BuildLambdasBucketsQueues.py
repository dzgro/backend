from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import LAMBDAS, LAYER_NAME, LambdaName, LambdaProperty, LambdaRegion, QueueProperty, QueueRole, Region, S3Property, S3Role
from dzgroshared.db.enums import ENVIRONMENT


class LambdasBucketsQueuesBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def execute(self, region: Region, LayerArn: dict[LAYER_NAME, str]):
        from dzgroshared.secrets.client import SecretManager
        secrets = SecretManager(self.builder.env).secrets.model_dump(mode="json")
        print(f"Loaded {len(secrets)} secrets for Lambda environment variables")
        
        for _lambda in LAMBDAS:
            if self.builder.env in _lambda.env:
                for _lambdaRegion in _lambda.regions:
                    if _lambdaRegion.region == region:
                        if region==Region.DEFAULT:
                            self.addBucket(_lambdaRegion.s3)
                            if self.builder.env != ENVIRONMENT.LOCAL:
                                self.createLambdaRole(_lambda, region)
                                if _lambdaRegion.queue: 
                                    self.addQueue(region, _lambdaRegion.queue, _lambda.name)
                                self.createFunction(_lambda, _lambdaRegion, LayerArn, secrets)
    
    def createFunction(self, property: LambdaProperty, _lambda: LambdaRegion, layer_arn: dict[LAYER_NAME, str], secrets: dict):
        fnName = self.builder.getFunctionName(property.name)
        # Start with base environment variables
        env_variables = {"ENV": self.builder.env.value, **secrets}
        properties = {
            'FunctionName': fnName,
            'Handler': 'handler.handler',
            'Runtime': 'python3.12',
            "Architectures": ["x86_64"],
            'CodeUri': f"functions/{property.name.value}",
            'Description': f'{self.builder.env.value.capitalize()} - {property.description}',
            'Timeout': property.timeout,
            'MemorySize': property.memorySize,
            'Role': {"Fn::GetAtt": [self.builder.getLambdaRoleName(property.name), "Arn"]},
            'Tags': self.builder.getDictTag(),
            "Environment": {"Variables": env_variables}
        }
        if property.layers: properties['Layers'] = [layer_arn[name] for name in property.layers]
        for s3 in _lambda.s3:
            if s3.trigger:
                event = { "Bucket": { "Ref": self.builder.getBucketResourceName(s3.name) }, "Events": s3.trigger.eventName }
                if s3.trigger.filter: event["Filter"] = s3.trigger.filter
                properties['Events'] = { "S3UploadEvent": { "Type": "S3", "Properties": event } }
        resource = { 'Type': 'AWS::Serverless::Function', 'Properties': properties }
        self.builder.resources[fnName] = resource

    def addBucket(self, s3Properties: list[S3Property]):
        for s3 in s3Properties:
            resource_name = self.builder.getBucketResourceName(s3.name)
            properties = {
                'BucketName': self.builder.getBucketName(s3.name),
                'Tags': self.builder.getListTag()
            }
            if s3.lifeCycleConfiguration:
                properties['LifecycleConfiguration'] = s3.lifeCycleConfiguration.model_dump(mode="json")
            if s3.cors:
                if self.builder.env==ENVIRONMENT.LOCAL: origins = ["https://localhost:4200"]
                else: origins = [self.builder.envDomain()]
                properties['CorsConfiguration'] = {
                    "CorsRules": [
                        { "AllowedOrigins": origins, "AllowedMethods": [m.value for m in s3.cors.methods], "AllowedHeaders": ["*"], "MaxAge": 3000 }
                    ]
                }
            self.builder.resources[resource_name] = {
                'Type': 'AWS::S3::Bucket',
                'Properties': properties
            }

    def addQueue(self, region: Region, sqsList: list[QueueProperty], functionName: LambdaName):
        for sqs in sqsList:
            resource = {}
            main_queue_name = self.builder.getQueueName(sqs.name, 'Q')
            dlq_name = self.builder.getQueueName(sqs.name, 'DLQ')
            resource[main_queue_name] = self.builder.createQ(main_queue_name, dlq_name)
            resource[dlq_name] = self.builder.createDLQ(dlq_name)
            if sqs.policy: resource[f'{sqs.name.value}Policy'] = sqs.policy
            eventName = self.builder.getQueueName(sqs.name, 'EventSourceMapping')
            resource[eventName] = self.builder.createQEventMapping(main_queue_name, self.builder.getFunctionName(functionName))
            self.builder.resources.update(resource)
            if sqs.apiTrigger:
                paths = self.addSQSPathToApiGateway(sqs)
                self.builder.resources[self.builder.getApiGatewayName()]['Properties']['DefinitionBody']['paths'] = paths
        if region==Region.DEFAULT and self.builder.env in [ENVIRONMENT.DEV, ENVIRONMENT.STAGING]:
            lambda_logical_id = self.builder.getFunctionName(LambdaName.Api) 
            self.builder.resources[self.builder.getApiGatewayName()]['Properties']['DefinitionBody']['paths'].update(
                {
                    "/api/{proxy+}": {
                        "x-amazon-apigateway-any-method": {
                        "x-amazon-apigateway-integration": {
                            "uri": { "Fn::Sub": f"arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{{lambda_logical_id}.Arn}}/invocations" },
                            "httpMethod": "POST",
                            "type": "aws_proxy"
                        }
                        },
                        "options": {
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "responses": {
                                "200": {
                                "description": "CORS support",
                                "headers": {
                                    "Access-Control-Allow-Origin": {"type": "string"},
                                    "Access-Control-Allow-Methods": {"type": "string"},
                                    "Access-Control-Allow-Headers": {"type": "string"}
                                }
                                }
                            },
                            "x-amazon-apigateway-integration": {
                                "type": "mock",
                                "requestTemplates": {"application/json": "{\"statusCode\": 200}"},
                                "responses": {
                                "default": {
                                    "statusCode": "200",
                                    "responseParameters": {
                                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST,PUT,DELETE'",
                                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                                    "method.response.header.Access-Control-Allow-Origin": "'*'"
                                    }
                                }
                                }
                            }
                        }
                    }
                }
            )

    def addSQSPathToApiGateway(self, sqs: QueueProperty):
        api_paths = {}
        for route in (sqs.apiTrigger or []):
            queuename = self.builder.getQueueName(sqs.name, 'Q')
            uri = { "Fn::Sub": [ "arn:aws:apigateway:${AWS::Region}:sqs:path/${AWS::AccountId}/${QueueName}", { "QueueName": { "Fn::GetAtt": [queuename, "QueueName"] } } ] }
            request_template = "Action=SendMessage&MessageBody=$input.body"
            if route.headers:
                for i, header in enumerate(route.headers, 1):
                    request_template += f"&MessageAttribute.{i}.Name={header}" \
                        f"&MessageAttribute.{i}.Value.StringValue=$input.params().header.get('{header}')" \
                        f"&MessageAttribute.{i}.Value.DataType=String"
            i = len(route.headers) if route.headers else 0    
            if route.modeltype:
                request_template += f"&MessageAttribute.{i+1}.Name=model" \
                    f"&MessageAttribute.{i+1}.Value.StringValue={route.modeltype.value}" \
                    f"&MessageAttribute.{i+1}.Value.DataType=String"
            integration = {
                'x-amazon-apigateway-integration': {
                    'type': 'aws',
                    'httpMethod': 'POST',
                    'uri': uri,
                    'credentials': {"Fn::GetAtt": [self.builder.getApiGatewayRoleName(), "Arn"]},
                    'requestParameters': { 'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'" },
                    'requestTemplates': { 'application/x-www-form-urlencoded': request_template }
                }
            }
            api_paths[route.path] = {route.method.lower(): { 'responses': {'200': {'description': 'Success'}}, **integration }}
        return api_paths
    
    def createLambdaRole(self, _lambda: LambdaProperty, region: Region):
        rolename: str = self.builder.getLambdaRoleName(_lambda.name)
        role = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": rolename,
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [ { "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole", } ]
                },
                "ManagedPolicyArns": [ "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" ]
            }
        }
        if _lambda.name != LambdaName.CognitoTrigger:
            queueNames: dict[str, list[QueueRole]] = {self.builder.getQueueName(q.name, 'Q'): q.roles for region in _lambda.regions for q in region.queue}
            bucketnames: dict[str, list[S3Role]] = {self.builder.getBucketName(s3.name): s3.roles for region in _lambda.regions for s3 in region.s3}
            if queueNames or bucketnames: role["Properties"]["Policies"] = []
            if queueNames:
                role["Properties"]["Policies"].append({
                    "PolicyName": f"LambdaSQSAccess",
                    "PolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [ 
                            { 
                                "Effect": "Allow",
                                "Action": [x.value for x in QueueRole.all()], 
                                "Resource": [ {"Fn::GetAtt": [k, "Arn"]}] } for k,v in queueNames.items()]
                    }
                })

            if bucketnames:
                role["Properties"]["Policies"].append({
                    "PolicyName": f"LambdaS3Access",
                    "PolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [ 
                            { 
                                "Effect": "Allow",
                                "Action": [x.value for x in [S3Role.GetObject, S3Role.PutObject, S3Role.DeleteObject]], 
                                "Resource": [ {"Fn::Sub": f"arn:aws:s3:::{k}/*"} for k,v in bucketnames.items()] 
                            },
                            { 
                                "Effect": "Allow",
                                "Action": [x.value for x in [S3Role.ListBucket]], 
                                "Resource": [ {"Fn::Sub": f"arn:aws:s3:::{k}"} for k,v in bucketnames.items()] 
                            }
                            
                        ]
                    
                    }
                })
        self.builder.resources[rolename] = role