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
        self.pp = PipelineProcessor(self.client.uid, self.client.marketplaceId)
        self.allDates = date_util.getAllDatesBetweenTwoDates(self.dates.startdate, self.dates.enddate)

    def __matchmarketplace(self):
        return { '$match': { '_id': self.client.marketplaceId, 'uid': self.client.uid } }
    
    def __setDates(self):
        datesObj = self.dates.model_dump()
        return { '$set': { 'dates': datesObj } }

    def __openDates(self):
        return {"$set": { "date": { "$map": { "input": { "$range": [ 0, { "$sum": [ { "$dateDiff": { "startDate": "$dates.startdate", "endDate": "$dates.enddate", "unit": "day" } }, 1 ] }, 1 ] }, "as": "day", "in": { "$dateAdd": { "startDate": "$dates.startdate", "unit": "day", "amount": "$$day" } } } } }}
    
    def __openDate(self):
        return {"$unwind": "$date"}

    def __collateData(self, key:str='data'):
        return Datatransformer(self.pp, key).collateData()
    
    def __setData(self, collatetype:CollateType):
        curr = { "marketplace": "$$current.marketplace", "date": "$$current.date", "data": ["$$current.data"] }
        cond = [ { "$eq": ["$$g.marketplace", "$$this.marketplace"] },{ "$eq": ["$$g.date", "$$this.date"] } ]
        if collatetype==CollateType.SKU: 
            curr.update({'value': '$$current.value','parent': '$$current.parent', "parentsku": "$$current.parentsku", "category": "$$current.category"})
            cond.append( { "$eq": ["$$g.value", "$$this.value"] } )
        elif collatetype==CollateType.ASIN: curr.update({'value': '$$current.parent','parent': '$$current.parentsku', "category": "$$current.category"})
        elif collatetype==CollateType.PARENT: curr.update({'value': '$$current.parent'})
        elif collatetype==CollateType.CATEGORY: curr.update({'value': '$$current.category'})
        return {"$set": { "data": { "$reduce": { "input": "$data", "initialValue": [], "in": { "$let": { "vars": { "current": "$$this", "existing": { "$filter": { "input": "$$value", "as": "g", "cond": { "$and": cond } } } }, "in": { "$cond": [ { "$gt": [{ "$size": "$$existing" }, 0] }, { "$map": { "input": "$$value", "as": "g", "in": { "$cond": [ { "$and": cond }, { "$mergeObjects": [ "$$g", { "data": { "$concatArrays": ["$$g.data", ["$$current.data"]] } } ] }, "$$g" ] } } }, { "$concatArrays": [ "$$value", [ curr ] ] } ] } } } } } }}

    def __setIdForDate(self, collatetype: CollateType):
        value = '$value' if collatetype!=CollateType.MARKETPLACE else collatetype.value
        return {"$set": { 'collatetype': collatetype.value, '_id': { '$concat': [ { '$toString': [ '$marketplace' ] }, '_', value, '_', { '$dateToString': { 'date': '$date' , 'format': '%Y-%m-%d' } } ] } }}


    def __mergeToDateAnalytics(self):
        return self.pp.merge(CollectionType.DATE_ANALYTICS)
    
    def __lookupStateAnalytics(self, collatetype: CollateType):
        pipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] }] } } } ]
        return { '$lookup': { 'from': 'state_analytics', 'let': { 'marketplace': '$_id', 'collatetype': collatetype.value, 'date': '$date'}, 'pipeline': pipeline, 'as': 'data' } }

    def __lookupDateAnalytics(self, collatetype: CollateType):
        pipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] } ] } } } ]
        return { '$lookup': { 'from': 'date_analytics', 'let': { 'marketplace': '$_id', 'collatetype': collatetype.value, 'date': '$date', }, 'pipeline': pipeline, 'as': 'data' } }

    def __lookupAds(self):
        return { '$lookup': { 'from': 'adv', 'let': { 'marketplace': '$marketplace', 'assettype': 'Ad', 'date': '$date', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }

    def __lookupAllAds(self):
        return { '$lookup': { 'from': 'adv', 'let': { 'marketplace': '$marketplace', 'assettype': 'Campaign', 'date': '$date'}, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }

    def __lookupTraffic(self):
        return { '$lookup': { 'from': 'traffic', 'let': { 'marketplace': '$marketplace', 'asin': '$value', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$traffic' } } ], 'as': 'traffic' } }

    def __mergeDataWithAdTraffic(self):
        return { '$set': { 'data': { '$mergeObjects': [ '$data', '$ad', '$traffic' ] } } }
    
    def __hideAdTrafficExpenses(self):
        return { '$project': { 'ad': 0, 'traffic': 0 , 'expense': 0} }
    
    def __matchMarketplaceSetAndOpenDates(self):
        return [
            self.__matchmarketplace(),
            self.__setDates(),
            self.__openDates(),
            self.__openDate()
        ]
    
    def __opendata(self):
        return { '$unwind': { 'path': '$data', 'preserveNullAndEmptyArrays': False } }
    
    def __setDataAsRoot(self):
        return { '$replaceRoot': { 'newRoot': '$data' } }
    
    def __addMiscExpense(self):
        return { '$lookup': { 'from': 'settlements', 'let': {'marketplace': '$marketplace', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ { '$ifNull': [ '$orderid', None ] }, None ] }, { '$ne': [ '$amounttype', 'Cost of Advertising' ] } ] } } }, { '$match': { 'amountdescription': { '$not': { '$regex': 'Reserve', '$options': 'i' } } } }, { '$group': { '_id': None, 'expense': { '$sum': '$amount' } } } ], 'as': 'expense' } }


    async def __executeSkuDate(self):
        pipeline = self.__matchMarketplaceSetAndOpenDates()
        pipeline.append(self.__lookupStateAnalytics(CollateType.SKU))
        pipeline.extend([
            self.__setData(CollateType.SKU),
            self.__opendata(),
            self.__setDataAsRoot(),
            self.__collateData(),
            self.__setIdForDate(CollateType.SKU),
            self.__lookupAds(),
            self.__collateData('ad'),
            self.__mergeDataWithAdTraffic(),
            self.__hideAdTrafficExpenses(),
            self.__mergeToDateAnalytics()
        ])
        mongo_pipeline_print.copy_pipeline(pipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)


    async def __executeAsinDate(self):
        pipeline = self.__matchMarketplaceSetAndOpenDates()
        pipeline.append(self.__lookupDateAnalytics(CollateType.SKU))
        pipeline.extend([
            self.__setData(CollateType.ASIN),
            self.__opendata(),
            self.__setDataAsRoot(),
            self.__collateData(),
            self.__setIdForDate(CollateType.ASIN),
            self.__lookupTraffic(),
            self.__collateData('traffic'),
            self.__mergeDataWithAdTraffic(),
            self.__hideAdTrafficExpenses(),
            self.__mergeToDateAnalytics()
        ])
        mongo_pipeline_print.copy_pipeline(pipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)

    async def __executeParentDate(self):
        pipeline = self.__matchMarketplaceSetAndOpenDates()
        pipeline.append(self.__lookupDateAnalytics(CollateType.ASIN))
        pipeline.extend([
            self.__setData(CollateType.PARENT),
            self.__opendata(),
            self.__setDataAsRoot(),
            self.__collateData(),
            self.__setIdForDate(CollateType.PARENT),
            self.__lookupTraffic(),
            self.__collateData('traffic'),
            self.__mergeDataWithAdTraffic(),
            self.__hideAdTrafficExpenses(),
            {"$match": {"_id": {"$ne": None}}},
            {"$project": {"category": 0}},
            self.__mergeToDateAnalytics()
        ])
        mongo_pipeline_print.copy_pipeline(pipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)


    async def __executeCategoryDate(self):
        pipeline = self.__matchMarketplaceSetAndOpenDates()
        pipeline.append(self.__lookupDateAnalytics(CollateType.ASIN))
        pipeline.extend([
            self.__setData(CollateType.CATEGORY),
            self.__opendata(),
            self.__setDataAsRoot(),
            self.__collateData(),
            self.__setIdForDate(CollateType.CATEGORY),
            self.__mergeToDateAnalytics()
        ])
        mongo_pipeline_print.copy_pipeline(pipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)

    async def __executeMarketplaceDate(self):
        pipeline = self.__matchMarketplaceSetAndOpenDates()
        pipeline.append(self.__lookupDateAnalytics(CollateType.ASIN))
        pipeline.extend([
            self.__setData(CollateType.MARKETPLACE),
            self.__opendata(),
            self.__setDataAsRoot(),
            self.__collateData(),
            self.__lookupAllAds(),
            self.__collateData('ad'),
            self.__addMiscExpense(),
            {"$set": {"data.miscexpense": { "$first": "$expense.expense" }}},
            self.__mergeDataWithAdTraffic(),
            self.__hideAdTrafficExpenses(),
            self.__setIdForDate(CollateType.MARKETPLACE),
            {"$match": {"_id": {"$ne": None}}},
            {"$project": {"category": 0, "parentsku": 0}},
            self.__mergeToDateAnalytics()
        ])
        mongo_pipeline_print.copy_pipeline(pipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)

    async def __executeStateAnalytics(self):
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines import CreateStateAnalytics
        statepipeline = CreateStateAnalytics.pipeline(self.client.uid, self.client.marketplaceId, self.dates)
        mongo_pipeline_print.copy_pipeline(statepipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(statepipeline)


    async def execute(self):
        await self.client.db.state_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
        await self.client.db.date_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
        start_time = time.perf_counter()
        await self.__executeStateAnalytics()
        await self.__executeSkuDate()
        await self.__executeAsinDate()
        await self.__executeParentDate()
        await self.__executeCategoryDate()
        await self.__executeMarketplaceDate()
        process_time_seconds = (time.perf_counter() - start_time)  # ms
        print(f"Total Analytics took {process_time_seconds:.4f} seconds")

        

        