from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import ENVIRONMENT, CollectionType, MarketplaceStatus 
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.model import PyObjectId, SuccessResponse
from dzgroshared.db.razorpay_orders.model import RazorPayDbOrderCategory, RazorPayDbOrder, OrderVerificationRequest
from dzgroshared.razorpay.order.model import RazorPayOrderNotes, RazorpayOrder
from dzgroshared.sqs.model import QueueName, SendMessageRequest

class RazorPayDbOrderHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PG_ORDERS.value), uid=client.uid)

    async def getOrderById(self, id: str) -> RazorPayDbOrder:
        return RazorPayDbOrder.model_validate(await self.db.findOne({"_id": id, "uid": self.client.uid}))
    
    async def getOrderByUid(self, uid: str) -> list[RazorPayDbOrder]:
        data = await self.db.findOne({"uid": uid})
        return [RazorPayDbOrder.model_validate(d) for d in data]
    
    async def getOrderByUidMarketplace(self, uid: str, marketplace: PyObjectId) -> list[RazorPayDbOrder]:
        data = await self.db.findOne({"uid": uid, "marketplace": marketplace})
        return [RazorPayDbOrder.model_validate(d) for d in data]
    
    async def setOrderAsPaid(self, id: str, payment_id: str):
        count, updatedId = await self.db.updateOne({"_id": id, "uid": self.client.uid, "status": {"$ne": "paid"}}, setDict={"status": "paid", "payment_id": payment_id})
        return count>0
    
    async def setInvoiceOrderAsExpired(self, id: str):
        count, updatedId = await self.db.updateOne({"_id": id, "uid": self.client.uid, "status": {"$ne": "expired"}}, setDict={"status": "expired"})
        await self.client.db.users.setUserAsOverdue()

    async def addOrder(self, order: RazorpayOrder, notes: RazorPayOrderNotes, category: RazorPayDbOrderCategory) -> RazorPayDbOrder:
        try:
            item = {"_id": order.id, "amount": order.amount/100, "currency": order.currency.value, "status": order.status.value, "uid": self.client.uid}
            item.update({"notes": notes.model_dump(mode="json")})
            item["category"] = category.value
            await self.db.insertOne(item)
            return RazorPayDbOrder.model_validate(item)
        except Exception as e:
            raise ValueError("We could not process your order. Please contact support.")
    
    async def verifyOrder(self, req: OrderVerificationRequest):
        success = self.client.razorpay.verify_razorpay_signature(req.razorpayOrderId, req.razorpayPaymentId, req.razorpaySignature, self.client.secrets.RAZORPAY_CLIENT_SECRET)
        if not success: raise ValueError("Payment verification failed")
        order = (await self.getOrderById(req.razorpayOrderId))
        if order.paymentId: raise ValueError("Payment has been processed")
        if not order.notes.marketplace: raise ValueError("Marketplace not found in order notes")
        if not order.notes.plan: raise ValueError("Plan not found in order notes")
        from dzgroshared.sqs import utils
        await self.client.db.marketplace_plans.addPlan(order.id, order.notes.marketplace, order.notes.plan)
        await self.client.db.marketplaces.db.updateOne({"_id": order.notes.marketplace, "uid": self.client.uid}, setDict={"status": MarketplaceStatus.BUFFERING.value})
        await utils.sendCreateReportsMessage(self.client, order.notes.marketplace)
        await utils.sendGenerateInvoiceMessage(self.client, order.id, req.razorpayPaymentId)
        return SuccessResponse(success=success)