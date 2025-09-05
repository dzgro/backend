from datetime import datetime
import time
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DataTransformer import Datatransformer
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.models.enums import ENVIRONMENT, CollateType, CollectionType
from dzgroshared.models.model import LambdaContext, StartEndDate
from dzgroshared.utils import date_util, mongo_pipeline_print

class AnalyticsProcessor:

    client: DzgroSharedClient
    pp: PipelineProcessor
    dates: StartEndDate
    allDates: list[datetime]

    def __init__(self, client: DzgroSharedClient, dates: StartEndDate):
        self.client = client
        self.dates = dates
        self.pp = PipelineProcessor(self.client.uid, self.client.marketplace)
        self.allDates = date_util.getAllDatesBetweenTwoDates(self.dates.startdate, self.dates.enddate)



    def matchmarketplace(self):
        return { '$match': { '_id': self.client.marketplace, 'uid': self.client.uid } }
    
    def setDates(self):
        datesObj = self.dates.model_dump()
        return { '$set': { 'dates': datesObj } }

    def openDates(self):
        return {"$set": { "date": { "$map": { "input": { "$range": [ 0, { "$sum": [ { "$dateDiff": { "startDate": "$dates.startdate", "endDate": "$dates.enddate", "unit": "day" } }, 1 ] }, 1 ] }, "as": "day", "in": { "$dateAdd": { "startDate": "$dates.startdate", "unit": "day", "amount": "$$day" } } } } }}
    
    def openDate(self):
        return {"$unwind": "$date"}

    def match(self, date: datetime):
        return { '$match': { 'uid': self.client.uid, 'marketplace': self.client.marketplace, 'date': date } }
    
    def lookupSettlements(self):
        return { '$lookup': { 'from': 'settlements', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'orderid': '$orderid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$orderid', '$$orderid' ] } ] } } } ], 'as': 'settlement' } }
    
    def lookupOrderItems(self):
        return { '$lookup': { 'from': 'order_items', 'localField': '_id', 'foreignField': 'order', 'as': 'orderitem' } }

    def addOrderValueTax(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': '$orderitem', 'initialValue': { 'orderValue': 0, 'orderTax': 0, 'orders': 1, 'cancelledorders': { '$cond': { 'if': { '$eq': [ '$orderstatus', 'Cancelled' ] }, 'then': 1, 'else': 0 } }, 'fbmordervalue': 0, 'fbaordervalue': 0, 'fbmorders': { '$cond': { 'if': { '$eq': [ '$fulfillment', 'Merchant' ] }, 'then': 1, 'else': 0 } }, 'fbaorders': { '$cond': { 'if': { '$and': [ { '$ne': [ '$orderstatus', 'Cancelled' ] }, { '$ne': [ '$fulfillment', 'Merchant' ] } ] }, 'then': 1, 'else': 0 } } }, 'in': { '$mergeObjects': [ '$$value', { 'orderValue': { '$sum': [ '$$value.orderValue', '$$this.revenue' ] }, 'orderTax': { '$sum': [ '$$value.orderTax', '$$this.tax' ] }, 'fbaordervalue': { '$sum': [ '$$value.fbaordervalue', { '$cond': { 'if': { '$ne': [ '$fulfillment', 'Merchant' ] }, 'then': '$$this.revenue', 'else': 0 } } ] }, 'fbmordervalue': { '$sum': [ '$$value.fbmordervalue', { '$cond': { 'if': { '$eq': [ '$fulfillment', 'Merchant' ] }, 'then': '$$this.revenue', 'else': 0 } } ] } } ] } } } ] } } }
    
    def unwindOrderItems(self):
        return { '$unwind': { 'path': '$orderitem', 'preserveNullAndEmptyArrays': False } }
    
    def getSkuValues(self):
        return { '$replaceRoot': { "newRoot": { "$mergeObjects": [ "$$ROOT", { "$reduce": { "input": { "$filter": { "input": "$settlement", "as": "s", "cond": { "$and": [ { "$in": [ "$$s.amounttype", ["ItemPrice", "ItemTax"] ] }, { "$eq": [ "$$s.sku", "$orderitem.sku" ] }, { "$eq": [ "$$s.transactiontype", "Refund" ] } ] } } }, "initialValue": { "skuValue": "$orderitem.revenue", "skuTax": "$orderitem.tax", "skuReturnValue": 0, "skuReturnTax": 0 }, "in": { "$mergeObjects": [ "$$value", { "$cond": { "if": { "$eq": [ "$$this.amounttype", "ItemPrice" ] }, "then": { "skuReturnValue": { "$sum": [ "$$value.skuReturnValue", "$$this.amount" ] } }, "else": { "skuReturnTax": { "$sum": [ "$$value.skuReturnTax", "$$this.amount" ] } } } } ] } } } ] } } }
    
    def setSkuRatio(self):
        return { '$set': { 'skuRatio': { '$cond': { 'if': { '$eq': [ '$orderValue', 0 ] }, 'then': 0, 'else': { '$divide': [ '$orderitem.revenue', '$orderValue' ] } } } } }
    
    def reduceSettlements(self):
        return { '$set': { 'settlement': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$and': [ { '$not': { '$in': [ '$$s.amounttype', [ 'ItemPrice', 'ItemTax' ] ] } }, { '$or': [ { '$eq': [ { '$ifNull': [ '$$s.sku', None ] }, None ] }, { '$eq': [ '$$s.sku', '$orderitem.sku' ] } ] } ] } } } } }
    
    def addSkuFees(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$reduce': { 'input': '$settlement', 'initialValue': { 'skufees': 0, 'nonskufees': 0 }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$ifNull': [ '$$this.sku', False ] }, 'then': { 'nonskufees': { '$sum': [ '$$value.nonskufees', '$$this.amount' ] } }, 'else': { 'skufees': { '$sum': [ '$$value.skufees', '$$this.amount' ] } } } } ] } } } ] } } }
    
    def addNonSkuFees(self):
        return { '$set': { 'nonskufees': { '$round': [ { '$multiply': [ '$nonskufees', '$skuRatio' ] }, 2 ] }, 'skuReturnValue': { '$sum': [ '$skuReturnValue', '$skuReturnTax' ] }, 'quantity': '$orderitem.quantity', 'returnQuantity': { '$cond': { 'if': { '$eq': [ '$skuValue', 0 ] }, 'then': 0, 'else': { '$round': [ { '$multiply': [ '$orderitem.quantity', { '$divide': [ { '$abs': '$skuReturnValue' }, '$skuValue' ] } ] } ] } } } } }
    
    def addNetProceeds(self):
        return { '$set': { 'netproceeds': { '$cond': { 'if': { '$eq': [ { '$size': '$settlement' }, 0 ] }, 'then': 0, 'else': { '$add': [ '$skuValue', '$skuReturnValue', '$skufees', '$nonskufees' ] } } } } }
    
    def createData(self):
        return { '$set': { 'data': { 'netproceeds': '$netproceeds', 'ordervalue': '$skuValue', 'ordertax': '$skuTax', 'returnvalue': '$skuReturnValue', 'quantity': '$quantity', 'returnQuantity': '$returnQuantity', 'fees': '$skufees', 'otherexpenses': '$nonskufees', 'orders': '$orders', 'cancelledorders': '$cancelledorders', 'fbmordervalue': '$fbmordervalue', 'fbaordervalue': '$fbaordervalue', 'fbmorders': '$fbmorders', 'fbaorders': '$fbaorders' } }}
    
    def projectData(self):
        return { '$project': { 'uid': '$uid', 'marketplace': '$marketplace', 'sku': '$orderitem.sku', 'parent': '$orderitem.asin', 'state': '$state', 'date': '$date', 'data': '$data', '_id': 0 } }

    def groupByState(self):
        return { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$sku', 'parent': '$parent', 'state': '$state', 'date': '$date' }, 'data': { '$push': '$data' } } }
    
    def collateData(self, key:str='data'):
        return Datatransformer(self.pp, key).collateData()
    
    def setData(self, isState: bool, collatetype:CollateType):
        curr = { "uid": "$$current.uid", "marketplace": "$$current.marketplace", "date": "$$current.date", "data": ["$$current.data"] }
        cond = [ { "$eq": ["$$g.uid", "$$this.uid"] }, { "$eq": ["$$g.marketplace", "$$this.marketplace"] },{ "$eq": ["$$g.date", "$$this.date"] } ]
        if collatetype==CollateType.SKU: curr.update({'value': '$$current.value','parent': '$$current.parent', "parentsku": "$$current.parentsku", "category": "$$current.category"})
        elif collatetype==CollateType.ASIN: curr.update({'value': '$$current.parent','parent': '$$current.parentsku', "category": "$$current.category"})
        elif collatetype==CollateType.PARENT: curr.update({'value': '$$current.parent'})
        elif collatetype==CollateType.CATEGORY: curr.update({'value': '$$current.category'})
        if isState:
            curr.update({'state': '$$current.state'})
            cond.append( { "$eq": ["$$g.state", "$$this.state"] } )
        return {"$set": { "data": { "$reduce": { "input": "$data", "initialValue": [], "in": { "$let": { "vars": { "current": "$$this", "existing": { "$filter": { "input": "$$value", "as": "g", "cond": { "$and": cond } } } }, "in": { "$cond": [ { "$gt": [{ "$size": "$$existing" }, 0] }, { "$map": { "input": "$$value", "as": "g", "in": { "$cond": [ { "$and": cond }, { "$mergeObjects": [ "$$g", { "data": { "$concatArrays": ["$$g.data", ["$$current.data"]] } } ] }, "$$g" ] } } }, { "$concatArrays": [ "$$value", [ curr ] ] } ] } } } } } }}

    
    def removeEmptyDataSets(self):
        return { '$match': { '$expr': { '$gt': [ { '$sum': { '$map': { 'input': { '$objectToArray': '$data' }, 'as': 'kv', 'in': { '$abs': '$$kv.v' } } } }, 0 ] } } }
    
    def createIdForStateSku(self):
        return { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'collatetype': CollateType.SKU.value, 'data': '$data', '_id': { '$concat': [ { '$toString': [ '$_id.marketplace' ] }, '_', "$_id.value", '_', { '$dateToString': { 'date': '$_id.date', 'format': '%Y-%m-%d' } }, '_', '$_id.state' ] } } ] } } }

    def setIdForState(self, collatetype: CollateType):
        value = '$value' if collatetype!=CollateType.MARKETPLACE else collatetype.value
        return {"$set": { 'collatetype': collatetype.value, '_id': { '$concat': [ { '$toString': [ '$marketplace' ] }, '_', value, '_', { '$dateToString': { 'date': '$date' , 'format': '%Y-%m-%d' } }, "_","$state" ] } }}
    
    def setIdForDate(self, collatetype: CollateType):
        value = '$value' if collatetype!=CollateType.MARKETPLACE else collatetype.value
        return {"$set": { 'collatetype': collatetype.value, '_id': { '$concat': [ { '$toString': [ '$marketplace' ] }, '_', value, '_', { '$dateToString': { 'date': '$date' , 'format': '%Y-%m-%d' } } ] } }}


    def mergeToStateAnalytics(self):
        return self.pp.merge(CollectionType.STATE_ANALYTICS)
    
    def mergeToDateAnalytics(self):
        return self.pp.merge(CollectionType.DATE_ANALYTICS)
    
    def lookupStateAnalytics(self, collatetype: CollateType):
        pipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] }] } } } ]
        return { '$lookup': { 'from': 'state_analytics', 'let': { 'uid': '$uid', 'marketplace': '$_id', 'collatetype': collatetype.value, 'date': '$date'}, 'pipeline': pipeline, 'as': 'data' } }
    
    def lookupDateAnalytics(self, collatetype: CollateType):
        pipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] } ] } } } ]
        return { '$lookup': { 'from': 'date_analytics', 'let': { 'uid': '$uid', 'marketplace': '$_id', 'collatetype': collatetype.value, 'date': '$date', }, 'pipeline': pipeline, 'as': 'data' } }

    def groupStateAnalyticsByDate(self):
        return { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'value': '$value', 'parent': '$parent', 'date': '$date', 'collatetype': "$collatetype" }, 'data': { '$push': '$data' } } }
    
    def lookupAds(self):
        return { '$lookup': { 'from': 'adv', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'assettype': 'Ad', 'date': '$date', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }
    
    def lookupTraffic(self):
        return { '$lookup': { 'from': 'traffic', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$value', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$traffic' } } ], 'as': 'traffic' } }
    
    def mergeDataWithAdTraffic(self):
        return { '$set': { 'data': { '$mergeObjects': [ '$data', '$ad', '$traffic' ] } } }
    
    def hideAdTraffic(self):
        return { '$project': { 'ad': 0, 'traffic': 0 } }
    
    def addParentSku(self):
        return { "$lookup": { "from": "products", "let": { "uid": "$uid", "marketplace": "$marketplace", "sku": "$value" }, "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": ["$uid", "$$uid"] }, { "$eq": [ "$marketplace", "$$marketplace" ] }, { "$eq": ["$sku", "$$sku"] } ] } } }, { "$project": { "parent": "$parentsku", "category": "$producttype", "_id": 0 } } ], "as": "product" } }

    def setParentSku(self):
        return { "$set": { "parentsku": { "$first": "$product.parent" }, "category": { "$first": "$product.category" } } }

    def addProductType(self):
        return { "$lookup": { "from": "products", "let": { "uid": "$uid", "marketplace": "$marketplace", "asin": "$value" }, "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": ["$uid", "$$uid"] }, { "$eq": [ "$marketplace", "$$marketplace" ] }, { "$eq": ["$asin", "$$asin"] } ] } } }, { "$project": { "parent": "$parentsku", "_id": 0 } } ], "as": "parent" } }
    
    def setProductType(self):
        return { "$set": { "parent": { "$first": "$parent.parent" } } }

    def matchMarketplaceSetAndOpenDates(self):
        return [
            self.matchmarketplace(),
            self.setDates(),
            self.openDates(),
            self.openDate()
        ]
    
    
    def lookupOrders(self, pipeline: list[dict]):
        pipeline = [{ '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] } ] } } }] + pipeline
        return { '$lookup': { 'from': 'orders', 'let': {"uid": "$uid", "marketplace": "$_id", "date": "$date"}, 'pipeline': pipeline, 'as': 'data' } }
    
    def opendata(self):
        return { '$unwind': { 'path': '$data', 'preserveNullAndEmptyArrays': False } }
    
    def setDataAsRoot(self):
        return { '$replaceRoot': { 'newRoot': '$data' } }


    async def executeSkuDate(self):
        pipeline = self.matchMarketplaceSetAndOpenDates()
        pipeline.append(self.lookupStateAnalytics(CollateType.SKU))
        pipeline.extend([
            self.setData(False, CollateType.SKU),
            self.opendata(),
            self.setDataAsRoot(),
            self.collateData(),
            self.setIdForDate(CollateType.SKU),
            self.lookupAds(),
            self.collateData('ad'),
            self.mergeDataWithAdTraffic(),
            self.hideAdTraffic(),
            self.mergeToDateAnalytics()
        ])
        
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)


    async def executeAsinDate(self):
        pipeline = self.matchMarketplaceSetAndOpenDates()
        pipeline.append(self.lookupDateAnalytics(CollateType.SKU))
        pipeline.extend([
            self.setData(False, CollateType.ASIN),
            self.opendata(),
            self.setDataAsRoot(),
            self.collateData(),
            self.setIdForDate(CollateType.ASIN),
            self.lookupTraffic(),
            self.collateData('traffic'),
            self.mergeDataWithAdTraffic(),
            self.hideAdTraffic(),
            self.mergeToDateAnalytics()
        ])
        
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)

    async def executeParentDate(self):
        pipeline = self.matchMarketplaceSetAndOpenDates()
        pipeline.append(self.lookupDateAnalytics(CollateType.ASIN))
        pipeline.extend([
            self.setData(False, CollateType.PARENT),
            self.opendata(),
            self.setDataAsRoot(),
            self.collateData(),
            self.setIdForDate(CollateType.PARENT),
            self.lookupTraffic(),
            self.collateData('traffic'),
            self.mergeDataWithAdTraffic(),
            self.hideAdTraffic(),
            {"$match": {"_id": {"$ne": None}}},
            {"$project": {"category": 0}},
            self.mergeToDateAnalytics()
        ])
        
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)


    async def executeCategoryDate(self):
        pipeline = self.matchMarketplaceSetAndOpenDates()
        pipeline.append(self.lookupDateAnalytics(CollateType.ASIN))
        pipeline.extend([
            self.setData(False, CollateType.CATEGORY),
            self.opendata(),
            self.setDataAsRoot(),
            self.collateData(),
            self.setIdForDate(CollateType.CATEGORY),
            self.mergeToDateAnalytics()
        ])
        
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)

    async def executeMarketplaceDate(self):
        pipeline = self.matchMarketplaceSetAndOpenDates()
        pipeline.append(self.lookupDateAnalytics(CollateType.ASIN))
        pipeline.extend([
            self.setData(False, CollateType.MARKETPLACE),
            self.opendata(),
            self.setDataAsRoot(),
            self.collateData(),
            self.setIdForDate(CollateType.MARKETPLACE),
            {"$match": {"_id": {"$ne": None}}},
            {"$project": {"category": 0, "parentsku": 0}},
            self.mergeToDateAnalytics()
        ])
        
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)


    async def execute(self):
        await self.client.db.state_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
        await self.client.db.date_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
        start_time = time.perf_counter()
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines import CreateStateAnalytics
        statepipeline = CreateStateAnalytics.pipeline(self.client.uid, self.client.marketplace, self.dates)
        await self.client.db.marketplaces.marketplaceDB.aggregate(statepipeline)
        await self.executeSkuDate()
        await self.executeAsinDate()
        await self.executeParentDate()
        await self.executeCategoryDate()
        await self.executeMarketplaceDate()
        process_time_seconds = (time.perf_counter() - start_time)  # ms
        print(f"Total Analytics took {process_time_seconds:.4f} seconds")

        

        