from bson import ObjectId
from dzgroshared.models.collections.pg_orders import OrderVerificationRequest, PGOrderCategory
from dzgroshared.models.collections.pricing import Pricing, PricingDetail, PricingDetailItem
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.enums import CollectionType 
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.model import PyObjectId, SuccessResponse
from dzgroshared.models.razorpay.order import RazorpayOrder

class PGOrderHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PG_ORDERS.value), uid=client.uid)

    async def getOrderById(self, id: str) -> RazorpayOrder:
        return RazorpayOrder.model_validate(await self.db.findOne({"_id": id}))
    
    async def getOrderByUid(self, uid: str) -> list[RazorpayOrder]:
        data = await self.db.findOne({"uid": uid})
        return [RazorpayOrder.model_validate(d) for d in data]
    
    async def getOrderByUidMarketplace(self, uid: str, marketplace: PyObjectId) -> list[RazorpayOrder]:
        data = await self.db.findOne({"uid": uid, "marketplace": marketplace})
        return [RazorpayOrder.model_validate(d) for d in data]

    async def addOrder(self, order: RazorpayOrder, category: PGOrderCategory, marketplace: PyObjectId|None=None) -> RazorpayOrder:
        item = order.model_dump(mode="json")
        if marketplace: item["marketplace"] = marketplace
        del item['notes']
        item["category"] = category.value
        await self.db.insertOne(item)
        return order
    
    async def verifyOrder(self, req: OrderVerificationRequest):
        success = self.client.razorpay.verify_razorpay_signature(req.razorpay_order_id, req.razorpay_payment_id, req.razorpay_signature, self.client.secrets.RAZORPAY_CLIENT_SECRET)
        success = await self.client.db.user.setUserAsPaid()
        return SuccessResponse(success=success)