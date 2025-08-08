from db import DbClient
from bson import ObjectId
from fastapi import Request
from fastapi.exceptions import HTTPException
import jwt   
from dzgrosecrets import DzgroSecrets
MARKETING_MISSING = HTTPException(status_code=401, detail="Missing Marketplace ID")
UID_MISSING = HTTPException(status_code=401, detail="Missing User ID")

class RequestHelper:
    request: Request
    dbClient: DbClient
    uid: str
    marketplace: ObjectId|None

    # Routes that don't require authentication
    EXCLUDED_ROUTES = {
        "/pricing"  # Add your routes here
    }

    def __init__(self, request: Request):
        self.request = request
        self.dbClient = request.app.state.dbClient
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
    def user(self):
        if not self.uid: raise UID_MISSING
        return self.dbClient.user(self.uid)
    
    @property
    def country_details(self):
        return self.dbClient.country_details()
    
    @property
    def pricing(self):
        return self.dbClient.pricing()
    
    @property
    def calculation_keys(self):
        return self.dbClient.calculation_keys()
    
    @property
    def marketplaces(self):
        if not self.uid: raise UID_MISSING
        return self.dbClient.marketplaces(self.uid)

    @property
    def subscriptions(self):
        if not self.uid: raise UID_MISSING
        return self.dbClient.subscriptions(self.uid)

    @property
    def payments(self):
        if not self.uid: raise UID_MISSING
        return self.dbClient.payments(self.uid)
    
    @property
    def advertising_accounts(self):
        if not self.uid: raise UID_MISSING
        return self.dbClient.advertising_accounts(self.uid)
    
    @property
    def spapi_accounts(self):
        if not self.uid: raise UID_MISSING
        return self.dbClient.spapi_accounts(self.uid)
    
    @property
    def health(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.health(self.uid, self.marketplace)
    
    @property
    def analytics(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.analytics(self.uid, self.marketplace)
    
    @property
    def ad_structure(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.ad_structure(self.uid, self.marketplace)
    
    @property
    def query_results(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.query_results(self.uid, self.marketplace)
    
    @property
    def queries(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.queries(self.uid, self.marketplace)
    
    @property
    def reports(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.reports(self.uid, self.marketplace)
    
    @property
    def ad_assets(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.adv_assets(self.uid, self.marketplace)

    @property
    def ad_rule_utility(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.ad_rule_utility(self.uid, self.marketplace)

    @property
    def ad_rule_run_utility(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.ad_rule_run_utility(self.uid, self.marketplace)

    @property
    def ad_rule_criteria_groups(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.ad_rule_criteria_groups(self.uid, self.marketplace)

    @property
    def ad_rule_run_results(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.ad_rule_run_results(self.uid, self.marketplace)

    @property
    def ad_ad_group_mapping(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.ad_ad_group_mapping(self.uid, self.marketplace)

    @property
    def products(self):
        if not self.uid: raise UID_MISSING
        if not self.marketplace: raise MARKETING_MISSING
        return self.dbClient.products(self.uid, self.marketplace)
