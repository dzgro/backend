from dzgroshared.db.payments.model import PaymentList, Payment
from dzgroshared.db.model import Paginator, Sort
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
    
    async def getPayment(self, id: str):
        return Payment.model_validate(await self.db.findOne({"_id": id}))
    
    async def addPayment(self, paymentid: str, amount: float, paymenttype: str, invoiceid:str, gst: int):
        await self.db.insertOne({"_id": paymentid, "uid": self.client.uid, "amount": amount, "paymenttype": paymenttype, "invoiceid": invoiceid, "gst": gst})

    

   