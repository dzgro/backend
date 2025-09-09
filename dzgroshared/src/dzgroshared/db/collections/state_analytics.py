from bson import ObjectId
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class StateAnalyticsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.STATE_ANALYTICS.value), marketplace=client.marketplaceId)
