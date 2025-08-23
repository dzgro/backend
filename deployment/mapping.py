# mapping.py
"""
Maps function names to their deployment configuration, including AWS region and other metadata.
"""
from enum import Enum
from typing import Literal

from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class Environment(str, Enum):
    Prod = "Prod"
    Test = "Test"
    Dev = "Dev"
    
    @staticmethod
    def all():
        return list(Environment)

class Tag(BaseModel):
    Project: str = 'Dzgro'
    Environment: Environment

class QueueName(str, Enum):
    AmazonReports = "AmazonReports"
    RazorpayWebhook = "RazorpayWebhook"
    DzgroReports = "DzgroReports"
    AmsChange = "AmsChange"
    AmsPerformance = "AmsPerformance"
    PaymentProcessor = "PaymentProcessor"

class S3Bucket(str, Enum):
    DzgroReports = "dzgro-report-data"
    AmazonReports = "dzgro-amz-report-data"
    Invoices = "dzgro-invoice"

class LambdaName(str, Enum):
    AmazonDailyReport = "AmazonDailyReport"
    DzgroReports = "DzgroReports"
    DzgroReportsS3Trigger = "DzgroReportsS3Trigger"
    PaymentProcessor = "PaymentProcessor"
    RazorpayWebhookProcessor = "RazorpayWebhookProcessor"
    AmsChange = "AmsChange"
    AmsPerformance = "AmsPerformance"


class QueueRole(str, Enum):
    ReceiveMessage = "sqs:ReceiveMessage"
    SendMessage = "sqs:SendMessage"
    DeleteMessage = "sqs:DeleteMessage"
    GetQueueAttributes = "sqs:GetQueueAttributes"

    @staticmethod
    def all():
        return list(QueueRole)
    @staticmethod
    def read():
        return [QueueRole.ReceiveMessage, QueueRole.GetQueueAttributes, QueueRole.DeleteMessage]

class S3Role(str, Enum):
    GetObject = "s3:GetObject"
    PutObject = "s3:PutObject"

    @staticmethod
    def all():
        return list(S3Role)

class Region(str, Enum):
    DEFAULT = 'ap-south-1'
    EU = "eu-west-1"
    NA = "us-east-1"
    FE = "us-west-2"

    @staticmethod
    def all():
        return list(Region)

    @staticmethod
    def default():
        return [Region.DEFAULT]

    @staticmethod
    def others():
        return [Region.EU, Region.NA, Region.FE]
    
class ApiGatewayRoute(BaseModel):
    method: Literal['POST', 'GET', 'PUT', 'DELETE', 'PATCH']
    path: str

    
class APIGatewaySQSTrigger(ApiGatewayRoute):
    headers: list[str] = []

class QueueProperty(BaseModel):
    name: QueueName
    roles: list[QueueRole] 
    visibilityTimeout: int = 900
    maxReceiveCount: int = 1
    policy: dict|SkipJsonSchema[None]=None
    apiTrigger: list[APIGatewaySQSTrigger]|SkipJsonSchema[None]=None

class S3TiggerEvent(BaseModel):
    eventName: str
    filter: dict|SkipJsonSchema[None]=None

class S3Property(BaseModel):
    name: S3Bucket
    roles: list[S3Role]
    trigger: S3TiggerEvent|SkipJsonSchema[None]=None

class LambdaRegion(BaseModel):
    region: Region
    memorySize: int = 128
    timeout: int = 900
    description: str = "General Description"
    queue: QueueProperty|SkipJsonSchema[None]=None
    s3: S3Property|SkipJsonSchema[None]=None
    api: ApiGatewayRoute|SkipJsonSchema[None]=None

class LambdaProperty(BaseModel):
    name: LambdaName
    regions: list[LambdaRegion]

def createPolicy(region:Region, name:LambdaName, arns: list[str]):
    return {
        "Type": "AWS::SQS::QueuePolicy",
        "Properties": {
            "Queues": [ {'Ref': f'{name.value}Q'} ],
            "PolicyDocument": {
                "Version": "2008-10-17",
                "Id": f'Id-{name.value}-{region.value}',
                "Statement": [
                    {
                        "Sid": f'Sid-{name.value}-{region.value}',
                        "Effect": "Allow",
                        "Principal": { "Service": "sns.amazonaws.com" },
                        "Action": "SQS:SendMessage",
                        "Resource": {'Fn::GetAtt': [f'{name.value}Q', 'Arn']},
                        "Condition": { "ArnEquals": {"aws:SourceArn": arns} }
                    },
                    {
                        "Sid": f'SidReview-{name.value}-{region.value}',
                        "Effect": "Allow",
                        "Principal": { "AWS": "arn:aws:iam::926844853897:role/ReviewerRole" },
                        "Action": "SQS:GetQueueAttributes",
                        "Resource": "*"
                    }
                ]
            }
        }
    }

def getAMSPerformancePolicy(region: Region):
    if region == Region.NA:
        ids = ['906013806264', '802324068763', '370941301809', '877712924581', '709476672186', '154357381721']
    elif region == Region.EU:
        ids = ['668473351658', '562877083794', '947153514089', '664093967423', '623198756881', '195770945541']
    elif region == Region.FE:
        ids = ['074266271188', '622939981599', '310605068565', '818973306977', '485899199471', '112347756703']
    return createPolicy(region, LambdaName.AmsPerformance, [f"arn:aws:sns:{region}:{id}:*" for id in ids])

def getAMSChangeSetPolicy(region: Region):
    if region == Region.NA:
        ids = ['570159413969', '118846437111', '305370293182', '644124924521']
    elif region == Region.EU:
        ids = ['834862128520', '130948361130', '648558082147', '503759481754']
    elif region == Region.FE:
        ids = ['527383333093', '668585072850', '802070757281', '248074939493']
    return createPolicy(region, LambdaName.AmsChange, [f"arn:aws:sns:{region}:{id}:*" for id in ids])

LAMBDAS = [
    LambdaProperty(
        name=LambdaName.AmazonDailyReport,
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                queue=QueueProperty(
                    name=QueueName.AmazonReports,
                    roles=QueueRole.all()
                ),
                s3=S3Property(name=S3Bucket.AmazonReports, roles=S3Role.all())
            )
        ]
    ),
    LambdaProperty(
        name=LambdaName.DzgroReports,
        regions=[LambdaRegion(
            region=Region.DEFAULT,
            queue=QueueProperty(
                name=QueueName.DzgroReports,
                roles=QueueRole.all()
            ),
        )],
    ),
    LambdaProperty(
        name=LambdaName.DzgroReportsS3Trigger,
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                s3=S3Property(
                    name=S3Bucket.DzgroReports, 
                    roles=[S3Role.GetObject], 
                    trigger=S3TiggerEvent(
                        eventName="s3:ObjectCreated:*",
                        filter={ "S3Key": { "Rules": [ { "Name": "suffix", "Value": ".parquet" } ] } }
                    )
                )
            ),
        ]
    ),
    LambdaProperty(
        name=LambdaName.PaymentProcessor,
        regions=[LambdaRegion(
            region=Region.DEFAULT,
            queue=QueueProperty(
                name=QueueName.PaymentProcessor,
                roles=QueueRole.all()
            ),
            s3=S3Property(name=S3Bucket.Invoices, roles=S3Role.all())
        )]
    ),
    LambdaProperty(
        name=LambdaName.RazorpayWebhookProcessor,
        regions=[LambdaRegion(
            region=Region.DEFAULT,
            queue=QueueProperty(
                name=QueueName.RazorpayWebhook,
                roles=QueueRole.all(),
                apiTrigger=[
                    APIGatewaySQSTrigger(
                    method='POST',
                    path='/webhook/rzrpay',
                    headers=['x-razorpay-event-id', 'X-Razorpay-Signature']
                )]
            )
        )]  
    ),
    LambdaProperty(
        name=LambdaName.AmsChange,
        regions=[
            LambdaRegion(
                region=region,
                queue=QueueProperty(
                    name=QueueName.AmsChange,
                    roles=QueueRole.read(),
                    policy = getAMSChangeSetPolicy(region)
                ),
            ) for region in Region.others()
        ],
    ),
    LambdaProperty(
        name=LambdaName.AmsPerformance,
        regions=[
            LambdaRegion(
                region=region,
                queue=QueueProperty(
                    name=QueueName.AmsPerformance,
                    roles=QueueRole.read(),
                    policy = getAMSPerformancePolicy(region)
                ),
            ) for region in Region.others()
        ],
    )

]



# FUNCTIONS_MAP = {
#     'AmazonDailyReport': {
#         'region': [DEFAULT_REGION],
#         'test': True,
#         'path': 'functions/AmazonDailyReport',
#         'description': 'Amazon Daily Report Lambda',
#         'queue': 'AmazonReports',
#         'queueRoles': 'AmazonReports',
#         'bucket': 'dzgro-amz-report-data'
#     },
#     'DzgroReports': {
#         'region': [DEFAULT_REGION],
#         'test': True,
#         'path': 'functions/DzgroReports',
#         'description': 'Dzgro Reports Lambda',
#         'queue': 'AmazonReports',
#         'bucket': 'dzgro-report-data',
#         's3Roles': ["s3:GetObject","s3:PutObject"]
#     },
#     'DzgroReportsS3Trigger': {
#         'region': [DEFAULT_REGION],
#         'test': True,
#         'path': 'functions/DzgroReportsS3Trigger',
#         'description': 'Dzgro Report Parquet to Excel Lambda',
#         'bucket': 'dzgro-report-data',
#         's3Roles': ["s3:GetObject"]
#     },
#     'AmsChange': {
#         'region': [EU, NA, FE],
#         'path': 'functions/AmsChange',
#         'description': 'AMS Change Lambda',
#     },
#     'AmsPerformance': {
#         'region': [EU, NA, FE],
#         'path': 'functions/AmsPerformance',
#         'description': 'AMS Performance Lambda',
#     },
#     'PaymentProcessor': {
#         'region': [DEFAULT_REGION],
#         'test': True,
#         'path': 'functions/PaymentProcessor',
#         'description': 'Payment Processing Lambda',
#     },
#     'RazorpayWebhookProcessor': {
#         'region': [DEFAULT_REGION],
#         'path': 'functions/RazorpayWebhookProcessor',
#         'description': 'Razorpay Webhook Processor Lambda',
#     },
# }

# QUEUES_MAP = {
#     'RazorpayWebhook': {
#         'region': [DEFAULT_REGION],
#         'description': 'Main Queue for Razorpay Webhook',
#         'routes': [
#             {
#                 'method': 'POST',
#                 'path': '/webhook/rzrpay',
#                 'destination': 'SQS',
#                 'headers': ['x-razorpay-event-id', 'X-Razorpay-Signature']
#             }
#         ]
#     },
#     'AmazonReports': {
#         'region': [DEFAULT_REGION],
#         'test': True,
#         'description': 'Amazon Daily Reports',
#         'function': 'AmazonDailyReport'
#     },
#     'AmsChange': {
#         'region': [EU, NA, FE],
#         'description': 'AMSChange',
#     },
#     'AmsPerformance': {
#         'region': [EU, NA, FE],
#         'description': 'AMSPerformance',
#     },
#     'Payment': {
#         'region': [DEFAULT_REGION],
#         'test': True,
#         'description': 'Payment Processing',
#         'function': 'PaymentProcessor'
#     }
# }