from dzgroshared.db.advertising_accounts.model import AdvertisingAccount
from dzgroshared.db.marketplaces.model import UserMarketplaceBasic
from dzgroshared.db.spapi_accounts.model import SPAPIAccount
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import ObjectIdStr
from pydantic import BaseModel, Field
from typing import List
from dzgroshared.db.enums import CountryCode
from enum import Enum



class UserStatus(str, Enum):
    PENDING_ONBOARDING = 'Pending Onboarding'
    PAID = 'Paid'
    OVERDUE = 'Overdue'
    SUSPENDED = 'Suspended'


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
    status: UserStatus
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