from dzgroshared.models.model import Paginator, Sort
from dzgroshared.models.enums import  CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class PaymentHelper:
    db: DbManager
    uid: str

    def __init__(self, client: DzgroSharedClient, uid:str) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.PAYMENTS.value))
        self.uid = uid

    async def getPayments(self, paginator: Paginator):
        count = await self.db.count({"uid": self.uid})
        payments = await self.db.find({"uid": self.uid}, sort=Sort(field="_id", order=-1), skip=paginator.skip, limit=paginator.limit )
        return {"count": count, "payments": payments}
    
    async def getPayment(self, id: str):
        return await self.db.findOne({"_id": id})
    
    async def addPayment(self, paymentid: str, amount: float, paymenttype: str, invoiceid:str, gst: int):
        await self.db.insertOne({"_id": paymentid, "uid": self.uid, "amount": amount, "paymenttype": paymenttype, "invoiceid": invoiceid, "gst": gst})

    

   