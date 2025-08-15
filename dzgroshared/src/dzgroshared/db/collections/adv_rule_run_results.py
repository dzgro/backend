from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class AdRuleRunResultsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_RULE_RUN_RESULTS.value), uid=self.uid, marketplace=self.marketplace)

    def convertToObjectId(self, id: str|ObjectId):
        return ObjectId(id) if isinstance(id, str) else id
    
    def getResultCountWithColumns(self, runid: str|ObjectId):
        return {"count": self.db.count({"runid": self.convertToObjectId(runid)})}


