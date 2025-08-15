from dzgroshared.models.enums import  CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class DefaultsHelper:
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.DEFAULTS))

    async def getNextInvoiceId(self):
        result = await self.db.findOneAndUpdate( {"_id": "invoice_number"}, {"$inc": {"value": 1}} )
        return f"INV-{result['value']}"

    

   