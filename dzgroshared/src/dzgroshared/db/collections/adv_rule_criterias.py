from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import AdAssetType, AdProduct, CollectionType
from dzgroshared.client import DzgroSharedClient

class AdRuleCriteriaGroupsUtility:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_RULE_CRITERIA_GROUPS.value), marketplace=self.client.marketplaceId)

    async def getCriteriaGroups(self, assettype: AdAssetType, adproduct: AdProduct):
        return await self.db.find({"assettype": assettype.value, "adproduct": adproduct.value}, projectionInc=["action","subactions"])
    

        
    
    
    
