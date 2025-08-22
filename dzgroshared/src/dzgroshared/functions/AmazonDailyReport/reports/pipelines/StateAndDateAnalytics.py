from datetime import datetime
from typing import Literal
from bson import ObjectId
from dzgroshared.db.client import DbClient
from dzgroshared.db.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.models.enums import CollateType, CollectionType

stateKey = { 'Uttarpradesh': 'Uttar Pradesh', 'Tg': 'Telangana', 'Delhi': 'New Delhi' }
MergeType = Literal['state','sales','ad','traffic']

class AnalyticsProcessor:
    dbClient: DbClient
    pp: PipelineProcessor
    dates: list[datetime]

    def __init__(self, dbClient: DbClient, dates: list[datetime]):
        self.dates = dates
        self.dbClient = dbClient
        self.pp = self.dbClient.state_analytics.db.pp
        
    # async def addDateToOrderItems(self):
    #     pipeline = [self.pp.matchMarketplace()]
    #     pipeline.append(self.pp.lookup(CollectionType.ORDERS, 'date', localField='order', foreignField="_id", pipeline=[{ '$project': { 'date': '$orderdate', '_id': 0 } }]))
    #     pipeline.append(self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", self.pp.first("date")])))
    #     pipeline.append(self.pp.set({ 'date': { '$let': { 'vars': { 'parts': { '$dateToParts': { 'date': '$date', 'timezone': 'Asia/Kolkata' } } }, 'in': { '$dateFromParts': { 'year': '$$parts.year', 'month': '$$parts.month', 'day': '$$parts.day', 'timezone': 'UTC' } } } }}))
    #     pipeline.append(self.pp.merge(CollectionType.ORDER_ITEMS))
    #     await self.dbClient.order_items.db.aggregate(pipeline)
    #     return self.dates.pop()


    async def executeDate(self, date: datetime, collateTypes: list[CollateType] = list(CollateType)):
        print(f'-----------------------{date.strftime("%Y-%m-%d")}--------------------------------')
        for collateType in collateTypes:
            if collateType==CollateType.SKU: await self.createSkuAnalytics(date)
            elif collateType==CollateType.ASIN: await self.createAsinAnalytics(date)
            elif collateType==CollateType.PARENT: await self.createParentAsinAnalytics(date)
            elif collateType==CollateType.CATEGORY: await self.createCategoryAnalytics(date)
            else: await self.createMarketplaceAnalytics(date)
        index = self.dates.index(date)
        nextDate = self.dates[index-1] if index>0 else None
        return nextDate

    def addParents(self, key: Literal['sku', 'asin']):
        lookupParents = self.pp.lookup(CollectionType.PRODUCTS,'producttype', pipeline=[self.pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key)]), self.pp.project(['producttype','parentasin','parentsku'],[])], letkeys=[key])
        setproductType = self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", {'$first': '$producttype'}, {"_id": "$$ROOT._id"}]))
        setUnspecified = self.pp.set({'producttype': {"$ifNull": ["$producttype","Uncategorized"]}})
        return [lookupParents, setproductType, setUnspecified]
    
    def setId(self, collateType: CollateType, collection: CollectionType):
        id = [{"$toString": self.dbClient.marketplace},"_", { "$dateToString": { "date": "$date", "format": "%Y-%m-%d" } },"_"]
        if collection==CollectionType.STATE_ANALYTICS: id.extend(["$state","_","$fulfillment","_"])
        id.append(f'${collateType.value}') if collateType!=CollateType.MARKETPLACE else id.pop()
        return self.pp.set({"collatetype": collateType.value, "_id": {"$concat": id}, "value": f"${collateType.value}"})
    
    def openId(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { '$unsetField': { 'input': '$$ROOT', 'field': '_id' } }, '$_id' ] } } }
    
    def collate(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { "$arrayToObject": { "$filter": { "input": { "$objectToArray": "$$ROOT" }, "as": "kv", "cond": { "$not": { "$in": ["$$kv.k", ["ad","sales","traffic"]] } } } } }, { '$let': { 'vars': { 'data': { '$reduce': { 'input': [ 'ad', 'sales', 'traffic' ], 'initialValue': [], 'in': { '$let': { 'vars': { 'input': { '$ifNull': [ { '$getField': { 'input': '$$ROOT', 'field': '$$this' } }, [] ] } }, 'in': { '$cond': [ { '$eq': [ { '$size': '$$input' }, 0 ] }, '$$value', { '$concatArrays': [ '$$value', [ { 'k': '$$this', 'v': { '$arrayToObject': { '$reduce': { 'input': '$$input', 'initialValue': [], 'in': { '$let': { 'vars': { 'val': '$$value', 'curr': { '$objectToArray': '$$this' } }, 'in': { '$reduce': { 'input': '$$curr', 'initialValue': '$$val', 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$this.k' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ '$$this' ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$this.k' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { '$sum': [ '$$v.v', '$$this.v' ] } } ] } ] } } } ] } } } } } } } } } ] ] } ] } } } } } }, 'in': { '$cond': { 'if': { '$eq': [ { '$size': '$$data' }, 0 ] }, 'then': {}, 'else': { '$arrayToObject': '$$data' } } } } } ] } } }
    
    async def createSkuAnalytics(self, date: datetime):
        self.curr = datetime.now()
        pipeline = [ { '$match': { 'uid': self.dbClient.uid, 'marketplace': self.dbClient.marketplace, 'date': date } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$sku', 'asin': '$asin', 'date': '$date', 'orderid': '$order' }, 'quantity': { '$sum': '$quantity' }, 'revenue': { '$sum': '$revenue' }, 'tax': { '$sum': '$tax' } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { '$unsetField': { 'input': '$$ROOT', 'field': '_id' } } ] } } }, { '$lookup': { 'from': 'orders', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'order': '$order', 'sku': '$sku', 'quantity': '$quantity', 'revenue': '$revenue', 'tax': '$tax' }, 'localField': 'orderid', 'foreignField': '_id', 'pipeline': [ { '$lookup': { 'from': 'settlements', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'orderid': '$orderid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$orderid', '$$orderid' ] } ] } } } ], 'as': 'settlement' } }, { '$set': { 'metrics': { '$reduce': { 'input': '$settlement', 'initialValue': { 'skurevenue': 0, 'skufees': 0, 'otherrevenue': 0, 'nonskuexpense': 0 }, 'in': { '$mergeObjects': [ '$$value', { '$cond': [ { '$eq': [ { '$ifNull': [ '$$this.sku', None ] }, None ] }, { 'nonskuexpense': { '$sum': [ '$$value.nonskuexpense', '$$this.amount' ] } }, { '$cond': [ { '$eq': [ '$$this.sku', '$$sku' ] }, { '$cond': [ { '$in': [ '$$this.amounttype', [ 'ItemPrice', 'ItemTax' ] ] }, { 'skurevenue': { '$sum': [ '$$value.skurevenue', '$$this.amount' ] } }, { 'skufees': { '$sum': [ '$$value.skufees', '$$this.amount' ] } } ] }, { '$cond': [ { '$in': [ '$$this.amounttype', [ 'ItemPrice', 'ItemTax' ] ] }, { 'otherrevenue': { '$sum': [ '$$value.otherrevenue', '$$this.amount' ] } }, {} ] } ] } ] } ] } } } } }, { '$set': { 'derivedmetrics': { '$cond': { 'if': { '$gt': [ { '$size': '$settlement' }, 0 ] }, 'then': { 'revenue': { '$round': [ '$metrics.skurevenue', 1 ] }, 'returnquantity': { '$cond': { 'if': { '$eq': [ '$$revenue', 0 ] }, 'then': 0, 'else': { '$round': [ { '$multiply': [ { '$subtract': [ 1, { '$divide': [ '$metrics.skurevenue', '$$revenue' ] } ] }, '$$quantity' ] }, 0 ] } } }, 'tax': { '$cond': { 'if': { '$eq': [ '$$revenue', 0 ] }, 'then': 0, 'else': { '$round': [ { '$multiply': [ { '$divide': [ '$metrics.skurevenue', '$$revenue' ] }, '$$tax' ] }, 2 ] } } }, 'expense': { '$let': { 'vars': { 'total': { '$sum': [ '$metrics.otherrevenue', '$metrics.skurevenue' ] } }, 'in': { '$cond': { 'if': { '$or': [ { '$eq': [ '$$total', 0 ] }, { '$eq': [ '$metrics.skurevenue', 0 ] } ] }, 'then': '$metrics.nonskuexpense', 'else': { '$round': [ { '$sum': [ '$metrics.skufees', { '$divide': [ '$metrics.nonskuexpense', { '$divide': [ '$metrics.skurevenue', { '$sum': [ '$metrics.otherrevenue', '$metrics.skurevenue' ] } ] } ] } ] }, 1 ] } } } } } }, 'else': { 'revenue': '$$revenue', 'returnquantity': 0, 'expense': 0, 'tax': '$$tax' } } } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$derivedmetrics', '$metrics', { 's': '$settlement', 'state': '$state', 'fulfillment': '$fulfillment' } ] } } } ], 'as': 'state' } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$first': '$state' } ] } } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$sku', 'asin': '$asin', 'date': '$date', 'state': '$state', 'fulfillment': '$fulfillment' }, 'expense': { '$sum': '$expense' }, 'revenue': { '$sum': '$revenue' }, 'tax': { '$sum': '$tax' }, 'quantity': { '$sum': '$quantity' }, 'returnquantity': { '$sum': '$returnquantity' }, 'fbmrevenue': { '$sum': { '$cond': [ { '$eq': [ '$fulfillment', 'Merchant' ] }, '$revenue', 0 ] } }, 'fbarevenue': { '$sum': { '$cond': [ { '$ne': [ '$fulfillment', 'Merchant' ] }, '$revenue', 0 ] } } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'sales': { '$unsetField': { 'input': '$$ROOT', 'field': '_id' } } } ] } } }, { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$sku' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$project': { 'producttype': 1, 'parentasin': 1, 'parentsku': 1, '_id': 0 } } ], 'as': 'producttype' } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$first': '$producttype' } ] } } }, { '$set': { 'producttype': { '$ifNull': [ '$producttype', 'Uncategorized' ] } } } ]
        pipeline.extend([self.setId(CollateType.SKU, CollectionType.STATE_ANALYTICS), self.pp.merge(CollectionType.STATE_ANALYTICS)])
        await self.dbClient.order_items.db.aggregate(pipeline)
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.SKU.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$sku', 'asin': '$asin', 'date': '$date', "producttype": "$producttype", "parentsku": "$parentsku", "parentasin": "$parentasin" }, 'sales': { '$push': '$sales' } } }
        openId = self.openId()
        lookupAds = { '$lookup': { 'from': 'adv', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$sku', 'assettype': 'Ad', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }
        merge = self.pp.merge(CollectionType.DATE_ANALYTICS)
        pipeline = [matchStage, group, openId, lookupAds, self.collate(),self.setId(CollateType.SKU, CollectionType.DATE_ANALYTICS), merge]
        await self.dbClient.state_analytics.db.aggregate(pipeline)

    async def createAsinAnalytics(self, date: datetime):
        self.curr = datetime.now()
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.SKU.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'state': "$state",'fulfillment':"$fulfillment", 'asin': '$asin', 'date': '$date', "producttype": "$producttype", "parentsku": "$parentsku", "parentasin": "$parentasin" }, 'sales': { '$push': '$sales' } } }
        setId = self.setId(CollateType.ASIN, CollectionType.STATE_ANALYTICS)
        pipeline = [matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.STATE_ANALYTICS)]
        await self.dbClient.state_analytics.db.aggregate(pipeline)
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.SKU.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$asin', 'date': '$date', "producttype": "$producttype", "parentsku": "$parentsku", "parentasin": "$parentasin" }, 'sales': { '$push': '$sales' } ,'ad': { '$push': '$ad' } } }
        lookupTraffic = { '$lookup': { 'from': 'traffic', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$asin', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$traffic' } } ], 'as': 'traffic' } }
        setId = self.setId(CollateType.ASIN, CollectionType.DATE_ANALYTICS)
        pipeline = [matchStage, group, self.openId(),lookupTraffic , self.collate(), setId, self.pp.merge(CollectionType.DATE_ANALYTICS)]
        await self.dbClient.state_analytics.db.aggregate(pipeline)

    async def createParentAsinAnalytics(self, date: datetime):
        self.curr = datetime.now()
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.ASIN.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'state': "$state",'fulfillment':"$fulfillment", 'date': '$date', "producttype": "$producttype", "parentsku": "$parentsku", "parentasin": "$parentasin" }, 'sales': { '$push': '$sales' } } }
        setId = self.setId(CollateType.PARENT, CollectionType.STATE_ANALYTICS)
        pipeline = [matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.STATE_ANALYTICS)]
        await self.dbClient.state_analytics.db.aggregate(pipeline)
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.ASIN.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'date': '$date', "producttype": "$producttype", "parentsku": "$parentsku", "parentasin": "$parentasin" }, 'sales': { '$push': '$sales' } ,'ad': { '$push': '$ad' },'traffic': { '$push': '$traffic' } } }
        setId = self.setId(CollateType.PARENT, CollectionType.DATE_ANALYTICS)
        await self.dbClient.state_analytics.db.aggregate([matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.DATE_ANALYTICS)])

    async def createCategoryAnalytics(self, date: datetime):
        self.curr = datetime.now()
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.PARENT.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'state': "$state",'fulfillment':"$fulfillment", 'date': '$date', "producttype": "$producttype"}, 'sales': { '$push': '$sales' } } }
        setId = self.setId(CollateType.CATEGORY, CollectionType.STATE_ANALYTICS)
        pipeline = [matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.STATE_ANALYTICS)]
        await self.dbClient.state_analytics.db.aggregate(pipeline)
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.PARENT.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'date': '$date', "producttype": "$producttype"}, 'sales': { '$push': '$sales' } ,'ad': { '$push': '$ad' },'traffic': { '$push': '$traffic' } } }
        setId = self.setId(CollateType.CATEGORY, CollectionType.DATE_ANALYTICS)
        await self.dbClient.state_analytics.db.aggregate([matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.DATE_ANALYTICS)])

    async def createMarketplaceAnalytics(self, date: datetime):
        self.curr = datetime.now()
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.CATEGORY.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'state': "$state",'fulfillment':"$fulfillment", 'date': '$date'}, 'sales': { '$push': '$sales' } } }
        setId = self.setId(CollateType.MARKETPLACE, CollectionType.STATE_ANALYTICS)
        await self.dbClient.state_analytics.db.aggregate([matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.STATE_ANALYTICS)])
        matchStage = self.pp.matchMarketplace({"collatetype": CollateType.CATEGORY.value, "date": date})
        group = { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'date': '$date'}, 'sales': { '$push': '$sales' } ,'ad': { '$push': '$ad' },'traffic': { '$push': '$traffic' } } }
        setId = self.setId(CollateType.MARKETPLACE, CollectionType.DATE_ANALYTICS)
        await self.dbClient.state_analytics.db.aggregate([matchStage, group, self.openId(), self.collate(), setId, self.pp.merge(CollectionType.DATE_ANALYTICS)])
