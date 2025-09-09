from bson import ObjectId
from dzgroshared.models.collections.marketplaces import MarketplaceCache
from dzgroshared.models.enums import ENVIRONMENT
from fastapi import Request
from fastapi.exceptions import HTTPException
import jwt   
from dzgroshared.models.model import DzgroSecrets, PyObjectId
from motor.motor_asyncio import AsyncIOMotorClient
MARKETING_MISSING = HTTPException(status_code=403, detail="Missing Marketplace ID")
UID_MISSING = HTTPException(status_code=403, detail="Missing User ID")
INVALID_MARKETPLACE = HTTPException(status_code=403, detail="Invalid Marketplace for this user")
from cachetools import TTLCache
MARKETPLACE_CACHE  = TTLCache(maxsize=10000, ttl=600)

class RequestHelper:
    request: Request
    
    # Routes that don't require authentication
    EXCLUDED_ROUTES = {
        "/pricing"  # Add your routes here
    }

    def __init__(self, request: Request):
        self.request = request
        if not self._should_exclude_auth(request):
            self.uid = self.__uid(request)
            self.marketplaceId = self.__marketplace(request)


    def __getattr__(self, name):
        return None

    def _should_exclude_auth(self, request: Request) -> bool:
        """Check if the current route should exclude authentication"""
        path = request.url.path
        return path in self.EXCLUDED_ROUTES or any(path.startswith(route) for route in self.EXCLUDED_ROUTES)
    
    @property
    def secrets(self)->DzgroSecrets:
        return self.request.app.state.secrets
    
    @property
    def env(self)->ENVIRONMENT:
        return self.request.app.state.env

    @property
    def mongoClient(self)->AsyncIOMotorClient:
        return self.request.app.state.mongoClient

    def __marketplace(self, request: Request):
        marketplaceId = request.headers.get("marketplace")
        if marketplaceId: return ObjectId(marketplaceId)
            
    async def __marketplaceCache(self)->MarketplaceCache:
        key = f"{self.uid}:{str(self.marketplaceId)}"
        if key in MARKETPLACE_CACHE: return MARKETPLACE_CACHE [key]
        DB_NAME = f'dzgro-{self.env.value.lower()}' if self.env != ENVIRONMENT.LOCAL else 'dzgro-dev'
        doc = await self.mongoClient[DB_NAME]['marketplaces'].find_one({"_id": self.marketplaceId, "uid": self.uid})
        if not doc: raise INVALID_MARKETPLACE
        cache = MarketplaceCache.model_validate(doc)
        MARKETPLACE_CACHE[key] = cache
        return cache
    
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
        client.setUid(self.uid)
        if self.marketplaceId:
            cache = await self.__marketplaceCache()
            client.setMarketplace(cache)
        client.setSecretsClient(self.secrets)
        client.setMongoClient(self.mongoClient)
        return client