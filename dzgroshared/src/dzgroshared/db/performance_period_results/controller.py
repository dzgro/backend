from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.performance_period_results.model import PerformanceDashboardResponse, PerformanceTableRequest, ComparisonPeriodDataRequest
from dzgroshared.db.enums import CollectionType, CollateType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.analytics import controller
from dzgroshared.db.model import PeriodDataRequest, SingleAnalyticsMetricTableResponse, SingleMetricPeriodDataRequest


class PerformancePeriodResultsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PERFORMANCE_PERIOD_RESULTS), marketplace=client.marketplaceId)


    async def deletePerformanceResults(self, queryid: ObjectId|None=None):
        filterDict = {"queryid": queryid} if queryid else {}
        await self.db.deleteMany(filterDict)

    async def getPerformanceTable(self, req: SingleMetricPeriodDataRequest):
        lookupLet = { 'marketplace': self.client.marketplaceId, 'queryid': '$_id', 'collatetype': 'marketplace' }
        if req.value: lookupLet['value'] = req.value
        lookupMatch = { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$queryid', '$$queryid' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] } ] } }
        if req.value: lookupMatch['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [ { '$match': { 'uid': { '$exists': False } } }, { '$lookup': { 'from': 'query_results', 'let': lookupLet, 'pipeline': [ { '$match': lookupMatch }, { '$project': { 'data': 1, '_id': 0 } } ], 'as': 'data' } }, { '$set': { 'data': { '$first': '$data.data' } } } ]
        pipeline.extend([{"$match": { "data": {"$exists": True}}}, { '$project': { 'tag': 1, f'data.{req.key.value}': 1, "_id":0 } }])
        data = await self.db.aggregate(pipeline)
        from dzgroshared.analytics import controller
        data = controller.transformCurrPreData(data, self.client.marketplace.countrycode)
        return SingleAnalyticsMetricTableResponse.model_validate(data)
    
    async def getCount(self, body: PerformanceTableRequest):
        matchDict = {"queryid": body.queryId, "collatetype": body.collatetype.value}
        if body.value: matchDict.update({"value": body.value})
        elif body.parent: matchDict.update({"parent": body.parent})
        return await self.db.count(matchDict)
    
    async def getPerformanceListforPeriod(self, body: PerformanceTableRequest):
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
        if body.collatetype==CollateType.MARKETPLACE: raise ValueError("Collate Type cannot be marketplace for performance table")
        matchDict = { "queryid": body.queryId, "collatetype": body.collatetype.value}
        if body.parent: matchDict.update({"parent": body.parent})
        sort = self.db.pp.sort({f'data.{body.sort.field}.curr': body.sort.order})
        skip = self.db.pp.skip(body.paginator.skip)
        limit = self.db.pp.limit(body.paginator.limit)
        pipeline: list[dict] = [self.db.pp.matchMarketplace(matchDict), controller.getProjectionStage('Comparison', body.collatetype), sort, skip, limit]
        if body.collatetype==CollateType.CATEGORY: pipeline.extend(setCategory())
        elif body.collatetype==CollateType.PARENT: pipeline.extend(setParent())
        elif body.collatetype==CollateType.ASIN: pipeline.extend(setAsin())
        elif body.collatetype==CollateType.SKU: pipeline.extend(setSku())
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data =  await self.db.aggregate(pipeline)
        data = controller.transformData('Comparison',data, body.collatetype, self.client.marketplace.countrycode)
        columns = ["Skus" if body.collatetype==CollateType.SKU else "Asins" if body.collatetype==CollateType.ASIN else "Parent Skus" if body.collatetype==CollateType.PARENT else "Category"]
        columns.extend([item.metric.value for item in controller.getMetricGroupsBySchemaType('Comparison', body.collatetype)])
        return {"rows": data, "columns": columns}

    async def getDashboardPerformanceResults(self, req: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_comparison_pipeline(req)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return {"data": data}
    
    


        
      
    

        

