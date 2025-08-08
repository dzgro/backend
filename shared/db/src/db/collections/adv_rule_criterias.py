from bson import ObjectId
from db.DbUtils import DbManager
from models.enums import AdAssetType, AdProduct, CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase

class AdRuleCriteriaGroupsUtility:
    db: DbManager
    marketplace: ObjectId
    uid: str
    
    def __init__(self, db:AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.db = DbManager(db.get_collection(CollectionType.ADV_RULE_CRITERIA_GROUPS.value), uid=self.uid, marketplace=self.marketplace)
    
    async def getCriteriaGroups(self, assettype: AdAssetType, adproduct: AdProduct):
        return await self.db.find({"assettype": assettype.value, "adproduct": adproduct.value}, projectionInc=["action","subactions"])
    

        
    
    
    
