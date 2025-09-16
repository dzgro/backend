# mapping.py
"""
Maps function names to their deployment configuration, including AWS region and other metadata.
"""
from enum import Enum
from typing import Literal

from dzgroshared.db.enums import ENVIRONMENT
from dzgroshared.sqs.model import QueueName
from dzgroshared.storage.model import S3Bucket
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class Tag(BaseModel):
    Project: str = 'Dzgro'
    Environment: ENVIRONMENT


class LambdaName(str, Enum):
    CognitoTrigger = "CognitoTrigger"
    AmazonDailyReport = "AmazonDailyReport"
    DzgroReports = "DzgroReports"
    DzgroReportsS3Trigger = "DzgroReportsS3Trigger"
    RazorpayWebhookProcessor = "RazorpayWebhookProcessor"
    AmsChange = "AmsChange"
    AmsPerformance = "AmsPerformance"
    DailyReportRefreshByCountryCode = "DailyReportRefreshByCountryCode"


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

class S3TriggerEvent(BaseModel):
    eventName: str
    filter: dict|SkipJsonSchema[None]=None

class S3CorsRule(BaseModel):
    methods = list[Literal['GET', 'PUT', 'POST', 'DELETE', 'HEAD']]

class S3Property(BaseModel):
    name: S3Bucket
    roles: list[S3Role]
    trigger: S3TriggerEvent|SkipJsonSchema[None]=None
    lifeCycleConfiguration: S3LifeCycleRule|SkipJsonSchema[None]=None
    cors: S3CorsRule|SkipJsonSchema[None]=None

class LambdaRegion(BaseModel):
    region: Region
    memorySize: int = 128
    timeout: int = 900
    description: str = "General Description"
    queue: QueueProperty|SkipJsonSchema[None]=None
    s3: S3Property|SkipJsonSchema[None]=None
    api: ApiGatewayRoute|SkipJsonSchema[None]=None

class LambdaRequirement(BaseModel):
    name: str
    version: str

class LambdaProperty(BaseModel):
    name: LambdaName
    regions: list[LambdaRegion]
    env: list[ENVIRONMENT] = [ENVIRONMENT.DEV, ENVIRONMENT.TEST, ENVIRONMENT.PROD, ENVIRONMENT.LOCAL]
    requirements: list[LambdaRequirement]|SkipJsonSchema[None]=None
    skipSharedLibraries: bool = False

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
        name=LambdaName.CognitoTrigger,
        requirements=[
            LambdaRequirement(name="pymongo", version="4.15.0")
        ],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT
            ),
        ],
        skipSharedLibraries=True,
        env = [ENVIRONMENT.PROD]
    ),
    LambdaProperty(
        name=LambdaName.AmazonDailyReport,
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                queue=QueueProperty(
                    name=QueueName.AMAZON_REPORTS,
                    roles=QueueRole.all()
                ),
                s3=S3Property(name=S3Bucket.AMAZON_REPORTS, roles=S3Role.all())
            )
        ]
    ),
    LambdaProperty(
        name=LambdaName.DzgroReports,
        regions=[LambdaRegion(
            region=Region.DEFAULT,
            queue=QueueProperty(
                name=QueueName.DZGRO_REPORTS,
                roles=QueueRole.all()
            ),
        )],
    ),
    LambdaProperty(
        name=LambdaName.DzgroReportsS3Trigger,
        requirements=[
            LambdaRequirement(name="pandas", version="2.3.2"),
            LambdaRequirement(name="openpyxl", version="3.1.5")
        ],
        regions=[
            LambdaRegion(
                region=Region.DEFAULT,
                s3=S3Property(
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
                )
            ),
        ]
    ),
    LambdaProperty(
        name=LambdaName.RazorpayWebhookProcessor,
        requirements=[
            LambdaRequirement(name="num2words", version="0.5.14"),
            LambdaRequirement(name="reportlab", version="4.4.3")
        ],
        regions=[LambdaRegion(
            region=Region.DEFAULT,
            queue=QueueProperty(
                name=QueueName.RAZORPAY_WEBHOOK,
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
                    name=QueueName.AMS_CHANGE,
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
                    name=QueueName.AMS_PERFORMANCE,
                    roles=QueueRole.read(),
                    policy = getAMSPerformancePolicy(region)
                ),
            ) for region in Region.others()
        ],
    ),
    LambdaProperty(
        name=LambdaName.DailyReportRefreshByCountryCode,
        regions=[
            LambdaRegion(
                region=region,
                queue=QueueProperty(
                    name=QueueName.DAILY_REPORT_REFRESH_BY_COUNTRY_CODE,
                    roles=QueueRole.read(),
                ),
            ) for region in Region.others()
        ],
    )

]