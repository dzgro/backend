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
            data = await self.db.findOne({"marketplace": self.client.marketplaceId, "active": MarketplacePlanStatus.ACTIVE.value})
            return MarketplacePlan.model_validate({"data": data})
        except Exception as e:
            raise ValueError("No active plan found for this marketplace.")

    async def addPlan(self, marketplace: PyObjectId, plan: MarketplacePlan):
        data = {"marketplace": marketplace, "active": MarketplacePlanStatus.ACTIVE.value}
        await self.db.updateMany(data, setDict={"active": MarketplacePlanStatus.ARCHIVED.value})
        data.update(plan.model_dump(mode="json"))
        data['_id'] = await self.db.insertOne(data)
        return MarketplacePlan.model_validate(**data)
    
        
    
    