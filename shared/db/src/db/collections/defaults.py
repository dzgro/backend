from bson import ObjectId
from models.model import Paginator, Sort
from models.enums import  CollectionType
from db.DbUtils import DbManager
from motor.motor_asyncio import AsyncIOMotorDatabase

class DefaultsHelper:
    db: DbManager
    
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = DbManager(db.get_collection(CollectionType.DEFAULTS))
    
    async def getNextInvoiceId(self):
        result = await self.db.findOneAndUpdate( {"_id": "invoice_number"}, {"$inc": {"value": 1}} )
        return f"INV-{result['value']}"

    

   