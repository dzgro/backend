from bson import ObjectId
from db.collections.pipelines.adv_ad_group_mapping import ListAdGroupMappings
from db.collections.pipelines.adv_assets import GetAsssetsWithPerformance
from models.collections.adv_assets import ListAdAssetRequest
from models.enums import AdAssetType, AdProduct, CollectionType
from models.model import Paginator
from motor.motor_asyncio import AsyncIOMotorDatabase
from db.DbUtils import DbManager

class AdvAdGroupMappingHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(db.get_collection(CollectionType.ADV_AD_GROUP_MAPPING.value), uid=self.uid, marketplace=self.marketplace)

    # async def listMappings(self, paginator: Paginator):
    #     pipeline = ListAdGroupMappings.pipeline(self.uid, self.marketplace, paginator)
    #     return await self.assets.aggregate(pipeline)

    # async def createMapping(self, mapping: AdGroupMappingRequest):
        # setDict = {mapping.type.lower(): mapping.mapping}
        # self.db.updateOne({'marketplace': self.marketplace.id, 'adGroupId': mapping.adGroupId}, {"$set": setDict}, upsert=True)
        # return setDict
        # return {}