from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.enums import CollectionType 
from dzgroshared.db.DbUtils import DbManager

class SubscriptionsHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.SUBSCRIPTIONS.value), uid=client.uid)

    async def getUserSubscription(self):
        return await self.db.findOne({"_id": self.client.uid})

    async def addSubscription(self, subscription_id: str, plan_id: str, group_id: str, customer_id: str, status: str):
        await self.db.updateOne(
            {"_id": self.client.uid}, setDict={
                "subscriptionid": subscription_id, "status": status,
                "planid": plan_id, "groupid": group_id, "customerid": customer_id
            }, upsert=True
        )
        return await self.getUserSubscription()
        
    async def findSubscriptionById(self, id: str):
        return await self.db.findOne({ '_id': self.client.uid, 'subscriptionid': id })

    async def updateSubscriptionStatus(self, id: str, status: str):
        await self.db.updateOne(
            { '_id': self.client.uid, 'subscriptionid': id },
            { 'status': status }
        )