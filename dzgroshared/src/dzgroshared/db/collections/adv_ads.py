from bson import ObjectId
from dzgroshared.db.collections.pipelines.adv_assets import GetAsssetsWithPerformance
from dzgroshared.models.collections.adv_assets import ListAdAssetRequest
from dzgroshared.models.enums import AdAssetType, AdProduct, CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class AdvAAdsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_ADS.value), marketplace=client.marketplaceId)

    async def refreshAll(self):
        await self.deleteAll()
        await self.client.db.adv_assets.createCampaignAds()
        await self.client.db.adv_assets.createAdgroupAds()
        await self.client.db.adv_assets.createPortfolioAds()

    async def deleteAll(self):
        return await self.db.deleteMany({})
    
    
