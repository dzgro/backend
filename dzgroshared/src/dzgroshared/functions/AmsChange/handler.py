from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.enums import AMSDataSet, AdAssetType
from dzgroshared.models.functions.ams_change import CampaignDataSet, AdGroupDataSet, AdDataSet, TargetDataSet


class AmsChangeProcessor:
    dataSet: AMSDataSet
    sellerid: str
    marketplaceId: str
    body: dict
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict):
        try:
            parsed = SQSEvent.model_validate(event)
            for record in parsed.Records:
                if record.dictBody:
                    body = record.dictBody
                    SubscribeURL = body.get("SubscribeURL", None)
                    if SubscribeURL:
                        import urllib.request
                        urllib.request.urlopen(SubscribeURL)
                    else:
                        datasetid = AMSDataSet(body.get("dataset_id"))
                        sellerid = body.get("advertiser_id", None)
                        marketplaceid = body.get("marketplace_id", None)
                        if sellerid and marketplaceid:
                            if self.isChangeSet(datasetid):
                                await self.processChangeSet(datasetid, sellerid, marketplaceid, body)

        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    def isChangeSet(self, dataset: AMSDataSet)->bool:
        return dataset in [AMSDataSet.CAMPAIGNS, AMSDataSet.AD_GROUPS, AMSDataSet.ADS, AMSDataSet.TARGETS]
        
    async def processChangeSet(self, dataset: AMSDataSet, sellerid:str, marketplaceid:str, body: dict):
        self.dataSet = dataset
        self.sellerid = sellerid
        self.marketplaceId = marketplaceid
        self.body = body
        await self.executeDataSet()


    

    async def getUidMarketplaces(self):
        return await self.client.db.marketplaces.db.find({
            "sellerid": self.sellerid,
            "marketplaceid": self.marketplaceId
        })

    def getAdvAssets(self, uid:str, marketplaceid:ObjectId):
        self.client.setUid(uid)
        self.client.setMarketplace(marketplaceid)
        return self.client.db.adv_assets
    
    def pipeline(self, pp: PipelineProcessor, collatetype: AdAssetType, id: str, setDict: dict):
        return [pp.matchMarketplace({"assettype": collatetype.value, "id": id}), pp.set(setDict)]

    async def executeDataSet(self):
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
            setDict = {
                "name": campaign.name,
                "state": campaign.state,
                "lastupdateddatetime": campaign.audit.lastUpdatedDateTime,
            }
            if campaign.budget and campaign.budget.budgetCap and campaign.budget.budgetCap.monetaryBudget: setDict["budget"] = campaign.budget.budgetCap.monetaryBudget.amount
            if campaign.portfolioId: setDict["parent"] = campaign.portfolioId
            adv_assets = self.getAdvAssets(marketplace['uid'], marketplace['_id'])
            await adv_assets.aggregate(self.pipeline(adv_assets.db.pp, AdAssetType.CAMPAIGN, campaign.campaignId, setDict))

    async def executeAdGroup(self, ad_group: AdGroupDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            setDict = { "name": ad_group.name, "state": ad_group.state, "lastupdateddatetime": ad_group.audit.lastUpdatedDateTime }
            if ad_group.bidValue: setDict["bid"] = ad_group.bidValue.defaultBid.value
            adv_assets = self.getAdvAssets(marketplace['uid'], marketplace['_id'])
            await adv_assets.aggregate(self.pipeline(adv_assets.db.pp, AdAssetType.AD_GROUP, ad_group.adGroupId, setDict))

    async def executeAd(self, ad: AdDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            setDict: dict = {"state": ad.state, "lastupdateddatetime": ad.audit.lastUpdatedDateTime}
            if ad.name: setDict["name"] = ad.name
            adv_assets = self.getAdvAssets(marketplace['uid'], marketplace['_id'])
            await adv_assets.aggregate(self.pipeline(adv_assets.db.pp, AdAssetType.AD, ad.adId, setDict))

    async def executeTarget(self, target: TargetDataSet):
        marketplaces = await self.getUidMarketplaces()
        for marketplace in marketplaces:
            adv_assets = self.getAdvAssets(marketplace['uid'], marketplace['_id'])
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

            await adv_assets.aggregate(self.pipeline(adv_assets.db.pp, AdAssetType.TARGET, target.targetId, setDict))


