from bson import ObjectId
from dzgroshared.models.enums import ENVIRONMENT
from dzgroshared.models.model import DzgroSecrets, LambdaContext
from motor.motor_asyncio import AsyncIOMotorClient


class DzgroSharedClient:
    env: ENVIRONMENT
    uid: str
    marketplace: ObjectId
    mongoClient: AsyncIOMotorClient
    secretsClient: DzgroSecrets

    def __init__(self, env: ENVIRONMENT):
        self.env = env
        
    def __getattr__(self, item):
        return None
    
    def setUid(self, uid: str):
        self.uid = uid

    def setMarketplace(self, marketplace: ObjectId):
        self.marketplace = marketplace

    def setSecretsClient(self, secretsClient: DzgroSecrets):
        self.secretsClient = secretsClient

    def setMongoClient(self, mongoClient: AsyncIOMotorClient):
        self.mongoClient = mongoClient

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
        if not self.mongoClient:
            self.mongoClient = AsyncIOMotorClient(self.secrets.MONGO_DB_CONNECT_URI)
        self.dbClient = DbClient(self)
        return self.dbClient
    
    def spapi(self, object):
        if self.spapiClient: return self.spapiClient
        from dzgroshared.amazonapi.spapi import SpApiClient
        self.spapiClient = SpApiClient(object)
        return self.spapiClient
    
    def adapi(self, object):
        if self.adapiClient: return self.adapiClient
        from dzgroshared.amazonapi.adapi import AdApiClient
        self.adapiClient = AdApiClient(object)
        return self.adapiClient

    def functions(self, event: dict, context: LambdaContext):
        from dzgroshared.functions import FunctionClient
        return FunctionClient(self, event, context)