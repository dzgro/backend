from bson import ObjectId
from db.PipelineProcessor import PipelineProcessor
from models.collections.adv_assets import AdAssetTarget
from models.collections.adv_rule_runs import AdRuleRunStatus
from models.enums import CollectionType
from models.model import Paginator


def pipeline(marketplace: ObjectId, uid:str,  runid: str, paginator: Paginator):

    def lookupTarget():
        letkeys=['uid','marketplace','assettype','id']
        matchstage = pp.matchAllEQExpressions(letkeys)
        set = pp.set({"adgroupid": {"$concat": [{"$toString": "$marketplace"},"_","$adgroupid"]},"campaignid": {"$concat": [{"$toString": "$marketplace"},"_","$campaignid"]}})
        lookupadg = pp.lookup(CollectionType.ADV_ASSETS,'adgroup', localField="adgroupid", foreignField="_id", pipeline=[pp.project(obj={ "adgroup":"$name", "adgroupbid":"$bid", "_id":0 })])
        lookupcampaign = pp.lookup(CollectionType.ADV_ASSETS,'campaign', localField="campaignid", foreignField="_id", pipeline=[pp.project(obj={ "campaign":"$name", "_id":0 })])
        lookupAds = pp.lookup(CollectionType.ADV_ADS,'ads', localField="adgroupid", foreignField="_id", pipeline=[pp.project(obj={"_id":0 })])
        replaceRoot = pp.replaceRoot(pp.mergeObjects(["$$ROOT",pp.first("adgroup"),pp.first("campaign"),{"ads": pp.first("ads")}]))
        setBid = pp.set({"bid": { "$ifNull": [ "$bid", "$adgroupbid" ] }})
        replace = pp.replaceRoot({ '$reduce': { 'input': list(AdAssetTarget.model_fields.keys()), 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$this', 'v': { '$ifNull': [ { '$getField': { 'input': '$$ROOT', 'field': '$$this' } }, None ] } } ] ] } ] } } })
        innerpipeline = [matchstage, set, lookupadg, lookupcampaign, lookupAds, replaceRoot, setBid, replace]
        lookup = pp.lookup(CollectionType.ADV_ASSETS, "asset", letkeys=letkeys, pipeline=innerpipeline)
        return lookup
    pp = PipelineProcessor(uid, marketplace)
    matchstage = pp.matchMarketplace({"_id": ObjectId(runid), "status": AdRuleRunStatus.COMPLETED.value})
    lookupRule = pp.lookup(CollectionType.ADV_RULES, 'assettype', localField="ruleId", foreignField="_id", pipeline=[pp.project(['assettype'],["_id"])])
    setAssetType = pp.replaceWith({"assettype": pp.first("assettype.assettype"), "runid": "$_id", "uid": "$uid", "marketplace":"$marketplace"})
    lookupresults = pp.lookup(CollectionType.ADV_RULE_RUN_RESULTS,'data', localField="runid", foreignField="runid", pipeline=[pp.skip(paginator.skip), pp.limit(paginator.limit)])
    unwindData = pp.unwind("data")
    setData = pp.replaceRoot(pp.mergeObjects(["$data", {"assettype": "$assettype"}]))
    setAsset = lookupTarget()
    setAssetKey = pp.replaceRoot(pp.mergeObjects(["$$ROOT", {"$arrayToObject": [[{"k": "$assettype", "v": pp.first("asset")}]]}]))
    pipeline = [matchstage,lookupRule,setAssetType,lookupresults,unwindData,setData, setAsset, setAssetKey]
    pipeline.extend(TargetRuleExecutor(marketplace, uid, runid).getAdObject())
    pipeline.append(pp.project([], ["id","assettype","asset","uid","marketplace","runid"]))
    return pipeline
