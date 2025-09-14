from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.adv.adv_rules.model import AdKey, AdRule, AdRuleAssetTypeWithAdProduct, CreateAdRuleRequest, SimplifyAdRuleRequest, getAdRuleSummary
from dzgroshared.db.enums import AdAssetType, AdProduct, CollectionType, Operator
from dzgroshared.db.model import Paginator, SuccessResponse
from dzgroshared.client import DzgroSharedClient

class AdRuleUtility:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_RULES.value), marketplace=client.marketplaceId)


    def convertToObjectId(self, id: str|ObjectId):
        return ObjectId(id) if isinstance(id, str) else id

    async def getRules(self, paginator: Paginator, assettype: AdAssetType|None=None):
        matchDict: dict = {} if not assettype else {'assettype': assettype.value}
        rules = await self.db.find(matchDict, skip=paginator.skip, limit=paginator.limit)
        for r in rules:
            try: AdRule(**r)
            except Exception as e:
                print(e) 
        return [AdRule(**r) for r in rules]
    
    async def getRuleById(self, id: str|ObjectId):
        rule = await self.db.findOne({'_id': self.convertToObjectId(id)})
        if not rule: raise ValueError('Rule not found')
        rule = AdRule(**rule)
        return rule 
    
    async def addRule(self, req: CreateAdRuleRequest):
        inserted_id = await self.db.insertOne(req.model_dump(exclude_none=True), withUidMarketplace=True)
        return await self.getRuleById(str(inserted_id))
        
    async def deleteRule(self, ruleId: str|ObjectId):
        deleted_count = await self.db.deleteOne({'marketplace': self.client.marketplace, '_id': self.convertToObjectId(ruleId)})
        message = 'Rule deleted' if deleted_count==1 else 'Rule could not be deleted'
        return SuccessResponse(success=deleted_count==1, message=message)
    
    async def updateRule(self, ruleid: str, req: CreateAdRuleRequest):
        await self.db.updateOne({"_id": self.convertToObjectId(ruleid)}, setDict=req.model_dump(exclude_none=True))
        return await self.getRuleById(ruleid)
        
    async def getRuleTemplates(self):
        return await self.db.find({"template": True}, withUidMarketplace=False)
    
    async def getTemplateById(self, id: str|ObjectId):
        return await self.db.findOne({"_id": self.convertToObjectId(id), "template": True}, withUidMarketplace=False)
    
    async def getRuleParams(self):
        target = AdRuleAssetTypeWithAdProduct(assettype=AdAssetType.TARGET, adproducts=[AdProduct.SP])
        searchTerm = AdRuleAssetTypeWithAdProduct(assettype=AdAssetType.SEARCH_TERM, adproducts=[AdProduct.SP])
        return [target, searchTerm]
    
    async def getCriteriaGroups(self, assettype: AdAssetType, adproduct: AdProduct):
        groups = await self.client.db.ad_rule_criteria_groups.db.find({"assettype": assettype.value, "adproduct": adproduct.value}, projectionInc=["action","subactions"])
        detail = await self.client.db.marketplaces.getCountryBidsByMarketplace(self.client.marketplaceId)
        bidMinMax: dict|None = None
        if adproduct==AdProduct.SP: bidMinMax = detail.bids[adproduct]
        if not bidMinMax: raise ValueError(f"Your marketplace country is currently not eligible to run this automation.")
        return { "criteriaGroups": groups, "bids": bidMinMax, "operators": Operator.withSigns(), "keys": AdKey.labelValues(), "currency": detail.currencyCode}
    
    async def createTemplate(self, req: CreateAdRuleRequest):
        inserted_id = await self.db.insertOne(req.model_dump(exclude_none=True), withUidMarketplace=False)
        return await self.getTemplateById(inserted_id)
    
    def summariseAdRule(self, req: SimplifyAdRuleRequest):
        return getAdRuleSummary(req.criterias, req.filters)

        

        
    
    
    
