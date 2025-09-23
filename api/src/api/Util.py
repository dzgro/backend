from bson import ObjectId
from dzgroshared.db.marketplaces.model import MarketplaceCache
from dzgroshared.db.users.model import User, UserBasicDetails
from dzgroshared.db.enums import ENVIRONMENT
from dzgroshared.razorpay.customer.model import RazorpayCreateCustomer
from dzgroshared.razorpay.client import RazorpayClient
from fastapi import Request
from fastapi.exceptions import HTTPException
import jwt   
from dzgroshared.secrets.model import DzgroSecrets
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
MARKETING_MISSING = HTTPException(status_code=403, detail="Missing Marketplace ID")
UID_MISSING = HTTPException(status_code=403, detail="Missing User ID")
INVALID_MARKETPLACE = HTTPException(status_code=403, detail="Invalid Marketplace for this user")
from cachetools import TTLCache
MARKETPLACE_CACHE  = TTLCache(maxsize=10000, ttl=600)
USER_CACHE  = TTLCache(maxsize=10000, ttl=600)

class RequestHelper:
    request: Request
    excludedPath: bool = False
    
    # Routes that don't require authentication
    EXCLUDED_ROUTES = {
        "/pricing"  # Add your routes here
    }

    def __init__(self, request: Request):
        self.request = request
        self.excludedPath = self._should_exclude_auth(request)
        if not self.excludedPath:
            self.uid = self.__uid(request)
            self.marketplaceId = self.__marketplace(request)


    def __getattr__(self, name):
        return None

    def _should_exclude_auth(self, request: Request) -> bool:
        """Check if the current route should exclude authentication"""
        return any(request.url.path.startswith(route) for route in self.EXCLUDED_ROUTES)
    
    @property
    def secrets(self)->DzgroSecrets:
        return self.request.app.state.secrets
    
    @property
    def env(self)->ENVIRONMENT:
        return self.request.app.state.env

    @property
    def mongoClient(self)->AsyncIOMotorClient:
        return self.request.app.state.mongoClient

    @property
    def razorpayClient(self)->RazorpayClient:
        razorpay_client = getattr(self.request.app.state, "razorpayClient", None)
        if razorpay_client is None:
            key = self.secrets.RAZORPAY_CLIENT_ID if self.env == ENVIRONMENT.PROD else self.secrets.RAZORPAY_CLIENT_ID
            secret = self.secrets.RAZORPAY_CLIENT_SECRET if self.env == ENVIRONMENT.PROD else self.secrets.RAZORPAY_CLIENT_SECRET
            self.request.app.state.razorpayClient = RazorpayClient(key, secret)
        return self.request.app.state.razorpayClient
    
    @property
    def DB_NAME(self)->str:
        return f'dzgro-{self.env.value}' if self.env != ENVIRONMENT.LOCAL else 'dzgro-dev'

    async def _createRazorpayCustomer(self, user:UserBasicDetails, collection: AsyncIOMotorCollection):
        customerReq = RazorpayCreateCustomer(name=user.name, email=user.email, contact=user.phone_number)
        customer = await self.razorpayClient.customer.create_customer(customerReq)
        await collection.update_one({"_id": self.uid}, {"$set": {"customerid": customer.id}})
        return customer.id
    
    async def __userCache(self):
        if self.uid in USER_CACHE: return USER_CACHE[self.uid]
        users = self.mongoClient[self.DB_NAME]['users']
        doc = await users.find_one({"_id": self.uid})
        if not doc: raise UID_MISSING
        if 'customerid' not in doc:
            doc['customerid'] = await self._createRazorpayCustomer(UserBasicDetails.model_validate(doc), users)
        user = User.model_validate(doc)
        USER_CACHE[self.uid] = user
        return user

    def __marketplace(self, request: Request):
        marketplaceId = request.headers.get("marketplace")
        if marketplaceId: return ObjectId(marketplaceId)
            
    async def __marketplaceCache(self)->MarketplaceCache:
        marketplaceId = str(self.marketplaceId)
        if marketplaceId in MARKETPLACE_CACHE: return MARKETPLACE_CACHE[marketplaceId]
        marketplaces = self.mongoClient[self.DB_NAME]['marketplaces']
        doc = await marketplaces.find_one({"_id": self.marketplaceId, "uid": self.uid})
        if not doc: raise INVALID_MARKETPLACE
        if doc.get('uid') != self.uid: raise INVALID_MARKETPLACE
        marketplace = MarketplaceCache.model_validate(doc)
        MARKETPLACE_CACHE[marketplaceId] = marketplace
        return marketplace
    
    def __uid(self, request: Request):
        client: jwt.PyJWKClient = request.app.state.jwtClient
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        token = parts[1]
        return self.__getUid(client, token)

    def __getUid(self, client:jwt.PyJWKClient, token:str) -> str:
        header = jwt.get_unverified_header(token)
        key = client.get_signing_key(header["kid"]).key
        payload = jwt.decode(token, key, [header["alg"]])
        return payload['username']
    

    @property
    async def client(self):
        from dzgroshared.client import DzgroSharedClient
        client = DzgroSharedClient(self.env)
        if not self.excludedPath:
            user = await self.__userCache()
            client.setUser(user)
            if self.marketplaceId:
                marketplace = await self.__marketplaceCache()
                client.setMarketplace(marketplace)
        client.setSecretsClient(self.secrets)
        client.setMongoClient(self.mongoClient)
        return client