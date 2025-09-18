# mapping.py
"""
Maps function names to their deployment configuration, including AWS region and other metadata.
"""
from enum import Enum
from typing import List, Literal

from dzgroshared.db.enums import ENVIRONMENT
from dzgroshared.db.queue_messages.model import QueueMessageModelType
from dzgroshared.sqs.model import QueueName
from dzgroshared.storage.model import S3Bucket
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class Tag(BaseModel):
    Project: str = 'Dzgro'
    Environment: ENVIRONMENT

class LAYER_NAME(str, Enum):
    API = "ApiLayer"
    MANGUM  = "MangumLayer"
    DZGRO_SHARED = "DzgroSharedLayer"
    PYMONGO = "PymongoLayer"
    INVOICE_GENERATOR = "InvoiceGeneratorLayer"

LAYER_DEPENDENCIES = {
    LAYER_NAME.PYMONGO: ["pymongo==4.15.0"],
    LAYER_NAME.INVOICE_GENERATOR: [
        "num2words==0.5.14",
        "reportlab==4.4.3"
    ],
    LAYER_NAME.MANGUM: ["mangum==0.19.0"]
}

class LambdaName(str, Enum):
    Api = "Api"
    CognitoCustomMessage = "CognitoCustomMessage"
    CognitoTrigger = "CognitoTrigger"
    QueueModelMessageProcessor = "QueueModelMessageProcessor"
    DzgroReportsS3Trigger = "DzgroReportsS3Trigger"
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
    
class S3LifeCycleRule(BaseModel):
    Rules: list[dict]

class S3Role(str, Enum):
    GetObject = "s3:GetObject"
    PutObject = "s3:PutObject"
    ListBucket = "s3:ListBucket"
    DeleteObject = "s3:DeleteObject"

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
    method: Literal['POST', 'GET', 'PUT', 'DELETE', 'PATCH', 'ANY']
    path: str
    parameters: dict|SkipJsonSchema[None]=None

    
class APIGatewaySQSTrigger(ApiGatewayRoute):
    headers: list[str] = []
    modeltype: QueueMessageModelType|SkipJsonSchema[None]=None

class QueueProperty(BaseModel):
    name: QueueName
    roles: list[QueueRole] 
    visibilityTimeout: int = 900
    maxReceiveCount: int = 1
    policy: dict|SkipJsonSchema[None]=None
    apiTrigger: list[APIGatewaySQSTrigger]|SkipJsonSchema[None]=None

class S3TriggerEvent(BaseModel):
    eventName: str
    filter: dict|SkipJsonSchema[None]=None

class S3Method(str, Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"
    HEAD = "HEAD"

class S3CorsRule(BaseModel):
    methods: list[S3Method]

class S3Property(BaseModel):
    name: S3Bucket
    roles: list[S3Role]
    trigger: S3TriggerEvent|SkipJsonSchema[None]=None
    lifeCycleConfiguration: S3LifeCycleRule|SkipJsonSchema[None]=None
    cors: S3CorsRule|SkipJsonSchema[None]=None

class LambdaRegion(BaseModel):
    region: Region
    description: str = "General Description"
    queue: List[QueueProperty] = []
    s3: List[S3Property] = []
    api: ApiGatewayRoute|SkipJsonSchema[None]=None

class LambdaProperty(BaseModel):
    name: LambdaName
    memorySize: int = 128
    timeout: int = 900
    regions: List[LambdaRegion]
    env: List[ENVIRONMENT] = [ENVIRONMENT.DEV, ENVIRONMENT.TEST, ENVIRONMENT.PROD, ENVIRONMENT.LOCAL]
    layers: List[LAYER_NAME] = []

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
        name=LambdaName.CognitoCustomMessage,
        memorySize=256,
        timeout=30,
        layers = [],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT
            ),
        ],
        env = [ENVIRONMENT.DEV, ENVIRONMENT.TEST, ENVIRONMENT.PROD]
    ),
    LambdaProperty(
        name=LambdaName.CognitoTrigger,
        memorySize=512,
        timeout=10,
        layers = [LAYER_NAME.PYMONGO],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT
            ),
        ],
        env = [ENVIRONMENT.DEV, ENVIRONMENT.TEST, ENVIRONMENT.PROD]
    ),
    LambdaProperty(
        name=LambdaName.Api,
        memorySize=1024,
        timeout=30,
        layers = [LAYER_NAME.API,LAYER_NAME.MANGUM, LAYER_NAME.DZGRO_SHARED],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                api = ApiGatewayRoute(
                    method='ANY',
                    path='/api/{proxy+}',
                ),
                queue = [QueueProperty(name=name, roles=QueueRole.all()) for name in QueueName.all()],
                s3 = [S3Property(name=name, roles=S3Role.all()) for name in S3Bucket.all()]
            )
        ],
        env = [ENVIRONMENT.TEST, ENVIRONMENT.DEV]
    ),
    LambdaProperty(
        name=LambdaName.QueueModelMessageProcessor,
        layers = [LAYER_NAME.INVOICE_GENERATOR, LAYER_NAME.DZGRO_SHARED],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                queue=[
                    QueueProperty(
                        name=QueueName.AMAZON_REPORTS,
                        roles=QueueRole.all()
                    ),
                    QueueProperty(
                        name=QueueName.DAILY_REPORT_REFRESH_BY_COUNTRY_CODE,
                        roles=QueueRole.all()
                    ),
                    QueueProperty(
                        name=QueueName.DZGRO_REPORTS,
                        roles=QueueRole.all()
                    ),
                    QueueProperty(
                name=QueueName.RAZORPAY_WEBHOOK,
                roles=QueueRole.all(),
                apiTrigger=[
                    APIGatewaySQSTrigger(
                        method='POST',
                        path='/webhook/rzrpay/order/paid',
                        headers=['x-razorpay-event-id', 'X-Razorpay-Signature'],
                        modeltype=QueueMessageModelType.ORDER_PAID
                    ),
                    APIGatewaySQSTrigger(
                        method='POST',
                        path='/webhook/rzrpay/invoice/paid',
                        headers=['x-razorpay-event-id', 'X-Razorpay-Signature'],
                        modeltype=QueueMessageModelType.INVOICE_PAID
                    ),
                    APIGatewaySQSTrigger(
                        method='POST',
                        path='/webhook/rzrpay/invoice/expired',
                        headers=['x-razorpay-event-id', 'X-Razorpay-Signature'],
                        modeltype=QueueMessageModelType.INVOICE_EXPIRED
                    )
                ]
            )
                ],
                s3=[S3Property(name=S3Bucket.AMAZON_REPORTS, roles=S3Role.all())]
            )
        ]
    ),
    LambdaProperty(
        name=LambdaName.DzgroReportsS3Trigger,
        layers = [LAYER_NAME.DZGRO_SHARED],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                s3=[S3Property(
                    name=S3Bucket.DZGRO_REPORTS, 
                    roles=S3Role.all(), 
                    trigger=S3TriggerEvent(
                        eventName="s3:ObjectCreated:*",
                        filter={ "S3Key": { "Rules": [ { "Name": "suffix", "Value": ".csv" } ] } }
                    ),
                    lifeCycleConfiguration = S3LifeCycleRule(
                        Rules=[
                            {
                                "Id": "ExpireAfter3Days",
                                "Status": "Enabled",
                                "ExpirationInDays": 3
                            }
                        ]
                    )
                )]
            ),
        ]
    ),
    LambdaProperty(
        name=LambdaName.AmsChange,
        layers = [LAYER_NAME.PYMONGO],
        regions=[
            LambdaRegion(
                region=region,
                queue=[QueueProperty(
                    name=QueueName.AMS_CHANGE,
                    roles=QueueRole.read(),
                    policy = getAMSChangeSetPolicy(region)
                )],
            ) for region in Region.others()
        ],
    ),
    LambdaProperty(
        name=LambdaName.AmsPerformance,
        layers = [LAYER_NAME.PYMONGO],
        regions=[
            LambdaRegion(
                region=region,
                queue=[QueueProperty(
                    name=QueueName.AMS_PERFORMANCE,
                    roles=QueueRole.read(),
                    policy = getAMSPerformancePolicy(region)
                )],
            ) for region in Region.others()
        ],
    ),
]