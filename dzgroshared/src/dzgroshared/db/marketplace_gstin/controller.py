from bson import ObjectId
from dzgroshared.db.gstin.model import BusinessDetails, LinkedGsts, GstDetail
from dzgroshared.db.enums import CollectionType, GstStateCode
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.marketplace_gstin.model import MarketplaceGSTStatus, MarketplaceGst
from dzgroshared.db.model import PyObjectId, SuccessResponse

class MarketplaceGstHelper:
    client: DzgroSharedClient
    db:DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.MARKETPLACE_GSTIN.value))

    async def getActiveGST(self):
        try:
            data = await self.db.findOne({"marketplace": self.client.marketplaceId, "status": MarketplaceGSTStatus.ACTIVE.value})
            return MarketplaceGst.model_validate({"data": data})
        except Exception as e:
            raise ValueError("No active GSTIN found for this marketplace.")
        
    async def linkGst(self, gstin: PyObjectId, marketplace: PyObjectId):
        data = {"gstin": gstin, "marketplace": marketplace, "status": MarketplaceGSTStatus.ACTIVE.value}
        await self.db.updateMany(data, setDict={"status": MarketplaceGSTStatus.ARCHIVED.value})
        id = await self.db.insertOne(data)
        return MarketplaceGst.model_validate(**data)
    
        
    
    