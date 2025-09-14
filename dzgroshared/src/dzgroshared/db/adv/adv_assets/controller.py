from bson import ObjectId
from dzgroshared.db.adv.adv_assets.pipelines import GetAsssetsWithPerformance
from dzgroshared.db.adv.adv_assets.model import ListAdAssetRequest
from dzgroshared.db.enums import AdAssetType, AdProduct, CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager
from .pipelines import Campaigns, Adgroups, Portfolios

class AdvAssetsHelper:
    client: DzgroSharedClient
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_ASSETS.value), marketplace=client.marketplaceId)

    async def createCampaignAds(self):
        pipeline = Campaigns.pipeline(self.uid, self.marketplace)
        return await self.db.aggregate(pipeline)
    
    async def createAdgroupAds(self):
        pipeline = Adgroups.pipeline(self.uid, self.marketplace)
        return await self.db.aggregate(pipeline)
    
    async def createPortfolioAds(self):
        pipeline = Portfolios.pipeline(self.uid, self.marketplace)
        return await self.db.aggregate(pipeline)

    async def listAssets(self, req: ListAdAssetRequest):
        pipeline = GetAsssetsWithPerformance.execute(self.db.pp, req)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Data to Display")
        return data[0]
    
    async def aggregate(self, pipeline: list[dict]):
        return await self.db.aggregate(pipeline)

    async def getFiltersForAdRuleRun(self, adproduct: AdProduct, assettype: AdAssetType):
        filterDict = {"assettype": assettype.value, "adproduct": adproduct.value, "deliverystatus": "DELIVERING"}
        return await self.db.find(filterDict, projectionInc=["id", "name"], projectionExc=["_id"])
    
    async def getTargetTypes(self, adProduct: AdProduct):
        if adProduct!=AdProduct.SP: raise ValueError("Unsupported Ad Product Type")
        matchStage = self.db.pp.matchMarketplace({"assettype": AdAssetType.TARGET.value, 'adProduct': AdProduct.SP.value, 'negative': False})
        groupTargetTypes =self.db.pp.group(id='$targetType', groupings={'matchTypes': { '$push': '$targetDetails.matchType' }})
        setMatchTypes =  self.db.pp.set({ 'matchTypes': { '$setUnion': '$matchTypes' } })
        groupAll =  self.db.pp.group(None, {'data': { '$push': '$$ROOT' }})
        replaceRoot =  self.db.pp.replaceRoot({ 'targetTypes': { '$reduce': { 'input': '$data', 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$this._id', 'v': '$$this.matchTypes' } ] ] } ] }} } })
        pipeline = [ matchStage, groupTargetTypes, setMatchTypes, groupAll, replaceRoot  ]
        result = await self.db.aggregate(pipeline)
        if len(result)>0 and 'targetTypes' in result[0]: return result[0]['targetTypes']
        raise ValueError('No Target Types exists')

