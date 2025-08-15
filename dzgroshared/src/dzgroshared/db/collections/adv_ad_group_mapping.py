from bson import ObjectId
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class AdvAdGroupMappingHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_AD_GROUP_MAPPING.value), uid=self.uid, marketplace=self.marketplace)

    # async def listMappings(self, paginator: Paginator):
    #     pipeline = ListAdGroupMappings.pipeline(self.uid, self.marketplace, paginator)
    #     return await self.assets.aggregate(pipeline)

    # async def createMapping(self, mapping: AdGroupMappingRequest):
        # setDict = {mapping.type.lower(): mapping.mapping}
        # self.db.updateOne({'marketplace': self.marketplace.id, 'adGroupId': mapping.adGroupId}, {"$set": setDict}, upsert=True)
        # return setDict
        # return {}