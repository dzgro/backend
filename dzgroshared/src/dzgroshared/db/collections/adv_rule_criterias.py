from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import AdAssetType, AdProduct, CollectionType
from dzgroshared.client import DzgroSharedClient

class AdRuleCriteriaGroupsUtility:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_RULE_CRITERIA_GROUPS.value), uid=self.uid, marketplace=self.marketplace)
    
    async def getCriteriaGroups(self, assettype: AdAssetType, adproduct: AdProduct):
        return await self.db.find({"assettype": assettype.value, "adproduct": adproduct.value}, projectionInc=["action","subactions"])
    

        
    
    
    
