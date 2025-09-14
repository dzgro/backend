from dzgroshared.db.enums import  CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class InvoiceNumberHelper:
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.INVOICE_NUMBER))

    async def getNextInvoiceId(self):
        result = await self.db.findOneAndUpdate( {}, {"$inc": {"value": 1}} )
        return f"INV-{result['value']}"

    

   