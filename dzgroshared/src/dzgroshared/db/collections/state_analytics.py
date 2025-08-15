from bson import ObjectId
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class StateAnalyticsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(client.db.database.get_collection(CollectionType.STATE_ANALYTICS.value), uid=self.uid, marketplace=self.marketplace)
