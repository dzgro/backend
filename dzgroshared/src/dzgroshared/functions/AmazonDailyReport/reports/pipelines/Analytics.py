from datetime import datetime
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DataTransformer import Datatransformer
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.models.enums import CollateType, CollectionType
from dzgroshared.models.model import StartEndDate
from dzgroshared.utils import date_util

class PipelineBuilder:

    client: DzgroSharedClient
    pp: PipelineProcessor

    def __init__(self, client: DzgroSharedClient):
        self.client = client
        self.pp = PipelineProcessor(self.client.uid, self.client.marketplace)

    def match(self, date: datetime):
        return { '$match': { 'uid': self.client.uid, 'marketplace': self.client.marketplace, 'date': date } }
    
    def matchCollateTypeAndDate(self, date: datetime, collatetype:CollateType):
        return { '$match': { 'uid': self.client.uid, 'marketplace': self.client.marketplace, 'date': date, 'collatetype': collatetype.value } }

    def lookupSettlements(self):
        return { '$lookup': { 'from': 'settlements', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'orderid': '$orderid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$orderid', '$$orderid' ] } ] } } } ], 'as': 'settlement' } }
    
    def lookupOrderItems(self):
        return { '$lookup': { 'from': 'order_items', 'localField': '_id', 'foreignField': 'order', 'as': 'orderitem' } }
    
    def addOrderValueTax(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': '$orderitem', 'initialValue': { 'orderValue': 0, 'orderTax': 0 }, 'in': { '$mergeObjects': [ '$$value', { 'orderValue': { '$sum': [ '$$value.orderValue', '$$this.revenue' ] }, 'orderTax': { '$sum': [ '$$value.orderTax', '$$this.tax' ] } } ] } } } ] } } }
    
    def unwindOrderItems(self):
        return { '$unwind': { 'path': '$orderitem', 'preserveNullAndEmptyArrays': False } }
    
    def getSkuValues(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$and': [ { '$in': [ '$$s.amounttype', [ 'ItemPrice', 'ItemTax' ] ] }, { '$eq': [ '$$s.sku', '$orderitem.sku' ] } ] } } }, 'initialValue': { 'skuValue': 0, 'skuTax': 0, 'skuReturnValue': 0, 'skuReturnTax': 0 }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$eq': [ '$$this.transactiontype', 'Refund' ] }, 'then': { '$cond': { 'if': { '$eq': [ '$$this.amounttype', 'ItemPrice' ] }, 'then': { 'skuReturnValue': { '$sum': [ '$$value.skuReturnValue', '$$this.amount' ] } }, 'else': { 'skuReturnTax': { '$sum': [ '$$value.skuReturnTax', '$$this.amount' ] } } } }, 'else': { '$cond': { 'if': { '$eq': [ '$$this.amounttype', 'ItemPrice' ] }, 'then': { 'skuValue': { '$sum': [ '$$value.skuValue', '$$this.amount' ] } }, 'else': { 'skuTax': { '$sum': [ '$$value.skuTax', '$$this.amount' ] } } } } } } ] } } } ] } } }
    
    def setSkuRatio(self):
        return { '$set': { 'skuRatio': { '$cond': { 'if': { '$eq': [ '$orderValue', 0 ] }, 'then': 0, 'else': { '$divide': [ '$orderitem.revenue', '$orderValue' ] } } } } }
    
    def reduceSettlements(self):
        return { '$set': { 'settlement': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$and': [ { '$not': { '$in': [ '$$s.amounttype', [ 'ItemPrice', 'ItemTax' ] ] } }, { '$or': [ { '$eq': [ { '$ifNull': [ '$$s.sku', None ] }, None ] }, { '$eq': [ '$$s.sku', '$orderitem.sku' ] } ] } ] } } } } }
    
    def addSkuFees(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': '$settlement', 'initialValue': { 'skufees': 0, 'nonskufees': 0 }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$ifNull': [ '$$this.sku', False ] }, 'then': { 'nonskufees': { '$sum': [ '$$value.nonskufees', '$$this.amount' ] } }, 'else': { 'skufees': { '$sum': [ '$$value.skufees', '$$this.amount' ] } } } } ] } } } ] } } }
    
    def addNonSkuFees(self):
        return { '$set': { 'nonskufees': { '$round': [ { '$multiply': [ '$nonskufees', '$skuRatio' ] }, 2 ] }, 'skuReturnValue': { '$sum': [ '$skuReturnValue', '$skuReturnTax' ] }, 'expenses': { '$sum': [ '$skufees', '$nonskufees' ] }, 'quantity': '$orderitem.quantity', 'returnQuantity': { '$cond': { 'if': { '$eq': [ '$skuValue', 0 ] }, 'then': 0, 'else': { '$round': [ { '$multiply': [ '$orderitem.quantity', { '$divide': [ { '$abs': '$skuReturnValue' }, '$skuValue' ] } ] } ] } } } } }
    
    def addNetProceeds(self):
        return { '$set': { 'netproceeds': { '$cond': { 'if': { '$eq': [ { '$size': '$settlement' }, 0 ] }, 'then': 0, 'else': { '$add': [ '$skuValue', '$skuReturnValue', '$expenses' ] } } } } }
    
    def createData(self):
        return { '$set': { 'data': { 'netproceeds': '$netproceeds', 'ordervalue': '$skuValue', 'returnvalue': '$skuReturnValue', 'quantity': '$quantity', 'returnQuantity': '$returnQuantity', 'fees': '$skufees', 'otherexpenses': '$nonskufees', 'expenses': '$expenses' } } }
    
    def projectData(self):
        return { '$project': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$orderitem.sku', 'parent': '$orderitem.asin', 'state': '$state', 'date': '$date', 'data': '$data', '_id': 0 } }

    def groupByState(self):
        return { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$sku', 'parent': '$parent', 'state': '$state', 'date': '$date' }, 'data': { '$push': '$data' } } }
    
    def collateData(self, key:str='data'):
        return Datatransformer(self.pp, key).collateData()
    
    def removeEmptyDataSets(self):
        return { '$match': { '$expr': { '$gt': [ { '$sum': { '$map': { 'input': { '$objectToArray': '$data' }, 'as': 'kv', 'in': { '$abs': '$$kv.v' } } } }, 0 ] } } }
    
    def createIdForState(self, collatetype: CollateType):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'collatetype': collatetype.value, 'data': '$data', '_id': { '$concat': [ { '$toString': [ '$_id.marketplace' ] }, '_', '$_id.value', '_', { '$dateToString': { 'date': '$_id.date' } }, '_', '$_id.state' ] } } ] } } }
    
    def createIdForDate(self, collatetype: CollateType):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'collatetype': collatetype.value, 'data': '$data', '_id': { '$concat': [ { '$toString': [ '$_id.marketplace' ] }, '_', '$_id.value', '_', { '$dateToString': { 'date': '$_id.date' } } ] } } ] } } }
    
    def mergeToStateAnalytics(self):
        return self.pp.merge(CollectionType.STATE_ANALYTICS)
    
    def mergeToDateAnalytics(self):
        return self.pp.merge(CollectionType.DATE_ANALYTICS)

    def groupStateAnalyticsByDate(self):
        return { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$value', 'parent': '$parent', 'date': '$date' }, 'data': { '$push': '$data' } } }

    def groupStateAnalyticsByParent(self):
        return { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'parent': '$parent', 'date': '$date' }, 'data': { '$push': '$data' } } }

    def groupDateAnalyticsByValue(self):
        return { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$value', 'date': '$date' }, 'data': { '$push': '$data' } } }
    
    def lookupAds(self):
        return { '$lookup': { 'from': 'adv', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'assettype': 'Ad', 'date': '$date', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }
    
    def lookupTraffic(self):
        return { '$lookup': { 'from': 'traffic', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$value', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$traffic' } } ], 'as': 'traffic' } }
    
    def mergeDataWithAdTraffic(self):
        return { '$set': { 'data': { '$mergeObjects': [ '$data', '$ad' ] } } }
    
    def hideAdTraffic(self):
        return { '$project': { 'ad': 0 } }
    
    def addParentSku(self):
        return { "$lookup": { "from": "products", "let": { "uid": "$uid", "marketplace": "$marketplace", "asin": "$value" }, "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": ["$uid", "$$uid"] }, { "$eq": [ "$marketplace", "$$marketplace" ] }, { "$eq": ["$asin", "$$asin"] } ] } } }, { "$project": { "parent": "$parentsku", "_id": 0 } } ], "as": "parent" } }
    
    def setParentSku(self):
        return { "$set": { "parent": { "$first": "$parent.parent" } } }
    
    def addProductType(self):
        return { "$lookup": { "from": "products", "let": { "uid": "$uid", "marketplace": "$marketplace", "asin": "$value" }, "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": ["$uid", "$$uid"] }, { "$eq": [ "$marketplace", "$$marketplace" ] }, { "$eq": ["$asin", "$$asin"] } ] } } }, { "$project": { "parent": "$parentsku", "_id": 0 } } ], "as": "parent" } }
    
    def setProductType(self):
        return { "$set": { "parent": { "$first": "$parent.parent" } } }



    async def executeSkuState(self, date: datetime):
        pipeline = [
            self.match(date),
            self.lookupSettlements(),
            self.lookupOrderItems(),
            self.addOrderValueTax(),
            self.unwindOrderItems(),
            self.getSkuValues(),
            self.setSkuRatio(),
            self.reduceSettlements(),
            self.addSkuFees(),
            self.addNonSkuFees(),
            self.addNetProceeds(),
            self.createData(),
            self.projectData(),
            self.groupByState(),
            self.collateData(),
            self.removeEmptyDataSets(),
            self.createIdForState(CollateType.SKU),
            self.mergeToStateAnalytics()
        ]
        await self.client.db.orders.db.aggregate(pipeline)

    async def executeSkuDate(self, date: datetime):
        pipeline = [
            self.matchCollateTypeAndDate(date, CollateType.SKU),
            self.groupStateAnalyticsByDate(),
            self.collateData(),
            self.createIdForDate(CollateType.SKU),
            self.lookupAds(),
            self.collateData('ad'),
            self.mergeDataWithAdTraffic(),
            self.hideAdTraffic(),
            self.mergeToDateAnalytics()
        ]
        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def executeSku(self, date: datetime):
        await self.executeSkuState(date)
        await self.executeSkuDate(date)

    async def executeAsinState(self, date: datetime):
        pipeline = [
            self.matchCollateTypeAndDate(date, CollateType.SKU),
            self.groupStateAnalyticsByParent(),
            self.collateData(),
            self.createIdForState(CollateType.ASIN),
            self.addParentSku(),
            self.setParentSku(),
            self.mergeToStateAnalytics()
        ]
        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def executeAsinDate(self, date: datetime):
        pipeline = [
            self.matchCollateTypeAndDate(date, CollateType.ASIN),
            self.groupStateAnalyticsByDate(),
            self.collateData(),
            self.createIdForDate(CollateType.ASIN),
            self.lookupTraffic(),
            self.collateData('traffic'),
            self.mergeDataWithAdTraffic(),
            self.hideAdTraffic(),
            self.mergeToDateAnalytics(),
        ]
        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def executeAsin(self, date: datetime):
        await self.executeAsinState(date)
        await self.executeAsinDate(date)

    async def executeParentState(self, date: datetime):
        pipeline = [
            self.matchCollateTypeAndDate(date, CollateType.ASIN),
            self.groupStateAnalyticsByParent(),
            self.collateData(),
            self.createIdForState(CollateType.PARENT),
            self.mergeToStateAnalytics()
        ]
        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def executeParentDate(self, date: datetime):
        pipeline = [
            self.matchCollateTypeAndDate(date, CollateType.PARENT),
            self.groupStateAnalyticsByDate(),
            self.collateData(),
            self.createIdForDate(CollateType.PARENT),
            self.mergeToDateAnalytics(),
        ]
        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def executeParent(self, date: datetime):
        await self.executeParentState(date)
        await self.executeParentDate(date)

    async def categoryDate(self, date: datetime):
        pipeline = [
            self.matchCollateTypeAndDate(date, CollateType.ASIN),
            self.groupDateAnalyticsByValue(),
            self.collateData(),
            self.addProductType(),
            self.setProductType(),
            self.createIdForDate(CollateType.CATEGORY),
            {"$set": {"value": "parent"}},
            {"$project": {"value": 0}},
            self.mergeToDateAnalytics(),
        ]
        await self.client.db.date_analytics.db.aggregate(pipeline)

    async def execute(self, date: datetime):
        for collateType in CollateType.values():
            if collateType==CollateType.SKU: await self.executeSku(date)
            elif collateType==CollateType.ASIN: await self.executeAsin(date)
            elif collateType==CollateType.PARENT: await self.executeParent(date)
            elif collateType==CollateType.CATEGORY: await self.categoryDate(date)



class AnalyticsProcessor:
    client: DzgroSharedClient
    pp: PipelineProcessor
    dates: StartEndDate

    def __init__(self, client: DzgroSharedClient, dates: StartEndDate):
        self.client = client
        self.dates = dates
        self.pp = self.client.db.state_analytics.db.pp


    async def executeDate(self, date: datetime|None, collateTypes: list[CollateType] = list(CollateType)):
        if not date: 
            await self.client.db.state_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
            await self.client.db.date_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
            date = self.dates.enddate
        print(f'-----------------------{date.strftime("%Y-%m-%d")}--------------------------------')
        for collateType in collateTypes:
            if collateType==CollateType.SKU: await self.createSkuAnalytics(date)
            elif collateType==CollateType.ASIN: await self.createAsinAnalytics(date)
            elif collateType==CollateType.PARENT: await self.createParentAnalytics(date)
            elif collateType==CollateType.CATEGORY: await self.createCategoryAnalytics(date)
            else: await self.createMarketplaceAnalytics(date)
        dates = date_util.getAllDatesBetweenTwoDates(self.dates.startdate, self.dates.enddate)
        index = dates.index(date)
        nextDate = dates[index-1] if index>0 else None
        return nextDate

    async def createSkuAnalytics(self, date):
        pipeline = [ { '$match': { 'uid': self.client.uid, 'marketplace': self.client.marketplace, 'date': date } }, { '$lookup': { 'from': 'settlements', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'orderid': '$orderid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$orderid', '$$orderid' ] } ] } } } ], 'as': 'settlement' } }, { '$lookup': { 'from': 'order_items', 'localField': '_id', 'foreignField': 'order', 'as': 'orderitem' } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': '$orderitem', 'initialValue': { 'orderValue': 0, 'orderTax': 0 }, 'in': { '$mergeObjects': [ '$$value', { 'orderValue': { '$sum': [ '$$value.orderValue', '$$this.revenue' ] }, 'orderTax': { '$sum': [ '$$value.orderTax', '$$this.tax' ] } } ] } } } ] } } }, { '$unwind': { 'path': '$orderitem', 'preserveNullAndEmptyArrays': False } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$and': [ { '$in': [ '$$s.amounttype', [ 'ItemPrice', 'ItemTax' ] ] }, { '$eq': [ '$$s.sku', '$orderitem.sku' ] } ] } } }, 'initialValue': { 'skuValue': 0, 'skuTax': 0, 'skuReturnValue': 0, 'skuReturnTax': 0 }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$eq': [ '$$this.transactiontype', 'Refund' ] }, 'then': { '$cond': { 'if': { '$eq': [ '$$this.amounttype', 'ItemPrice' ] }, 'then': { 'skuReturnValue': { '$sum': [ '$$value.skuReturnValue', '$$this.amount' ] } }, 'else': { 'skuReturnTax': { '$sum': [ '$$value.skuReturnTax', '$$this.amount' ] } } } }, 'else': { '$cond': { 'if': { '$eq': [ '$$this.amounttype', 'ItemPrice' ] }, 'then': { 'skuValue': { '$sum': [ '$$value.skuValue', '$$this.amount' ] } }, 'else': { 'skuTax': { '$sum': [ '$$value.skuTax', '$$this.amount' ] } } } } } } ] } } } ] } } }, { '$set': { 'skuRatio': { '$cond': { 'if': { '$eq': [ '$orderValue', 0 ] }, 'then': 0, 'else': { '$divide': [ '$orderitem.revenue', '$orderValue' ] } } } } }, { '$set': { 'settlement': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$and': [ { '$not': { '$in': [ '$$s.amounttype', [ 'ItemPrice', 'ItemTax' ] ] } }, { '$or': [ { '$eq': [ { '$ifNull': [ '$$s.sku', None ] }, None ] }, { '$eq': [ '$$s.sku', '$orderitem.sku' ] } ] } ] } } } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': '$settlement', 'initialValue': { 'skufees': 0, 'nonskufees': 0 }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$ifNull': [ '$$this.sku', False ] }, 'then': { 'nonskufees': { '$sum': [ '$$value.nonskufees', '$$this.amount' ] } }, 'else': { 'skufees': { '$sum': [ '$$value.skufees', '$$this.amount' ] } } } } ] } } } ] } } }, { '$set': { 'nonskufees': { '$round': [ { '$multiply': [ '$nonskufees', '$skuRatio' ] }, 2 ] }, 'skuReturnValue': { '$sum': [ '$skuReturnValue', '$skuReturnTax' ] }, 'expenses': { '$sum': [ '$skufees', '$nonskufees' ] }, 'quantity': '$orderitem.quantity', 'returnQuantity': { '$cond': { 'if': { '$eq': [ '$skuValue', 0 ] }, 'then': 0, 'else': { '$round': [ { '$multiply': [ '$orderitem.quantity', { '$divide': [ { '$abs': '$skuReturnValue' }, '$skuValue' ] } ] } ] } } } } }, { '$set': { 'netproceeds': { '$cond': { 'if': { '$eq': [ { '$size': '$settlement' }, 0 ] }, 'then': 0, 'else': { '$add': [ '$skuValue', '$skuReturnValue', '$expenses' ] } } } } }, { '$set': { 'data': { 'netproceeds': '$netproceeds', 'ordervalue': '$skuValue', 'returnvalue': '$skuReturnValue', 'quantity': '$quantity', 'returnQuantity': '$returnQuantity', 'fees': '$skufees', 'otherexpenses': '$nonskufees', 'expenses': '$expenses' } } }, { '$project': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$orderitem.sku', 'parent': '$orderitem.asin', 'state': '$state', 'date': '$date', 'data': '$data', '_id': 0 } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$sku', 'parent': '$parent', 'state': '$state', 'date': '$date' }, 'data': { '$push': '$data' } } }, { '$set': { 'data': { '$reduce': { 'input': '$data', 'initialValue': {}, 'in': { '$arrayToObject': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } } } } } } }, { '$match': { '$expr': { '$gt': [ { '$sum': { '$map': { 'input': { '$objectToArray': '$data' }, 'as': 'kv', 'in': { '$abs': '$$kv.v' } } } }, 0 ] } } },{ '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'collatetype': 'sku', 'data': '$data', '_id': { '$concat': [ { '$toString': [ '$_id.marketplace' ] }, '_', '$_id.value', '_', { '$dateToString': { 'date': '$_id.date' } }, '_', '$_id.state' ] } } ] } } }, { '$merge': 'state_analytics' }]
        await self.client.db.orders.db.aggregate(pipeline)
        pipeline = [ { '$match': { 'uid': self.client.uid, 'marketplace': self.client.marketplace, 'date': date } }, ,  ]
        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def createAsinAnalytics(self, date):
        

        await self.client.db.state_analytics.db.aggregate(pipeline)

    async def createParentAnalytics(self, date):
        pipeline = [ { '$match': { 'uid': self.client.uid, 'marketplace': self.client.marketplace, 'date': date, 'colatetype':'asin' } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$parent', 'date': '$date', 'state':"$state" }, 'data': { '$push': '$data' } } }, { '$set': { 'data': { '$reduce': { 'input': '$data', 'initialValue': {}, 'in': { '$arrayToObject': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } } } } } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'colatetype': 'parentsku', 'data': '$data', '_id': { '$concat': [ { '$toString': [ '$_id.marketplace' ] }, '_', '$_id.value', '_', { '$dateToString': { 'date': '$_id.date' } }, '_', '$_id.state' ] } } ] } } }, { '$merge': 'state_analytics' } ]
        
        await self.client.db.state_analytics.db.aggregate(pipeline)

