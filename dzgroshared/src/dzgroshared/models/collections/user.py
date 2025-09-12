from dzgroshared.models.collections.advertising_accounts import AdvertisingAccount, AdvertisingAccountBasic
from dzgroshared.models.collections.marketplaces import UserMarketplaceBasic
from dzgroshared.models.collections.spapi_accounts import SPAPIAccount
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.model import ObjectIdStr
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List
from dzgroshared.models.enums import CountryCode
from enum import Enum


class OnboardStep(str, Enum):
    ADD_SPAPI_ACCOUNT = 'Add Seller Central Account'
    ADD_AD_ACCOUNT = 'Add Advertising Account'
    ADD_MARKETPLACE = 'Add Marketplace'

    @staticmethod
    def values():
        return list(OnboardStep)
    
class TempAccountRequest(BaseModel):
    countrycode: CountryCode
    name: str
    state: str|SkipJsonSchema[None] = None

class UserBasicDetails(BaseModel):
    name: str
    phoneNumber: str
    email: str
    customerid: str
    groups: list[str] = Field(alias='cognito:groups', default_factory=list)

class MarketplaceOnboarding(BaseModel):
    spapi: List[SPAPIAccount]
    marketplaces: List[UserMarketplaceBasic]
    ad: List[AdvertisingAccount]
    step: OnboardStep|SkipJsonSchema[None]=None
    onboardsteps: List[OnboardStep] = OnboardStep.values()

class User(ObjectIdStr, UserBasicDetails):
    pass

class UserList(BaseModel):
    users: list[User]
    token: str|SkipJsonSchema[None] = None