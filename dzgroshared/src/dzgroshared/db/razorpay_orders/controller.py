from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import CollectionType 
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.model import PyObjectId, SuccessResponse
from dzgroshared.db.razorpay_orders.model import RazorPayDbOrderCategory, RazorPayDbOrder, OrderVerificationRequest
from dzgroshared.razorpay.order.model import RazorpayOrder
from dzgroshared.sqs.model import QueueName, SendMessageRequest

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
    
    async def setOrderAsPaid(self, id: str, payment_id: str):
        count, updatedId = await self.db.updateOne({"_id": id, "status": {"$ne": "paid"}}, setDict={"status": "paid", "payment_id": payment_id})
        return count>0
    
    async def setInvoiceOrderAsExpired(self, id: str):
        count, updatedId = await self.db.updateOne({"_id": id, "status": {"$ne": "expired"}}, setDict={"status": "expired"})
        await self.client.db.users.setUserAsOverdue()

    async def addOrder(self, order: RazorpayOrder, category: RazorPayDbOrderCategory) -> RazorPayDbOrder:
        item = {"_id": order.id, "amount": order.amount/100, "currency": order.currency, "status": order.status, "uid": self.client.uid}
        item.update({k: ObjectId(v) if ObjectId.is_valid(v) else v for k,v in order.notes.items()})
        item["category"] = category.value
        await self.db.insertOne(item)
        return RazorPayDbOrder.model_validate(item)
    
    async def verifyOrder(self, req: OrderVerificationRequest):
        success = self.client.razorpay.verify_razorpay_signature(req.razorpayOrderId, req.razorpayPaymentId, req.razorpaySignature, self.client.secrets.RAZORPAY_CLIENT_SECRET)
        plantype = (await self.getOrderById(req.razorpayOrderId)).plantype
        if not plantype: raise ValueError("Invalid Order, Plan Type not found")
        success = await self.client.db.users.setUserAsPaid()
        await self.client.db.marketplaces.startMarketplaceReporting(req.marketplace, plantype)
        return SuccessResponse(success=success)