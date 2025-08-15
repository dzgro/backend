from bson import ObjectId
from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.models.enums import ENVIRONMENT
from dzgroshared.models.model import LambdaContext


class DzgroSharedClient:
    env: ENVIRONMENT
    uid: str|None
    marketplace: ObjectId|None

    def __init__(self, env: ENVIRONMENT = ENVIRONMENT.DEV, uid: str|None = None, marketplace: ObjectId|None = None):
        self.env = env
        self.uid = uid
        self.marketplace = marketplace

    def __getattr__(self, item):
        return None

    @property
    def secrets(self):
        if self.secretsClient: return self.secretsClient
        from dzgroshared.secrets.client import SecretManager
        self.secretsClient = SecretManager().secrets
        return self.secretsClient
    
    @property
    def cognito(self):
        if self.cognitoClient: return self.cognitoClient
        from dzgroshared.cognito.client import CognitoManager
        self.cognitoClient = CognitoManager(self.secrets.COGNITO_APP_CLIENT_ID, self.secrets.COGNITO_USER_POOL_ID)
        return self.cognitoClient
        
    @property
    def sqs(self):
        if self.sqsClient: return self.sqsClient
        from dzgroshared.sqs.client import SqsHelper
        self.sqsClient = SqsHelper(self)
        return self.sqsClient

    @property
    def storage(self):
        if self.s3: return self.s3
        from dzgroshared.storage.client import S3Storage
        self.s3 = S3Storage()
        return self.s3
    
    @property
    def razorpay(self):
        if self.razorpayClient: return self.razorpayClient
        from dzgroshared.razorpay.client import RazorpayClient
        self.razorpayClient = RazorpayClient(self.secrets.RAZORPAY_CLIENT_ID, self.secrets.RAZORPAY_CLIENT_SECRET)
        return self.razorpayClient
    
    @property
    def fedDb(self):
        if self.fedDbClient: return self.fedDbClient
        from dzgroshared.fed_db.client import FedDbClient
        self.fedDbClient = FedDbClient(self)
        return self.fedDbClient
    
    @property
    def db(self):
        if self.dbClient: return self.dbClient
        from dzgroshared.db.client import DbClient
        self.dbClient = DbClient(self, uid=self.uid, marketplace=self.marketplace)
        return self.dbClient
    
    def amazonapi(self, object: AmazonApiObject):
        if self.amazonapiClient: return self.amazonapiClient
        from dzgroshared.amazonapi import AmazonApiClient
        self.amazonapiClient = AmazonApiClient(object)
        return self.amazonapiClient
    
    def functions(self, event: dict, context: LambdaContext):
        from dzgroshared.functions import FunctionClient
        return FunctionClient(self, event, context)