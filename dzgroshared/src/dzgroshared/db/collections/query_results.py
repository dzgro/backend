from bson import ObjectId
from dzgroshared.models.collections.analytics import CollateTypeAndValue
from dzgroshared.models.collections.query_results import QueryRequest
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.DataTransformer import Datatransformer
from dzgroshared.models.enums import CollectionType, CollateType
from dzgroshared.client import DzgroSharedClient


class QueryResultsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.QUERY_RESULTS), uid, marketplace)

    async def deleteQueryResults(self, queryid: ObjectId|None=None):
        filterDict = {"queryid": queryid} if queryid else {}
        await self.db.deleteMany(filterDict)

    async def deleteExtraFields(self, id: ObjectId|None=None):
        filterDict = {"queryid": id} if id else {}
        await self.db.deleteFields(["data.buyBoxViews","data.unitSessions","data.returnQuantity","data.revenuePreTax","data.tax"], filterDict=filterDict)


    async def getQueryTable(self, key:str, req: CollateTypeAndValue):
        matchDict = {"collatetype": req.collatetype.value}
        if req.value: matchDict.update({"value": req.value})
        pipeline: list[dict] = [self.db.pp.matchMarketplace(matchDict)]
        pipeline.extend(Datatransformer(self.db.pp).getQueryResultForTable(key))
        pipeline.append({ '$project': { 'data': f'$data.{key}', "_id":"$queryid" } })
        data =  await self.db.aggregate(pipeline)
        return data
    
    async def getCount(self, body: QueryRequest):
        matchDict = {"collatetype": body.collateType.value, "queryid": ObjectId(body.queryId)}
        if body.value: matchDict.update({"value": body.value})
        elif body.parent: matchDict.update({"parent": body.parent})
        elif body.category: matchDict.update({"category": body.category})
        return await self.db.count(matchDict)
    
    async def getPerformance(self, body: QueryRequest):
        def setCategory():
            lookup = { '$lookup': { 'from': 'query_results', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'queryid': '$queryid', 'type': 'asin', 'producttype': '$producttype' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$type', '$$type' ] }, { '$eq': [ '$queryid', '$$queryid' ] }, { '$eq': [ '$producttype', '$$producttype' ] } ] } } }, { '$sort': { 'data.revenue.curr': -1 } }, { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$asin' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$set': { 'image': { '$cond': [ { '$eq': [ { '$size': '$images' }, 0 ] }, None, { '$arrayElemAt': [ '$images', 0 ] } ] } } }, { '$project': { 'sku': 1, 'asin': 1, 'image': 1, '_id': 0 } } ], 'as': 'images' } } ], 'as': 'children' } }
            replaceWith = { '$replaceWith': { 'data': '$data', 'category': { 'producttype': '$producttype', 'count': { '$size': '$children' }, 'skus': { '$firstN': { 'input': { '$reduce': { 'input': '$children', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', '$$this.images' ] } } }, 'n': 10 } } } } }
            return [lookup, replaceWith]

        def setParent():
            lookup = { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$set': { 'childskus': { '$ifNull': [ '$childskus', [ '$sku' ] ] } } }, { '$unwind': { 'path': '$childskus' } }, { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$childskus' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$set': { 'image': { '$arrayElemAt': [ '$images', 0 ] } } }, { '$project': { 'image': 1, 'sku': 1, 'asin': 1, '_id': 0 } } ], 'as': 'result' } }, { '$group': { '_id': { 'sku': '$sku', 'asin': '$asin', 'title': '$title', 'producttype': '$producttype', 'variationtheme': '$variationtheme' }, 'images': { '$first': '$images' }, 'skus': { '$push': { '$first': '$result' } } } }, { '$set': { 'image': { '$cond': [ { '$gt': [ { '$size': '$images' }, 0 ] }, { '$arrayElemAt': [ '$images', 0 ] }, { '$getField': { 'input': { '$first': '$skus' }, 'field': 'image' } } ] } } }, { '$replaceWith': { '$mergeObjects': [ '$_id', { 'image': '$image' }, { 'count': { '$size': '$skus' } }, { '$cond': [ { '$eq': [ { '$ifNull': [ '$_id.variationtheme', None ] }, None ] }, {}, { 'skus': { '$slice': [ '$skus', 1, 5 ] } } ] } ] } } ], 'as': 'result' } }
            replaceWith = { '$replaceWith': { 'data': '$data', 'parent': { '$first': '$result' } } }
            return [lookup, replaceWith]

        def setAsin():
            lookup = { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$group': { '_id': { 'asin': '$asin', 'title': '$title', 'producttype': '$producttype', 'variationtheme': '$variationtheme', 'variationdetails':'$variationdetails', 'parentsku': '$parentsku', 'parentasin': '$parentasin' }, 'images': { '$first': '$images' }, 'skus': { '$push': '$sku' } } }, { '$set': { 'image': { '$arrayElemAt': [ '$images', 0 ] } } }, { '$replaceWith': { '$mergeObjects': [ { 'asin': '$_id.asin', 'title': '$_id.title', 'producttype': '$_id.producttype' }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$_id.variationtheme', None ] }, None ] }, { 'variationtheme': '$_id.variationtheme' }, {} ] }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$_id.variationdetails', None ] }, None ] }, { 'variationdetails': '$_id.variationdetails' }, {} ] }, { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$_id.variationdetails', None ] }, None ] }, { '$ne': [ '$_id.parentsku', '$sku' ] } ] }, { 'parentsku': '$_id.parentsku', 'parentasin': '$_id.parentasin' }, {} ] }, { 'image': '$image' }, { '$cond': [ { '$eq': [ { '$size': '$skus' }, 1 ] }, { 'sku': { '$first': '$skus' } }, { 'count': { '$size': '$skus' } } ] } ] } } ], 'as': 'result' } }
            replaceWith = { '$replaceWith': { 'data': '$data', 'asin': { '$first': '$result' } } }
            return [lookup, replaceWith]

        def setSku():
            lookup = { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceWith': { '$mergeObjects': [ { 'sku': '$sku', 'asin': '$asin', 'title': '$title', 'producttype': '$producttype', 'variationdetails':'$variationdetails', 'image': { '$first': '$images' } }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$_id.variationdetails', None ] }, None ] }, { 'variationdetails': '$_id.variationdetails' }, {} ] }, { '$cond': [ { '$ne': [ { '$ifNull': [ '$variationtheme', None ] }, None ] }, { 'variationtheme': '$variationtheme', 'variationdetails': '$variationdetails' }, {} ] }, { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$variationtheme', None ] }, None ] }, { '$ne': [ '$parentsku', '$sku' ] } ] }, { 'parentsku': '$parentsku', 'parentasin': '$parentasin' }, {} ] } ] } } ], 'as': 'result' } }
            replaceWith = { '$replaceWith': { 'data': '$data', 'sku': { '$first': '$result' } } }
            return [lookup, replaceWith]
        
        matchDict = {"collatetype": body.collateType.value, "queryid": ObjectId(body.queryId)}
        if body.value: matchDict.update({"value": body.value})
        elif body.parent: matchDict.update({"parent": body.parent})
        elif body.category: matchDict.update({"category": body.category})
        sort = self.db.pp.sort({f'data.{body.sort.field}.curr': body.sort.order})
        skip = self.db.pp.skip(body.paginator.skip)
        limit = self.db.pp.limit(body.paginator.limit)
        pipeline: list[dict] = [self.db.pp.matchMarketplace(matchDict), sort, skip, limit]
        pipeline.extend(Datatransformer(self.db.pp).convertResultsForPerformance())
        if body.collateType==CollateType.CATEGORY: pipeline.extend(setCategory())
        elif body.collateType==CollateType.PARENT: pipeline.extend(setParent())
        elif body.collateType==CollateType.ASIN: pipeline.extend(setAsin())
        elif body.collateType==CollateType.SKU: pipeline.extend(setSku())
        data =  await self.db.aggregate(pipeline)
        return data
    
    async def getPerformanceByQuery(self, id: str, req: CollateTypeAndValue):
        filterDict = {"collatetype": req.collatetype.value, "queryid": ObjectId(id)}
        if req.value: filterDict.update({"value": req.value})
        pipeline = [self.db.pp.matchMarketplace(filterDict)]
        pipeline.extend(Datatransformer(self.db.pp).convertResultsForPerformance())
        pipeline.extend([{ '$project': { 'data': 1, '_id': 0 } }, { '$unwind': { 'path': '$data' } }, { '$replaceRoot': { 'newRoot': '$data' } }])
        data = await self.db.aggregate(pipeline)
        # print(pipeline)
        return data


        
      
    

        

