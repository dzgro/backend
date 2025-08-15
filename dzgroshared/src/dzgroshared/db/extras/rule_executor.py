from bson import ObjectId
import json
from dzgroshared.models.model import Paginator
from dzgroshared.models.enums import Operator, CollectionType
from dzgroshared.models.collections.adv_rule_runs import AdRuleRunStatus
from dzgroshared.models.collections.adv_rules import AdCriteria, AdCriteriaResultAction, AdCriteriaResultSubAction, CriteriasSimplified
from dzgroshared.db.PipelineProcessor import LookUpLetExpression, LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.db.DataTransformer import Datatransformer

class AdRuleExecutor:
    uid: str
    marketplace: ObjectId
    runid: str
    # helper: AdRuleRunUtility
    pp: PipelineProcessor

    def __init__(self, uid: str,marketplace: ObjectId,runid: str) -> None:
        try:
            self.uid = uid
            self.runid = runid
            self.marketplace = ObjectId(marketplace)
            # self.helper = AdRuleRunUtility(self.marketplace, self.uid)
            self.pp = self.helper.db.pp
            self.processRule()
            self.helper.updateRunStatus(runid, AdRuleRunStatus.COMPLETED)
        except Exception as e:
            raise ValueError("Invalid Configuration")

    def __getattr__(self, item):
        return None

    def processRule(self):
        from app.HelperModules.Db import mongo_db
        mongo_db.connect_to_database()
        pipeline = self.createResults()
        self.helper.db.aggregate(pipeline)
        print("Done")

    def getAdObject(self):
        letkeys=['assettype','id','dates']
        letExprs = [LookUpLetExpression(key=key) for key in letkeys]
        innerpipeline = [self.pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key) for key in ['assettype','id']]+[LookUpPipelineMatchExpression(key="date", value="dates", operator=Operator.IN, isValueVariable=True)]), self.pp.replaceWith("$ad")]
        pipeline = [self.pp.lookup(CollectionType.ADV,'ad', letExpressions=letExprs, pipeline=innerpipeline)]
        dt = Datatransformer(self.pp, 'ad')
        pipeline.extend(dt.transformDataForAdRuleResult())
        return pipeline
    
    def getInitPipeline(self, status: AdRuleRunStatus):
        from app.HelperModules.Collections.dzgro.adv.rule_runs.Helper import AdRuleRunUtility
        run = AdRuleRunUtility(self.marketplace,self.uid).getRunById(self.runid)
        from app.HelperModules.Collections.dzgro.adv.rules.Helper import AdRuleUtility
        rule = AdRuleUtility(self.marketplace,self.uid).getRuleById(run.ruleId)    
        matchrun = self.pp.matchMarketplace({"_id": ObjectId(self.runid), "status": status.value})
        addRule = self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", json.loads(rule.model_dump_json())]))
        getBidsAndDates = { '$lookup': { 'from': 'marketplaces', 'localField': 'marketplace', 'foreignField': '_id', 'let': { 'adproduct': '$adproduct', 'lookback': '$lookback', 'exclude': '$exclude' }, 'pipeline': [ { '$project': { 'endDate': 1, 'countryCode': 1, '_id': 0 } }, { '$lookup': { 'from': 'country_details', 'localField': 'countryCode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'bids': 1, '_id': 0 } }, { '$replaceWith': '$bids' } ], 'as': 'bids' } }, { '$set': { 'bids': { '$getField': { 'input': { '$first': '$bids' }, 'field': '$$adproduct' } } } }, { '$set': { 'dates': { '$let': { 'vars': { 'startdate': { '$dateSubtract': { 'startDate': '$endDate', 'unit': 'day', 'amount': "$$exclude" } } }, 'in': { '$reduce': { 'input': { '$range': [ 0, "$$lookback", 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$$startdate', 'unit': 'day', 'amount': '$$this' } } ] ] } } } } } } }, { '$project': { 'countryCode': 0, 'endDate': 0 } } ], 'as': 'bids' } }
        return rule, [matchrun,addRule,getBidsAndDates]

    def createResults(self):
        rule, pipeline = self.getInitPipeline(AdRuleRunStatus.QUEUED)
        letkeys = ['assettype','adproduct']
        innerpipeline = [{"$match": {"$expr": {"$and": [{"$eq": ["$state","ENABLED"]}, {"$eq": ["$negative",False]}]}}}, self.pp.project(["id","adgroupid","campaignid","bid"],["_id"])]
        getAssets = self.pp.lookup(CollectionType.ADV_ASSETS,rule.assettype.value, letkeys=letkeys, pipeline=innerpipeline)
        openAsset = self.pp.unwind(rule.assettype.value)
        replaceRoot = self.pp.replaceRoot(self.pp.mergeObjects([ { '$getField': { 'input': '$$ROOT', 'field': '$assettype' } }, { '$first': '$bids' }, { "assettype": "$assettype", "uid": "$uid", "marketplace": "$marketplace", }]))
        defaultBid = self.pp.lookup(CollectionType.ADV_ASSETS, 'defaultbid', letExpressions=[LookUpLetExpression(key='assettype', value='adgroup'),LookUpLetExpression(key='id', value='$adgroupid')], pipeline=[self.pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key) for key in ['assettype','id']]), self.pp.replaceWith({"$ifNull": ["$bid",{"defaultBid":None}]})])
        setbid = self.pp.set({"bid": { "$let": { "vars": { "default": {"$first": "$defaultbid"} }, "in": { "$ifNull": ["$bid.bid", "$$default.defaultBid"] } } }})
        pipeline.extend([getAssets,openAsset,  replaceRoot,defaultBid, setbid])
        pipeline.extend(self.getAdObject())
        if not rule.summary: raise ValueError("Rule is not summarised")
        pipeline.extend(self.bucketByCriteria(rule.criterias, rule.summary.criterias))
        setminmaxBids =  self.pp.set({ 'case.bid': { '$cond': [ { '$eq': [ { '$ifNull': [ '$case.bid', None ] }, None ] }, None, { '$round': [ { '$cond': [ { '$gt': [ '$case.bid', '$bids.max' ] }, '$bids.max', { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$bids.min', None ] }, None ] }, { '$lt': [ '$case.bid', 1.0 ] } ] }, '$bids.min', '$case.bid' ] } ] }, 2 ] } ] } })
        project = self.pp.replaceRoot({"id": "$id", "case": "$case", "runid": ObjectId(self.runid), "uid": self.uid, "marketplace": self.marketplace})
        merge = self.pp.merge(CollectionType.ADV_RULE_RUN_RESULTS)
        pipeline.extend([setminmaxBids, project, merge])
        return pipeline
    
    def bucketByCriteria(self, criterias: list[AdCriteria], simplifiedCriterias: list[CriteriasSimplified]):
        branches = []
        for index, criteria in enumerate(criterias):
            simplified = simplifiedCriterias[index]
            case = {"$and": [{f'${condition.operator.name.lower()}': [{"$ifNull": [f'$ad.{condition.metric.value}.rawvalue',0]}, condition.val]} for condition in criteria.conditions]}
            result: dict = {'simplifiedAction': simplified.result, 'action': criteria.result.action.value}
            if criteria.result.action==AdCriteriaResultAction.SET_BID:
                if criteria.result.subaction==AdCriteriaResultSubAction.SET_EXACT_BID: result.update({"bid": {"$round": [criteria.result.val,2]}})
                elif criteria.result.subaction==AdCriteriaResultSubAction.CALCULATED: result.update({"bid": {"$divide": [{"$multiply": ["$ad.cpc.rawvalue", criteria.result.val]},"$ad.acos.rawvalue"]}})
            elif criteria.result.action==AdCriteriaResultAction.UPDATE_BID:
                action = "$sum" if criteria.result.subaction==AdCriteriaResultSubAction.INCREASE_PERCENT else "$subtract"
                result['bid'] = {"$round": [{action: ["$bid", {"$multiply": ["$bid",{"$divide": [criteria.result.val, 100]}]}]},2]}
            branches.append({"case": case, "then": result})
        return [{"$set": {"case": {"$switch": {"branches": branches, "default": None}}}}, {"$match": {"case": {"$ne": None}}}]
    
    def viewResults(self, paginator: Paginator):
        def lookupTarget():
            letkeys=['uid','marketplace','assettype','id']
            matchstage = self.pp.matchAllEQExpressions(letkeys)
            set = self.pp.set({"adgroupid": {"$concat": [{"$toString": "$marketplace"},"_","$adgroupid"]},"campaignid": {"$concat": [{"$toString": "$marketplace"},"_","$campaignid"]}})
            lookupadg = self.pp.lookup(CollectionType.ADV_ASSETS,'adgroup', localField="adgroupid", foreignField="_id", pipeline=[self.pp.project(obj={ "adgroup":"$name", "adgroupbid":"$bid", "_id":0 })])
            lookupcampaign = self.pp.lookup(CollectionType.ADV_ASSETS,'campaign', localField="campaignid", foreignField="_id", pipeline=[self.pp.project(obj={ "campaign":"$name", "_id":0 })])
            lookupAds = self.pp.lookup(CollectionType.ADV_ADS,'ads', localField="adgroupid", foreignField="_id", pipeline=[self.pp.project(obj={"_id":0 })])
            replaceRoot = self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT",self.pp.first("adgroup"),self.pp.first("campaign"),{"ads": self.pp.first("ads")}]))
            setBid = self.pp.set({"bid": { "$ifNull": [ "$bid", "$adgroupbid" ] }})
            replace = self.pp.replaceRoot({ '$reduce': { 'input': list(AdAssetTarget.model_fields.keys()), 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$this', 'v': { '$ifNull': [ { '$getField': { 'input': '$$ROOT', 'field': '$$this' } }, None ] } } ] ] } ] } } })
            innerpipeline = [matchstage, set, lookupadg, lookupcampaign, lookupAds, replaceRoot, setBid, replace]
            lookup = self.pp.lookup(CollectionType.ADV_ASSETS, "asset", letkeys=letkeys, pipeline=innerpipeline)
            return lookup
        
        rule, pipeline = self.getInitPipeline(AdRuleRunStatus.COMPLETED)
        lookupresults = self.pp.lookup(CollectionType.ADV_RULE_RUN_RESULTS,'data', localField="_id", foreignField="runid", pipeline=[self.pp.skip(paginator.skip), self.pp.limit(paginator.limit)])
        unwindData = self.pp.unwind("data")
        setData = self.pp.replaceRoot(self.pp.mergeObjects(["$data", {"assettype": "$assettype", "dates": { "$getField": { "input": self.pp.first("bids"), "field": "dates" } }}]))
        setAsset = lookupTarget()
        setAssetKey = self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", {"assettype": "$assettype", "asset": self.pp.first("asset")}]))
        pipeline.extend([lookupresults,unwindData,setData, setAsset, setAssetKey])
        pipeline.extend(self.getAdObject())
        pipeline.append(self.pp.project([], ["id","uid","marketplace","runid","dates"]))
        print(pipeline)
        return pipeline

