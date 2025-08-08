from bson import ObjectId
from db.collections.pipelines.adv_assets import GetAsssetsWithPerformance
from models.collections.adv_assets import ListAdAssetRequest
from models.enums import AdAssetType, AdProduct, CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase
from db.DbUtils import DbManager

class AdvAssetsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(db.get_collection(CollectionType.ADV_ASSETS.value), uid=self.uid, marketplace=self.marketplace)

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

