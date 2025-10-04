from datetime import datetime
import time
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import ENVIRONMENT, CollateType, CollectionType
from dzgroshared.db.model import LambdaContext, StartEndDate
from dzgroshared.utils import date_util, mongo_pipeline_print

class AnalyticsProcessor:

    client: DzgroSharedClient
    pp: PipelineProcessor
    dates: StartEndDate
    marketplacedates: StartEndDate|None
    allDates: list[datetime] = []

    def __init__(self, client: DzgroSharedClient, dates: StartEndDate, marketplacedates: StartEndDate|None=None) -> None:
        self.client = client
        self.dates = dates
        self.marketplacedates = marketplacedates
        self.pp = PipelineProcessor(self.client.uid, self.client.marketplaceId)

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
        return self.pp.collateData(key)
    
    def __setData(self, collatetype:CollateType):
        curr = { "marketplace": "$$current.marketplace", "date": "$$current.date", "data": ["$$current.data"] }
        cond = [ { "$eq": ["$$g.value", f"$$this.{collatetype.value}"] }] if collatetype!=CollateType.MARKETPLACE else True
        if collatetype==CollateType.SKU: 
            curr.update({'value': '$$current.value','asin': '$$current.asin', "parentsku": "$$current.parentsku", "category": "$$current.category"})
            cond = [{ "$eq": ["$$g.value", "$$this.value"] }]
        elif collatetype==CollateType.ASIN: curr.update({'value': '$$current.asin','parentsku': '$$current.parentsku', "category": "$$current.category"})
        elif collatetype==CollateType.PARENT: curr.update({'value': '$$current.parentsku'})
        elif collatetype==CollateType.CATEGORY: curr.update({'value': '$$current.category'})
        return {"$set": { "data": { "$reduce": { "input": "$data", "initialValue": [], "in": { "$let": { "vars": { "current": "$$this", "existing": { "$filter": { "input": "$$value", "as": "g", "cond": { "$and": cond } } } }, "in": { "$cond": [ { "$gt": [{ "$size": "$$existing" }, 0] }, { "$map": { "input": "$$value", "as": "g", "in": { "$cond": [ { "$and": cond }, { "$mergeObjects": [ "$$g", { "data": { "$concatArrays": ["$$g.data", ["$$current.data"]] } } ] }, "$$g" ] } } }, { "$concatArrays": [ "$$value", [ curr ] ] } ] } } } } } }}

    def __setIdForDate(self, collatetype: CollateType):
        return {"$set": { 'collatetype': collatetype.value }}
        value = '$value' if collatetype!=CollateType.MARKETPLACE else collatetype.value
        return {"$set": { 'collatetype': collatetype.value, '_id': { '$concat': [ { '$toString': [ '$marketplace' ] }, '_', value, '_', { '$dateToString': { 'date': '$date' , 'format': '%Y-%m-%d' } } ] } }}


    def __mergeToDateAnalytics(self):
        return self.pp.merge(CollectionType.DATE_ANALYTICS)
    
    def __lookupStateAnalytics(self, collatetype: CollateType):
        pipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] }] } } } ]
        return { '$lookup': { 'from': CollectionType.STATE_ANALYTICS.value, 'let': { 'marketplace': '$_id', 'collatetype': collatetype.value, 'date': '$date'}, 'pipeline': pipeline, 'as': 'data' } }

    def __lookupDateAnalytics(self, collatetype: CollateType):
        pipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] } ] } } } ]
        return { '$lookup': { 'from': CollectionType.DATE_ANALYTICS.value, 'let': { 'marketplace': '$_id', 'collatetype': collatetype.value, 'date': '$date', }, 'pipeline': pipeline, 'as': 'data' } }

    def __lookupAds(self):
        return { '$lookup': { 'from': CollectionType.ADV_PERFORMANCE.value, 'let': { 'marketplace': '$marketplace', 'assettype': 'Ad', 'date': '$date', 'sku': '$value' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$sku', '$$sku' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }

    def __lookupAllAds(self):
        return { '$lookup': { 'from': CollectionType.ADV_PERFORMANCE.value, 'let': { 'marketplace': '$marketplace', 'assettype': 'Campaign', 'date': '$date'}, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$date', '$$date' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$ad' } } ], 'as': 'ad' } }

    def __lookupTraffic(self):
        return { '$lookup': { 'from': CollectionType.TRAFFIC.value, 'let': { 'marketplace': '$marketplace', 'asin': '$value', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$replaceRoot': { 'newRoot': '$traffic' } } ], 'as': 'traffic' } }

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
        return { '$lookup': { 'from': CollectionType.SETTLEMENTS.value, 'let': {'marketplace': '$marketplace', 'date': '$date' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$date', '$$date' ] }, { '$ne': [ '$amounttype', 'Cost of Advertising' ] }, { '$eq': [ { '$ifNull': [ '$orderid', None ] }, None ] } ] } } }, { '$match': { 'amountdescription': { '$not': { '$regex': 'Reserve', '$options': 'i' } } } }, { '$group': { '_id': None, 'expense': { '$sum': '$amount' } } } ], 'as': 'expense' } }


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
        
        await self.client.db.marketplaces.db.aggregate(pipeline)


    async def __executeAsinDate(self):
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines import CreateAsinDateAnalytics
        pipeline = CreateAsinDateAnalytics.pipeline(self.client.marketplaceId, self.dates)
        await self.client.db.marketplaces.db.aggregate(pipeline)

    async def __executeOtherDate(self):
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines import CreateOtherDateAnalytics
        pipeline = CreateOtherDateAnalytics.pipeline(self.client.marketplaceId, self.dates)
        await self.client.db.marketplaces.db.aggregate(pipeline)

    async def __executeMarketplaceDate(self):
        pipeline = [{ '$match': { 'marketplace': self.client.marketplaceId, 'collatetype': 'marketplace' } }]
        pipeline.extend([
            self.__addMiscExpense(),
            {"$set": {"data.miscexpense": { "$first": "$expense.expense" }}},
            {"$project": {"data": 1}},
            self.__mergeToDateAnalytics()
        ])
        await self.client.db.marketplaces.db.aggregate(pipeline)

    async def __executeStateAnalytics(self):
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines import CreateStateAnalytics
        statepipeline = CreateStateAnalytics.freshPipeline(self.client.marketplaceId, self.dates)
        await self.client.db.marketplaces.db.aggregate(statepipeline)

    async def __updatePrevious(self, dates: StartEndDate):
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines import CreateStateAnalytics
        statepipeline = CreateStateAnalytics.refreshPreviousStateAnalytics(self.client.marketplaceId, dates)
        await self.client.db.marketplaces.db.aggregate(statepipeline)



    async def execute(self):
        start_time = time.perf_counter()
        await self.client.db.date_analytics.db.deleteMany({})
        if self.marketplacedates:
            await self.client.db.state_analytics.db.deleteMany({"date": {"$gte": self.dates.startdate}})
            await self.client.db.state_analytics.db.deleteMany({"collatetype": {"$in": [CollateType.ASIN.value, CollateType.PARENT.value, CollateType.CATEGORY.value, CollateType.MARKETPLACE.value]}})
            await self.__updatePrevious(self.marketplacedates)
        else:
            await self.client.db.state_analytics.db.deleteMany({})
        await self.__executeStateAnalytics()
        await self.__executeSkuDate()
        await self.__executeAsinDate()
        await self.__executeOtherDate()
        await self.__executeMarketplaceDate()
        process_time_seconds = (time.perf_counter() - start_time)  # ms
        print(f"Total Analytics took {process_time_seconds:.4f} seconds")

        

        