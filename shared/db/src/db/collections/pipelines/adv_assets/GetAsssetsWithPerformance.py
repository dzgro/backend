from datetime import timedelta
from models.collections.adv_assets import AdAssetCampaign, AdGrowthFilterEnum, ListAdAssetRequest, AdAssetType, AdAssetAdGroup, AdAssetAd, AdAssetTarget, AdAssetPortfolio
from models.enums import Operator, CollectionType
from db.PipelineProcessor import PipelineProcessor, LookUpLetExpression, LookUpPipelineMatchExpression
from db.DataTransformer import Datatransformer

def execute(pp: PipelineProcessor, req: ListAdAssetRequest):

    def setGrowth(key: str):
        return pp.set({key: { '$arrayToObject': { '$reduce': { 'input': '$keys', 'initialValue': [], 'in': { '$let': { 'vars': { 'key': '$$this', 'calculated': { '$ne': [ { '$ifNull': [ '$$this.subkeys', None ] }, None ] }, 'ispercent': { '$ifNull': [ '$$this.ispercent', False ] }, 'isreversegrowth': { '$ifNull': [ '$$this.reversegrowth', False ] } }, 'in': { '$let': { 'vars': { 'curr': { '$cond': [ '$$calculated', 0, { '$ifNull': [ { '$getField': { 'input': { '$getField': { 'input': f'${key}', 'field': '$$key.value' } }, 'field': 'curr' } }, 0 ] } ] }, 'pre': { '$cond': [ '$$calculated', 0, { '$ifNull': [ { '$getField': { 'input': { '$getField': { 'input': f'${key}', 'field': '$$key.value' } }, 'field': 'pre' } }, 0 ] } ] }, 'currsubkey1': { '$cond': [ '$$calculated', { '$ifNull': [ { '$getField': { 'input': { '$getField': { 'input': f'${key}', 'field': { '$arrayElemAt': [ '$$key.subkeys', 0 ] } } }, 'field': 'curr' } }, 0 ] }, None ] }, 'presubkey1': { '$cond': [ '$$calculated', { '$ifNull': [ { '$getField': { 'input': { '$getField': { 'input': f'${key}', 'field': { '$arrayElemAt': [ '$$key.subkeys', 0 ] } } }, 'field': 'pre' } }, 0 ] }, None ] }, 'currsubkey2': { '$cond': [ '$$calculated', { '$ifNull': [ { '$getField': { 'input': { '$getField': { 'input': f'${key}', 'field': { '$arrayElemAt': [ '$$key.subkeys', 1 ] } } }, 'field': 'curr' } }, 0 ] }, None ] }, 'presubkey2': { '$cond': [ '$$calculated', { '$ifNull': [ { '$getField': { 'input': { '$getField': { 'input': f'${key}', 'field': { '$arrayElemAt': [ '$$key.subkeys', 1 ] } } }, 'field': 'pre' } }, 0 ] }, None ] } }, 'in': { '$let': { 'vars': { 'curr': { '$cond': [ '$$calculated', { '$round': [ { '$cond': [ { '$eq': [ '$$currsubkey2', 0 ] }, 0, { '$multiply': [ { '$divide': [ '$$currsubkey1', '$$currsubkey2' ] }, { '$cond': [ '$$ispercent', 1, 1 ] } ] } ] }, 4 ] }, '$$curr' ] }, 'pre': { '$cond': [ '$$calculated', { '$round': [ { '$cond': [ { '$eq': [ '$$presubkey2', 0 ] }, 0, { '$multiply': [ { '$divide': [ '$$presubkey1', '$$presubkey2' ] }, { '$cond': [ '$$ispercent', 1, 1 ] } ] } ] }, 4 ] }, '$$pre' ] } }, 'in': { '$let': { 'vars': { 'growth': { '$cond': [ { '$and': [ { '$ne': [ '$$curr', 0 ] }, { '$ne': [ '$$pre', 0 ] } ] }, { '$cond': [ '$$ispercent', { '$subtract': [ '$$pre', '$$curr' ] }, { '$round': [ { '$multiply': [ { '$subtract': [ { '$divide': [ '$$curr', '$$pre' ] }, 1 ] }, 100 ] }, 2 ] } ] }, None ] }, 'growing': { '$cond': [ { '$eq': [ '$$curr', '$$pre' ] }, None, { '$cond': [ '$$isreversegrowth', { '$gt': [ '$$pre', '$$curr' ] }, { '$lt': [ '$$pre', '$$curr' ] } ] } ] } }, 'in': { '$concatArrays': [ '$$value', { '$let': { 'vars': { 'obj': { '$mergeObjects': [ { '$cond': [ { '$ne': [ '$$curr', 0 ] }, { 'curr': '$$curr' }, {} ] }, { '$cond': [ { '$ne': [ '$$pre', 0 ] }, { 'pre': '$$pre' }, {} ] }, { '$cond': [ { '$ne': [ '$$growth', None ] }, { 'growth': '$$growth' }, {} ] }, { '$cond': [ { '$ne': [ '$$growing', None ] }, { 'growing': '$$growing' }, {} ] } ] } }, 'in': { '$cond': [ { '$eq': [ { '$size': { '$objectToArray': '$$obj' } }, 0 ] }, [], [ { 'k': '$$key.value', 'v': '$$obj' } ] ] } } } ] } } } } } } } } } } } }})
    dt = Datatransformer(pp, 'ad')
    fields: list[str] = []
    if req.assetType==AdAssetType.CAMPAIGN: fields = list(AdAssetCampaign.model_fields.keys())
    elif req.assetType==AdAssetType.AD_GROUP: fields = list(AdAssetAdGroup.model_fields.keys())
    elif req.assetType==AdAssetType.AD: fields = list(AdAssetAd.model_fields.keys())
    elif req.assetType==AdAssetType.TARGET: fields = list(AdAssetTarget.model_fields.keys())
    elif req.assetType==AdAssetType.PORTFOLIO: fields = list(AdAssetPortfolio.model_fields.keys())
    currDates = [req.dates.curr.start+timedelta(days=x) for x in range((req.dates.curr.end-req.dates.curr.start).days+1)]
    preDates = [req.dates.pre.start+timedelta(days=x) for x in range((req.dates.pre.end-req.dates.pre.start).days+1)]
    matchDict: dict = {"assettype": req.assetType.value}
    if req.parent: matchDict.update({"parent": req.parent})
    if req.states : matchDict.update({"state": {"$in": [s.value for s in req.states]}})
    if req.adProducts and req.assetType==AdAssetType.CAMPAIGN : matchDict.update({"adproduct": {"$in": [s.value for s in req.adProducts]}})
    matchStage = pp.matchMarketplace(matchDict)

    if req.assetType==AdAssetType.AD_GROUP:
        letExprs = [LookUpLetExpression(key='assettype', value=AdAssetType.AD.value), LookUpLetExpression(key='parent', value="$id"), LookUpLetExpression(key='date', value=currDates+preDates)]
        matchExprs = [LookUpPipelineMatchExpression(key=key, operator=Operator.EQ if key!='date' else Operator.IN) for key in ['assettype','parent','date']]
        innerpipeline: list[dict] = [pp.matchAllExpressions(matchExprs)]
        innerpipeline.append(pp.group(id="$date", groupings={"ad": { "$push": "$ad"}}))
        innerpipeline.append(dt.collateData())
        innerpipeline.extend([{ "$project": { "ad": 1, "date": "$_id", "_id": 0 } }, { "$group": { "_id": None, "ad": {"$push": "$$ROOT"} } }])
    elif req.assetType==AdAssetType.PORTFOLIO:
        letExprs = [LookUpLetExpression(key='assettype', value=AdAssetType.CAMPAIGN.value), LookUpLetExpression(key='portfolioid', value="$id"), LookUpLetExpression(key='date', value=currDates+preDates)]
        matchExprs = [LookUpPipelineMatchExpression(key=key, operator=Operator.EQ if key!='date' else Operator.IN) for key in ['assettype','date']]
        innerpipeline: list[dict] = [pp.matchAllExpressions(matchExprs)]
        innerpipeline.append(pp.group(id="$portfolioid", groupings={"ad": { "$push": "$ad"}}))
        innerpipeline.append(dt.collateData())
        innerpipeline.append(pp.project(["ad"],["_id"]))
    else:
        letExprs = [LookUpLetExpression(key=key) for key in ['assettype','id']]
        letExprs.append(LookUpLetExpression(key='date', value=currDates+preDates))
        matchExprs = [LookUpPipelineMatchExpression(key=key, operator=Operator.EQ if key!='date' else Operator.IN) for key in ['assettype','id','date']]
        innerpipeline: list[dict] = [pp.matchAllExpressions(matchExprs)]
        innerpipeline.append(pp.group(id=None, groupings={"ad": { "$push": { "ad": "$$ROOT.ad", "date": "$$ROOT.date" } }}))
        innerpipeline.append(pp.project(["ad"],["_id"]))

    lookupPerformance = pp.lookup(CollectionType.ADV,'ad', letExpressions=letExprs, pipeline=innerpipeline)
    replaceRoot = pp.replaceRoot(pp.mergeObjects([pp.first("ad"), pp.unsetField("$$ROOT", "ad")]))
    splitAdToCurrPre = pp.set({"ad": { '$reduce': { 'input': '$ad', 'initialValue': { 'curr': {}, 'pre': {} }, 'in': { '$let': { 'vars': { 'val': '$$value', 'item': { '$objectToArray': '$$this.ad' }, 'key': {"$switch": {"branches": [{"case": {"$in": ["$$this.date", currDates]}, "then": "curr"}, {"case": {"$in": ["$$this.date", preDates]}, "then": "pre"}]}} }, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$key', 'v': { '$arrayToObject': { '$reduce': { 'input': '$$item', 'initialValue': { '$objectToArray': { '$getField': { 'input': '$$value', 'field': '$$key' } } }, 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$this.k' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ '$$this' ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$this.k' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { '$sum': [ '$$v.v', '$$this.v' ] } } ] } ] } } } ] } } } } } ] ] } ] } } } }}})
    adKeysAsCurrPre = pp.set({"ad": { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$ad' }, 'initialValue': [], 'in': { '$let': { 'vars': { 'key': '$$this.k', 'val': '$$value' }, 'in': { '$reduce': { 'input': { '$objectToArray': '$$this.v' }, 'initialValue': '$$val', 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$this.k' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$arrayToObject': [ [ { 'k': '$$key', 'v': '$$this.v' } ] ] } } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$this.k' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { '$mergeObjects': [ '$$v.v', { '$arrayToObject': [ [ { 'k': '$$key', 'v': '$$this.v' } ] ] } ] } } ] } ] } } } ] } } } } } } } }})
    getAdKeys = { '$lookup': { 'from': 'analytics_calculation', 'pipeline': [ { '$match': { '$expr': { '$eq': [ '$value', 'ad' ] } } }, { '$project': { 'items': 1, '_id': 0 } }, { '$unwind': '$items' }, { '$replaceWith': '$items' } ], 'as': 'keys' } }
    percentkeys = dt.addPercentKeys()
    adCalculationsAndGrowth = setGrowth("ad")
    groupForCount = pp.group(None, groupings={"ad": { "$push": "$$ROOT" }, "count": { "$sum": 1 }, "total": { "$push": "$$ROOT.ad" }, "keys": { "$first": "$keys" }, "percentkeys": { "$first": "$percentkeys" }})
    getTotal = pp.set({ 'total': { '$arrayToObject': { '$reduce': { 'input': { '$reduce': { 'input': '$total', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$objectToArray': '$$this' } ] } } }, 'initialValue': [], 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$this.k' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { 'curr': { '$ifNull': [ '$$this.v.curr', 0 ] }, 'pre': { '$ifNull': [ '$$this.v.pre', 0 ] } } } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$this.k' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { 'curr': { '$sum': [ '$$v.v.curr', { '$ifNull': [ '$$this.v.curr', 0 ] } ] }, 'pre': { '$sum': [ '$$v.v.pre', { '$ifNull': [ '$$this.v.pre', 0 ] } ] } } } ] } ] } } } ] } } } } })
    setTotal = setGrowth("total")
    unwindAd = pp.unwind("ad")
    openAd = pp.replaceRoot(pp.mergeObjects(["$ad", {"count": "$count", 'total': '$total'}]))
    sort = pp.sort({f'ad.{req.sort.field}.curr': req.sort.order})
    skip = pp.skip(req.paginator.skip)
    limit = pp.limit(req.paginator.limit)
    convertAdToString = dt.convertCurrPreToString()
    addProducts = pp.lookup(CollectionType.ADV_ADS, 'ads', localField="_id", foreignField="_id", pipeline=[pp.project(['products','count'],['_id'])]) 
    addProduct = { "from": "products", "let": { "uid": "$uid", "marketplace": "$marketplace", "asin": { "$reduce": { "input": "$creative.products", "initialValue": None, "in": { "$cond": { "if": { "$eq": [ "$$this.productIdType", "ASIN" ] }, "then": "$$this.productId", "else": "$$value" } } } } }, "pipeline": [ { "$match": { "$expr": { "$and": [ {"$eq": ["$uid","$$uid"]}, {"$eq": ["$marketplace","$$marketplace"]}, {"$eq": ["$asin","$$asin"]} ] } } }, { "$replaceWith": { "sku": "$sku", "asin": "$asin", "image": {"$first": "$images"} } } ], "as": "product" }
    createObj = pp.replaceRoot(pp.mergeObjects([{ 'data': '$ad', "product": {"$first": "$product"}, 'ads': { '$first': '$ads' }, 'count': '$count', 'total': '$total', "percentkeys": "$percentkeys", 'assettype': req.assetType.value },{ '$arrayToObject': [ [ { 'k': 'details', 'v': { '$reduce': { 'input': fields, 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$this', 'v': { '$ifNull': [ { '$getField': { 'input': '$$ROOT', 'field': '$$this' } }, None ] } } ] ] } ] } } } } ] ] }]))
    groupObjects = pp.group(None, groupings={"count": { "$first":"$count" }, 'total': { '$first': '$total' },'percentkeys': { '$first': '$percentkeys' }, "items": { "$push": { "$unsetField": { "input": "$$ROOT", "field": "count" } } }})
    dt = Datatransformer(pp, 'total')
    convertTotalToString = dt.convertCurrPreToString()
    setPerformance = pp.set({"data": "$total"})
    pipeline = [matchStage, lookupPerformance,replaceRoot, splitAdToCurrPre, adKeysAsCurrPre]
    unset = pp.unset(["_id","percentkeys","total","items.percentkeys", "items.total"])
    if len(req.valueFilters)>0: pipeline.append(pp.match({x.key: {f'${x.operation.name.lower()}': x.val} for x in req.valueFilters}))
    pipeline.extend([getAdKeys, percentkeys, adCalculationsAndGrowth])
    req.growthFilters = list(filter(lambda x: x.val!=AdGrowthFilterEnum.ALL, req.growthFilters))
    if len(req.growthFilters)>0: pipeline.append(pp.match({f'ad.{x.key}.growing': x.val==AdGrowthFilterEnum.GROWING for x in req.growthFilters}))
    pipeline.extend([groupForCount, getTotal, setTotal, unwindAd, openAd,sort, skip, limit, convertAdToString, addProducts, createObj, groupObjects, convertTotalToString, setPerformance, unset])
    return pipeline
