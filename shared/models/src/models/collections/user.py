from pydantic.json_schema import SkipJsonSchema
from models.collections.pricing import PlanDetails
from models.model import ItemId, ItemIdWithDate, ObjectIdStr
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List
from models.enums import CountryCode, MarketplaceStatus, OnboardStep, RazorpaySubscriptionStatus, AmazonAccountType, MarketplaceId, PlanDuration,BusinessType
from enum import Enum



class UserDetails(BaseModel):
    name: str
    username: str
    phoneNumber: str
    email: str
    groups: list[str]

    @model_validator(mode="before")
    def setGroups(cls,v):
        if not v.get('groups'): v['groups'] = v.get('cognito:groups',[])
        return v

class GSTDetails(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15)
    name: str
    addressline1: str
    addressline2: str
    addressline3: str
    pincode: str
    city: str
    state: str
    
class User(ObjectIdStr):
    model_config = ConfigDict(populate_by_name=True)
    details: UserDetails

    @model_validator(mode="after")
    def setRoles(self):
        # self.canOnboard = self.subscriptionId is None and self.isAdmin
        # self.details.isAdmin = self.details.parent == self.id
        return self
    
class UserList(BaseModel):
    users: list[User]
    token: str|SkipJsonSchema[None] = None


class MarketplaceSeller(ItemIdWithDate):
    name: str
    countrycode: CountryCode
    sellerid:str

class UserMarketplace(ItemIdWithDate):
    uid:str
    countrycode: CountryCode
    marketplaceid: str
    profileid: int
    seller: MarketplaceSeller
    status: MarketplaceStatus
    storename: str|SkipJsonSchema[None]=None
    startdate: datetime|SkipJsonSchema[None]=None
    enddate: datetime|SkipJsonSchema[None]=None

class AdAccountEntity(ItemId):
    accountname: str
    countrycode: CountryCode
    entityid:str

class AdvertisingAccount(ItemIdWithDate):
    name: str
    countrycode: CountryCode


class BusinessDetails(BaseModel):
    businesstype: BusinessType|SkipJsonSchema[None]=None
    business: GSTDetails|SkipJsonSchema[None]=None

class UserWithAccounts(BusinessDetails):
    spapi: List[MarketplaceSeller]
    marketplaces: List[UserMarketplace]
    ad: List[AdvertisingAccount]
    status: RazorpaySubscriptionStatus|SkipJsonSchema[None]=None
    onboard: OnboardStep|SkipJsonSchema[None]=None
    onboardsteps: list[OnboardStep] = OnboardStep.values()

    @model_validator(mode="after")
    def setOnboardStep(self):
        if len(self.spapi)==0: self.onboard = OnboardStep.ADD_SPAPI_ACCOUNT
        elif len(self.ad)==0: self.onboard = OnboardStep.ADD_AD_ACCOUNT
        elif len(self.marketplaces)==0: self.onboard = OnboardStep.ADD_MARKETPLACE
        elif not self.businesstype: self.onboard = OnboardStep.ADD_GST_DETAILS
        elif not self.status: self.onboard = OnboardStep.SUBSCRIBE
        return self

class PlanWithCurrency(PlanDetails):
    currency: str
    currencyCode: str
    
class UserProfileWithSubscription(BaseModel):
    businesstype: BusinessType
    business: GSTDetails|SkipJsonSchema[None]=None
    plan: PlanWithCurrency
    duration: PlanDuration
    status: RazorpaySubscriptionStatus
