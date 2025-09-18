from typing import Literal
from dzgroshared.sqs.model import QueueName
from dzgroshared.storage.model import S3Bucket
from deploy.TemplateBuilder.StarterMapping import Region, LambdaName, Tag
from dzgroshared.db.enums import ENVIRONMENT
import os


    

class TemplateBuilder:
    env: ENVIRONMENT
    envtextlower: str
    resources: dict[str, dict] = {}
    is_default_region: bool
    lambdaRoleName: str = 'DzgroLambdaRole'
    apigateway: dict

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        from dzgroshared.db.enums import ENVIRONMENT, CountryCode
        env = ENVIRONMENT(os.getenv("ENV", None))
        if not env: raise ValueError("ENV environment variable not set")
        self.env = env
        self.envtextlower = env.value.lower()

    
    def askForRegions(self):
        import inquirer
        choices=[x.value for x in Region.all()]
        choices.append("All Regions")
        question = [
            inquirer.List(
                "script",
                message="Select a Region to run:",
                choices=choices,
            )
        ]
        answer = inquirer.prompt(question)
        if not answer or "script" not in answer:
            print("No selection made.")
            exit(1)
        if answer["script"] == "All Regions":
            return Region.all()
        return [Region(answer["script"])]

    def deploy(self):
        # regions = self.askForRegions()
        regions = [Region.DEFAULT]
        for region in regions:
            try:
                self.resources = {}
                if region==Region.DEFAULT and self.env != ENVIRONMENT.LOCAL:
                    from deploy.TemplateBuilder.BuildLayers import LambdaLayerBuilder
                    optimized_builder = LambdaLayerBuilder(self.env, region, max_workers=4)
                    layerArns = optimized_builder.execute_optimized()
                    optimized_builder.print_performance_summary()
                    from deploy.TemplateBuilder.BuildCertificates import CertificateBuilder
                    CertificateBuilder(self).execute()
                    from deploy.TemplateBuilder.BuildApiGateway import ApiGatewayBuilder
                    ApiGatewayBuilder(self).execute()
                    from deploy.TemplateBuilder.BuildCognito import CognitoBuilder
                    CognitoBuilder(self).execute()
                    from deploy.TemplateBuilder.BuildLambdasBucketsQueues import LambdasBucketsQueuesBuilder
                    LambdasBucketsQueuesBuilder(self).execute(region, layerArns)
                    from deploy.TemplateBuilder.SamExecutor import SAMExecutor
                    SAMExecutor(self).execute(region)
            except Exception as e:
                print(f"Error occurred while building SAM template for region {region.value}: {e}")
                raise e

    def getDomain(self):
        if self.env == ENVIRONMENT.PROD:return "dzgro.com"
        elif self.env == ENVIRONMENT.TEST:return "test.dzgro.com"
        else:return "dev.dzgro.com"

    def getLambdaRoleName(self, name: LambdaName):
        return f'{name.value}LambdaRole{self.env.value}'

    def getUserPoolName(self):
        return f'DzgroUserPool{self.env.value}'

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

    def createDLQ(self, name:str):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'Tags': self.getListTag() } }

    def createQ(self, name:str, dlq: str):
        return { 'Type': 'AWS::SQS::Queue', 'Properties': { 'QueueName': name, 'VisibilityTimeout': 900, 'RedrivePolicy': { 'deadLetterTargetArn': {'Fn::GetAtt': [dlq, 'Arn']}, 'maxReceiveCount': 1 }, 'Tags': self.getListTag() } }

    def createQEventMapping(self, q:str, functionName: str):
        return { 'Type': 'AWS::Lambda::EventSourceMapping', 'Properties': { 'EventSourceArn': {'Fn::GetAtt': [q, 'Arn']}, 'FunctionName': {'Ref': functionName} } }


if __name__ == "__main__":
    TemplateBuilder().deploy()