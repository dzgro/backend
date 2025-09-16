from dzgroshared.db.payments.model import PaymentList, Payment, PaymentRequest, PaymentStatus
from dzgroshared.db.model import Paginator, PyObjectId, Sort
from dzgroshared.db.enums import  CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class PaymentHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PAYMENTS.value), client.uid)

    async def getPayments(self, paginator: Paginator):
        payments = await self.db.find({"uid": self.client.uid}, sort=Sort(field="_id", order=-1), skip=paginator.skip, limit=paginator.limit )
        count: int|None = None
        if paginator.skip == 0: count = await self.db.count({"uid": self.client.uid})
        return PaymentList.model_validate({"count": count, "data": payments})
    
    async def getPayment(self, id: PyObjectId):
        return Payment.model_validate(await self.db.findOne({"_id": id}))
    
    async def addPayment(self, req: PaymentRequest):
        gst = round(req.amount/ ((1+req.gstrate) / 100), 2)
        pregst = req.amount-gst
        payment = Payment(
            _id= req.id,
            paymentId=req.paymentId,
            pregst=pregst,
            gstrate=req.gstrate,
            gst=gst,
            amount=req.amount,
            isRefund=False,
            invoice=0,
            invoicelink=None,
            status=PaymentStatus.GENERATING_INVOICE
        )
        id =  await self.db.insertOne(payment.model_dump(mode="json", exclude_none=True, by_alias=True))
        return await self.getPayment(id)

    

   