from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollateType, CountryCode
from dzgroshared.db.marketplaces.model import MarketplaceCache
from dzgroshared.db.model import PyObjectId
from dzgroshared.db.performance_period_results.model import ComparisonTableRequest


def setCategory():
    lookup = { '$lookup': { 'from': 'query_results', 'let': { 'marketplace': '$marketplace', 'queryid': '$queryid', 'type': 'asin', 'producttype': '$producttype' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$type', '$$type' ] }, { '$eq': [ '$queryid', '$$queryid' ] }, { '$eq': [ '$producttype', '$$producttype' ] } ] } } }, { '$sort': { 'data.revenue.curr': -1 } }, { '$lookup': { 'from': 'products', 'let': { 'marketplace': '$marketplace', 'asin': '$asin' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$set': { 'image': { '$cond': [ { '$eq': [ { '$size': '$images' }, 0 ] }, None, { '$arrayElemAt': [ '$images', 0 ] } ] } } }, { '$project': { 'sku': 1, 'asin': 1, 'image': 1, '_id': 0 } } ], 'as': 'images' } } ], 'as': 'children' } }
    replaceWith = { '$replaceWith': { 'data': '$data', 'category': { 'producttype': '$producttype', 'count': { '$size': '$children' }, 'skus': { '$firstN': { 'input': { '$reduce': { 'input': '$children', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', '$$this.images' ] } } }, 'n': 10 } } } } }
    return [lookup, replaceWith]

def setParent():
    lookup = { '$lookup': { 'from': 'products', 'let': { 'marketplace': '$marketplace', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$set': { 'childskus': { '$ifNull': [ '$childskus', [ '$sku' ] ] } } }, { '$unwind': { 'path': '$childskus' } }, { '$lookup': { 'from': 'products', 'let': { 'marketplace': '$marketplace', 'sku': '$childskus' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$set': { 'image': { '$arrayElemAt': [ '$images', 0 ] } } }, { '$project': { 'image': 1, 'sku': 1, 'asin': 1, '_id': 0 } } ], 'as': 'result' } }, { '$group': { '_id': { 'sku': '$sku', 'asin': '$asin', 'title': '$title', 'producttype': '$producttype', 'variationtheme': '$variationtheme' }, 'images': { '$first': '$images' }, 'skus': { '$push': { '$first': '$result' } } } }, { '$set': { 'image': { '$cond': [ { '$gt': [ { '$size': '$images' }, 0 ] }, { '$arrayElemAt': [ '$images', 0 ] }, { '$getField': { 'input': { '$first': '$skus' }, 'field': 'image' } } ] } } }, { '$replaceWith': { '$mergeObjects': [ '$_id', { 'image': '$image' }, { 'count': { '$size': '$skus' } }, { '$cond': [ { '$eq': [ { '$ifNull': [ '$_id.variationtheme', None ] }, None ] }, {}, { 'skus': { '$slice': [ '$skus', 1, 5 ] } } ] } ] } } ], 'as': 'result' } }
    replaceWith = { '$replaceWith': { 'data': '$data', 'parent': { '$first': '$result' } } }
    return [lookup, replaceWith]

def setAsin():
    lookup = { '$lookup': { 'from': 'products', 'let': {'marketplace': '$marketplace', 'asin': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$group': { '_id': { 'asin': '$asin', 'title': '$title', 'producttype': '$producttype', 'variationtheme': '$variationtheme', 'variationdetails':'$variationdetails', 'parentsku': '$parentsku', 'parentasin': '$parentasin' }, 'images': { '$first': '$images' }, 'skus': { '$push': '$sku' } } }, { '$set': { 'image': { '$arrayElemAt': [ '$images', 0 ] } } }, { '$replaceWith': { '$mergeObjects': [ { 'asin': '$_id.asin', 'title': '$_id.title', 'producttype': '$_id.producttype' }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$_id.variationtheme', None ] }, None ] }, { 'variationtheme': '$_id.variationtheme' }, {} ] }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$_id.variationdetails', None ] }, None ] }, { 'variationdetails': '$_id.variationdetails' }, {} ] }, { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$_id.variationdetails', None ] }, None ] }, { '$ne': [ '$_id.parentsku', '$sku' ] } ] }, { 'parentsku': '$_id.parentsku', 'parentasin': '$_id.parentasin' }, {} ] }, { 'image': '$image' }, { '$cond': [ { '$eq': [ { '$size': '$skus' }, 1 ] }, { 'sku': { '$first': '$skus' } }, { 'count': { '$size': '$skus' } } ] } ] } } ], 'as': 'result' } }
    replaceWith = { '$replaceWith': { 'data': '$data', 'asin': { '$first': '$result' } } }
    return [lookup, replaceWith]

def setSku():
    lookup = { '$lookup': { 'from': 'products', 'let': { 'marketplace': '$marketplace', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceWith': { '$mergeObjects': [ { 'sku': '$sku', 'asin': '$asin', 'title': '$title', 'producttype': '$producttype', 'variationdetails':'$variationdetails', 'image': { '$first': '$images' } }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$_id.variationdetails', None ] }, None ] }, { 'variationdetails': '$_id.variationdetails' }, {} ] }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$variationtheme', None ] }, None ] }, { 'variationtheme': '$variationtheme', 'variationdetails': '$variationdetails' }, {} ] }, { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$variationtheme', None ] }, None ] }, { '$ne': [ '$parentsku', '$sku' ] } ] }, { 'parentsku': '$parentsku', 'parentasin': '$parentasin' }, {} ] } ] } } ], 'as': 'result' } }
    replaceWith = { '$replaceWith': { 'data': '$data', 'sku': { '$first': '$result' } } }
    return [lookup, replaceWith]

def pipeline(marketplaceId: ObjectId, countryCode: CountryCode, body: ComparisonTableRequest):
    pp = PipelineProcessor()
    if body.collatetype==CollateType.MARKETPLACE: raise ValueError("Collate Type cannot be marketplace for performance table")
    matchDict = { "queryid": body.queryId, "collatetype": body.collatetype.value}
    if body.parent: matchDict.update({"parent": body.parent})
    sort = pp.sort({f'data.{body.sort.field}.curr': body.sort.order})
    skip = pp.skip(body.paginator.skip)
    limit = pp.limit(body.paginator.limit)
    from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
    builder = AnalyticsPipelineBuilder(marketplaceId, countryCode)
    pipeline: list[dict] = [pp.matchMarketplace(matchDict)]
    pipeline.extend(builder.create_comparison_pipeline())
    pipeline.extend([sort, skip, limit])
    if body.collatetype==CollateType.CATEGORY: pipeline.extend(setCategory())
    elif body.collatetype==CollateType.PARENT: pipeline.extend(setParent())
    elif body.collatetype==CollateType.ASIN: pipeline.extend(setAsin())
    elif body.collatetype==CollateType.SKU: pipeline.extend(setSku())
    return pipeline