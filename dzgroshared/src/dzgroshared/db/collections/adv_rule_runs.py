from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.collections.adv_rule_runs import AdRuleRun, AdRuleRunRequest, AdRuleRunStatus
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.model import Paginator
from dzgroshared.client import DzgroSharedClient

class AdRuleRunUtility:
    db: DbManager
    marketplace: ObjectId
    uid: str
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_RULE_RUNS.value), uid=self.uid, marketplace=self.marketplace)

    def convertToObjectId(self, id: str|ObjectId):
        return ObjectId(id) if isinstance(id, str) else id
    
    def getIdsAsObjectIds(self, ids: list[str]):
        return [ObjectId(x) for x in ids]
    
    async def runRule(self, req: AdRuleRunRequest):
        try:
            rule = await self.client.db.ad_rule_utility.getRuleById(req.ruleid)
            obj: dict = {"ruleId": self.convertToObjectId(rule.id), "status": AdRuleRunStatus.QUEUED.value}
            if req.filters: obj['filters']=req.filters.model_dump()
            id = await self.db.insertOne(obj, timestampkey="startedat", withUidMarketplace=True)
            return await self.getRunById(id)
        except: raise ValueError('We could not find the rule in your account')
    
    async def getRunById(self, runId: str|ObjectId):
        try: return AdRuleRun(**await self.db.findOne({'_id': self.convertToObjectId(runId)}))
        except: raise ValueError('We could not find the run history for this execution')

    async def updateRunStatus(self, runId: str|ObjectId, status: AdRuleRunStatus):
        return await self.db.updateOne({"_id": self.convertToObjectId(runId)}, setDict={"status": status.value})
    
    
    async def getRuns(self, ruleId:str|ObjectId, paginator: Paginator):
        return await self.db.find({ 'ruleId': self.convertToObjectId(ruleId)}, skip=paginator.skip, limit=paginator.limit)
    
    async def getRunsByIds(self, ruleId:str|ObjectId, ids: list[str]):
        return await self.db.find({ 'ruleId': self.convertToObjectId(ruleId), 'ids': {"$in": self.getIdsAsObjectIds(ids)}})

    
    async def execute(self, ruleId:str|ObjectId, runId:str|ObjectId, discardIds: list[str]):
        matchStage = self.db.pp.matchMarketplace({ '_id': self.convertToObjectId(runId),"ruleId":self.convertToObjectId(ruleId)})
        setDiscarded = self.db.pp.set({ 'discardedIds': discardIds, 'accepted': { '$subtract': [ '$count', len(discardIds) ] }, 'rejected': len(discardIds), 'executing': True })
        merge = self.db.pp.merge(CollectionType.ADV_RULE_RUNS)
        pipeline = [matchStage, setDiscarded, merge]
        await self.db.aggregate(pipeline)
        return await self.getRunById(runId)

    async def getRuleRunResults(self, runid: str, paginator: Paginator):
        pipeline: list[dict]|None = None
        from dzgroshared.db.extras.rule_executor import AdRuleExecutor
        pipeline = await AdRuleExecutor(self.uid, self.marketplace, runid).viewResults(paginator)
        data = await self.db.aggregate(pipeline)
        return data

    async def getRuleRunCountWithColumns(self, runid: str):
        matchstage = self.db.pp.matchMarketplace({"_id": ObjectId(runid), "status": AdRuleRunStatus.COMPLETED.value})
        lookupRule = self.db.pp.lookup(CollectionType.ADV_RULES, 'rule', localField="ruleId", foreignField="_id")
        getCount = self.db.pp.lookup(CollectionType.ADV_RULE_RUN_RESULTS, 'count', localField="_id", foreignField="runid", pipeline=[{"$count": "count"}])
        replaceWith = self.db.pp.replaceWith({"rule": self.db.pp.first("rule"), "count": self.db.pp.first("count.count")})
        pipeline = [matchstage, lookupRule, getCount, replaceWith]
        pipeline.extend(self.db.pp.getAdColumns())
        return await self.db.aggregate(pipeline)[0]

        
        
    
    
    
