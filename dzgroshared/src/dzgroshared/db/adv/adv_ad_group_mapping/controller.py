from bson import ObjectId
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class AdvAdGroupMappingHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_AD_GROUP_MAPPING.value), marketplace=self.client.marketplaceId)

    # async def listMappings(self, paginator: Paginator):
    #     pipeline = ListAdGroupMappings.pipeline(self.uid, self.marketplace, paginator)
    #     return await self.assets.aggregate(pipeline)

    # async def createMapping(self, mapping: AdGroupMappingRequest):
        # setDict = {mapping.type.lower(): mapping.mapping}
        # self.db.updateOne({'marketplace': self.marketplace.id, 'adGroupId': mapping.adGroupId}, {"$set": setDict}, upsert=True)
        # return setDict
        # return {}