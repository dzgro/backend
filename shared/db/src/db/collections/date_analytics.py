from bson import ObjectId
from models.enums import CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase
from db.DbUtils import DbManager

class DateAnalyticsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(db.get_collection(CollectionType.DATE_ANALYTICS.value), uid=self.uid, marketplace=self.marketplace)
