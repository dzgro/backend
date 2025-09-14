from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import CollectionType 
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.model import PyObjectId, SuccessResponse
from dzgroshared.db.razorpay_orders.model import RazorPayDbOrderCategory, RazorPayDbOrder, OrderVerificationRequest
from dzgroshared.razorpay.order.model import RazorpayOrder

class RazorPayDbOrderHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PG_ORDERS.value), uid=client.uid)

    async def getOrderById(self, id: str) -> RazorPayDbOrder:
        return RazorPayDbOrder.model_validate(await self.db.findOne({"_id": id}))
    
    async def getOrderByUid(self, uid: str) -> list[RazorPayDbOrder]:
        data = await self.db.findOne({"uid": uid})
        return [RazorPayDbOrder.model_validate(d) for d in data]
    
    async def getOrderByUidMarketplace(self, uid: str, marketplace: PyObjectId) -> list[RazorPayDbOrder]:
        data = await self.db.findOne({"uid": uid, "marketplace": marketplace})
        return [RazorPayDbOrder.model_validate(d) for d in data]

    async def addOrder(self, order: RazorpayOrder, category: RazorPayDbOrderCategory, marketplace: PyObjectId|None=None) -> RazorPayDbOrder:
        item = order.model_dump(mode="json")
        if marketplace: item["marketplace"] = marketplace
        del item['notes']
        item["category"] = category.value
        await self.db.insertOne(item)
        return RazorPayDbOrder.model_validate(item)
    
    async def verifyOrder(self, req: OrderVerificationRequest):
        success = self.client.razorpay.verify_razorpay_signature(req.razorpay_order_id, req.razorpay_payment_id, req.razorpay_signature, self.client.secrets.RAZORPAY_CLIENT_SECRET)
        success = await self.client.db.users.setUserAsPaid()
        return SuccessResponse(success=success)