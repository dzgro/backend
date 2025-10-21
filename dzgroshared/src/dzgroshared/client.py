from bson import ObjectId
from dzgroshared.db.marketplaces.model import MarketplaceCache
from dzgroshared.db.users.model import User
from dzgroshared.db.enums import ENVIRONMENT
from dzgroshared.db.model import LambdaContext, PyObjectId
from dzgroshared.razorpay.client import RazorpayClient
from dzgroshared.secrets.model import DzgroSecrets
from motor.motor_asyncio import AsyncIOMotorClient


class DzgroSharedClient:
    ACCOUNT_ID: str
    REGION: str
    env: ENVIRONMENT
    DB_NAME: str
    uid: str
    user: User
    marketplace: MarketplaceCache
    marketplaceId: ObjectId
    mongoClient: AsyncIOMotorClient
    mongoFedClient: AsyncIOMotorClient
    secretsClient: DzgroSecrets

    def __init__(self, env: ENVIRONMENT):
        self.env = env
        self.ACCOUNT_ID = "522814698847"
        self.REGION = "ap-south-1"
        self.DB_NAME = f'dzgro-{self.env.value}'

        
    def __getattr__(self, item):
        return None
    
    def setUid(self, uid: str):
        self.uid = uid
    
    def setUser(self, user: User):
        self.user= user
        self.setUid(user.id)

    def setMarketplace(self, marketplace: MarketplaceCache):
        self.marketplace = marketplace
        self.setMarketplaceId(marketplace.id)

    def setMarketplaceId(self, marketplaceId: ObjectId|PyObjectId):
        self.marketplaceId = marketplaceId if isinstance(marketplaceId, ObjectId) else ObjectId(marketplaceId)

    def setSecretsClient(self, secretsClient: DzgroSecrets):
        self.secretsClient = secretsClient

    def setMongoClient(self, mongoClient: AsyncIOMotorClient):
        self.mongoClient = mongoClient

    def setFedClient(self, mongoFedClient: AsyncIOMotorClient):
        self.mongoFedClient = mongoFedClient

    @property
    def secrets(self):
        if self.secretsClient: return self.secretsClient
        from dzgroshared.secrets.client import SecretManager
        self.secretsClient = SecretManager(self.env).secrets
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
        self.s3 = S3Storage(self)
        return self.s3
    
    @property
    def razorpay(self):
        if self.razorpayClient: return self.razorpayClient
        key = self.secrets.RAZORPAY_CLIENT_ID if self.env == ENVIRONMENT.PROD else self.secrets.RAZORPAY_CLIENT_ID
        secret = self.secrets.RAZORPAY_CLIENT_SECRET if self.env == ENVIRONMENT.PROD else self.secrets.RAZORPAY_CLIENT_SECRET
        self.razorpayClient = RazorpayClient(key, secret)
        return self.razorpayClient
    
    @property
    def fedDb(self):
        if self.fedDbClient: return self.fedDbClient
        if not self.mongoFedClient:
            try:
                print("Connecting to Fed MongoDB...")
                self.mongoFedClient = AsyncIOMotorClient(self.secrets.MONGO_DB_FED_CONNECT_URI)
            except Exception as e:
                print(f"Error connecting to Fed MongoDB: {e}")
                raise e
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