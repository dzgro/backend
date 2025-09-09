from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class AdRuleRunResultsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_RULE_RUN_RESULTS.value), marketplace=self.client.marketplaceId)

    def convertToObjectId(self, id: str|ObjectId):
        return ObjectId(id) if isinstance(id, str) else id
    
    def getResultCountWithColumns(self, runid: str|ObjectId):
        return {"count": self.db.count({"runid": self.convertToObjectId(runid)})}


