from bson import ObjectId
from fastapi import Request
from fastapi.exceptions import HTTPException
import jwt   
from dzgroshared.models.model import DzgroSecrets
from motor.motor_asyncio import AsyncIOMotorClient
MARKETING_MISSING = HTTPException(status_code=401, detail="Missing Marketplace ID")
UID_MISSING = HTTPException(status_code=401, detail="Missing User ID")

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
            self.marketplace = self.__marketplace(request) if self.uid else None

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
    def mongoClient(self)->AsyncIOMotorClient:
        return self.request.app.state.mongoClient

    def __marketplace(self, request: Request):
        marketplaceId = request.headers.get("marketplace")
        return ObjectId(marketplaceId) if marketplaceId else None
    
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
    def client(self):
        from dzgroshared.client import DzgroSharedClient
        from dzgroshared.models.enums import ENVIRONMENT
        client = DzgroSharedClient(ENVIRONMENT.DEV)
        client.setUid(self.uid)
        if self.marketplace: client.setMarketplace(self.marketplace)
        client.setSecretsClient(self.secrets)
        client.setMongoClient(self.mongoClient)
        return client

