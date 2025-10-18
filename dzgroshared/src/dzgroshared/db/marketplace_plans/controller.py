from bson import ObjectId
from dzgroshared.db.gstin.model import BusinessDetails, LinkedGsts, GstDetail
from dzgroshared.db.enums import CollectionType, GstStateCode
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.marketplace_gstin.model import MarketplaceGst
from dzgroshared.db.marketplace_plans.model import MarketplacePlanStatus
from dzgroshared.db.model import MarketplacePlan, PyObjectId, SuccessResponse

class MarketplacePlanHelper:
    client: DzgroSharedClient
    db:DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.MARKETPLACE_PLANS.value))

    async def getActivePlan(self):
        try:
            data = await self.db.findOne({"marketplace": self.client.marketplaceId, "status": MarketplacePlanStatus.ACTIVE.value})
            return MarketplacePlan.model_validate({"data": data})
        except Exception as e:
            raise ValueError("No active plan found for this marketplace.")

    async def addPlan(self, orderid: str, marketplace: PyObjectId, plan: MarketplacePlan):
        data = {"marketplace": marketplace, "status": MarketplacePlanStatus.ACTIVE.value}
        await self.db.updateMany(data, setDict={"status": MarketplacePlanStatus.ARCHIVED.value})
        data.update({"plan": plan.plan.value, "pricing": plan.pricing, "duration": plan.duration.value, "orderid": orderid})
        return await self.db.insertOne(data)
    
        
    
    