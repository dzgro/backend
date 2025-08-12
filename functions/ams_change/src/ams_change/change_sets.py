from models.collections.marketplaces import Marketplace
from models.enums import AMSDataSet, AdAssetType
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from models.enums import AdState
from db import DbClient


class Audit(BaseModel):
    creationDateTime: str | SkipJsonSchema[None] = None
    lastUpdatedDateTime: str | SkipJsonSchema[None] = None

class MonetaryBudget(BaseModel):
    amount: float | SkipJsonSchema[None] = None
    currencyCode: str | SkipJsonSchema[None] = None

class BudgetCap(BaseModel):
    monetaryBudget: MonetaryBudget | SkipJsonSchema[None] = None

class Budget(BaseModel):
    budgetCap: BudgetCap | SkipJsonSchema[None] = None


class CampaignDataSet(BaseModel):
    campaignId: str
    portfolioId: str | SkipJsonSchema[None] = None
    name: str
    state: AdState
    budget: Budget
    audit: Audit

    @model_validator(mode="after")
    def validate_portfolioId(self):
        if self.portfolioId:
            self.portfolioId = None if not self.portfolioId.strip() else self.portfolioId
        return self

class DefaultBid(BaseModel):
    value: float

class AdGroupBidValue(BaseModel):
    defaultBid: DefaultBid

class AdGroupDataSet(BaseModel):
    adGroupId: str
    name: str
    state: AdState
    bidValue: AdGroupBidValue | SkipJsonSchema[None] = None
    audit: Audit

class AdDataSet(BaseModel):
    adId: str
    name: str | SkipJsonSchema[None] = None
    state: AdState
    audit: Audit

class TargetDataSet(BaseModel):
    targetId: str
    bid: float
    state: AdState
    audit: Audit

class ChangeSet:
    dataSet: AMSDataSet
    sellerid: str
    marketplaceId: str
    body: dict
    dbClient: DbClient

    def __init__(self, db: DbClient, dataSet: AMSDataSet, sellerid: str, marketplaceId: str, body: dict):
        self.dataSet = dataSet
        self.sellerid = sellerid
        self.marketplaceId = marketplaceId
        self.body = body
        self.dbClient = db

    async def getUidMarketplaces(self):
        coll = self.dbClient.db['marketplaces']
        return (await coll.find({
            "sellerid": self.sellerid,
            "marketplaceid": self.marketplaceId
        }).to_list())


    async def execute(self):
        if self.dataSet == AMSDataSet.CAMPAIGNS:
            campaign = CampaignDataSet.model_validate(self.body)
            await self.executeCampaign(campaign)
        elif self.dataSet == AMSDataSet.AD_GROUPS:
            ad_group = AdGroupDataSet.model_validate(self.body)
            await self.executeAdGroup(ad_group)
        elif self.dataSet == AMSDataSet.ADS:
            ad = AdDataSet.model_validate(self.body)
            await self.executeAd(ad)
        elif self.dataSet == AMSDataSet.TARGETS:
            target = TargetDataSet.model_validate(self.body)
            await self.executeTarget(target)

    async def executeCampaign(self, campaign: CampaignDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            uid, marketplace = marketplace['uid'], marketplace['_id']
            adv_assets = self.dbClient.adv_assets(uid, marketplace)
            setDict = {
                "name": campaign.name,
                "state": campaign.state,
                "lastupdateddatetime": campaign.audit.lastUpdatedDateTime,
            }
            if campaign.budget and campaign.budget.budgetCap and campaign.budget.budgetCap.monetaryBudget: setDict["budget"] = campaign.budget.budgetCap.monetaryBudget.amount
            if campaign.portfolioId: setDict["parent"] = campaign.portfolioId
            await adv_assets.aggregate( [ { "$match": { "uid":uid, "marketplace": marketplace, "assettype": AdAssetType.CAMPAIGN.value, "id": campaign.campaignId } }, { "$set": setDict } ] )

    async def executeAdGroup(self, ad_group: AdGroupDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            uid, marketplace = marketplace['uid'], marketplace['_id']
            adv_assets = self.dbClient.adv_assets(uid, marketplace)
            setDict = { "name": ad_group.name, "state": ad_group.state, "lastupdateddatetime": ad_group.audit.lastUpdatedDateTime }
            if ad_group.bidValue: setDict["bid"] = ad_group.bidValue.defaultBid.value
            await adv_assets.aggregate( [ { "$match": { "uid":uid, "marketplace": marketplace, "assettype": AdAssetType.AD_GROUP.value, "id": ad_group.adGroupId } }, { "$set": setDict } ] )

    async def executeAd(self, ad: AdDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            uid, marketplace = marketplace['uid'], marketplace['_id']
            adv_assets = self.dbClient.adv_assets(uid, marketplace)
            setDict: dict = {"state": ad.state, "lastupdateddatetime": ad.audit.lastUpdatedDateTime}
            if ad.name: setDict["name"] = ad.name
            await adv_assets.aggregate( [ { "$match": { "uid":uid, "marketplace": marketplace, "assettype": AdAssetType.AD.value, "id": ad.adId } }, { "$set": setDict } ] )

    async def executeTarget(self, target: TargetDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            uid, marketplace = marketplace['uid'], marketplace['_id']
            adv_assets = self.dbClient.adv_assets(uid, marketplace)
            setDict: dict = {"state": target.state, "lastupdateddatetime": target.audit.lastUpdatedDateTime}
            if target.bid: 
                setDict["bid"] = target.bid
                curr = await adv_assets.db.findOne({"assettype": AdAssetType.TARGET.value, "id": target.targetId})
                if 'bid' in curr and curr['bid']!=target.bid:
                    setDict['bidChanges'] = {
                        "$concatArrays": [
                            { "$ifNull": ["$bidChanges", []] },  
                            [{
                                "time": target.audit.lastUpdatedDateTime,
                                "previous": curr['bid'],
                                "current": target.bid
                            }]                            
                        ]
                    }

            await adv_assets.aggregate( [ { "$match": { "uid":uid, "marketplace": marketplace, "assettype": AdAssetType.TARGET.value, "id": target.targetId } }, { "$set": setDict } ] )
