from motor.motor_asyncio import AsyncIOMotorDatabase
from models.enums import CollectionType 
from db.DbUtils import DbManager

class SubscriptionsHelper:
    db: DbManager
    uid: str
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str) -> None:
        self.db = DbManager(db.get_collection(CollectionType.SUBSCRIPTIONS.value), uid=uid)
        self.uid = uid

    async def getUserSubscription(self):
        return await self.db.findOne({"_id": self.uid})

    async def addSubscription(self, subscription_id: str, plan_id: str, group_id: str, customer_id: str, status: str):
        await self.db.updateOne(
            {"_id": self.uid}, setDict={
                "subscriptionid": subscription_id, "status": status,
                "planid": plan_id, "groupid": group_id, "customerid": customer_id
            }, upsert=True
        )
        return await self.getUserSubscription()
        
    async def findSubscriptionById(self, id: str):
        return await self.db.findOne({ '_id': self.uid, 'subscriptionid': id })

    async def updateSubscriptionStatus(self, id: str, status: str):
        await self.db.updateOne(
            { '_id': self.uid, 'subscriptionid': id },
            { 'status': status }
        )