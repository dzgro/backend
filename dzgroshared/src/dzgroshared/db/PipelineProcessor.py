from datetime import datetime, timedelta
from typing import Literal, Any
from bson import ObjectId
from dzgroshared.db.date_analytics.pipelines.Get30DaysGraph import pipeline
from dzgroshared.db.model import PyObjectId, SATKey
from dzgroshared.db.enums import Operator, CollectionType
from dzgroshared.Methods import AddCalculations, AddCurrPreGrowth, AddPercentKeys, CollateCurrPreGrowth, CollateSATs, ConvertDataArrayToDataObject, GetAsinQueries, GetCalculatedAnalyticsKeys, OpenSATs, BreakDataToCurrPreByDates, GroupAnalyticKeys, CollateListOfObjectsAsObject, TransformAnalyticsKeys
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class LookUpLetExpression(BaseModel):
    key: str
    value: Any|SkipJsonSchema[None]=None
class LookUpPipelineMatchExpression(LookUpLetExpression):
    operator: Operator = Operator.EQ
    isValueVariable:bool = False

class PipelineProcessor:
    marketplace: ObjectId
    uid: str

    def __init__(self, uid: str|None, marketplace: ObjectId|str|PyObjectId|None = None):
        if(marketplace): self.marketplace = marketplace if isinstance(marketplace, ObjectId) else ObjectId(str(marketplace))
        if(uid): self.uid = uid

    def __getattr__(self, item):
        return None

    def getLetDict(self, others: dict = {}):
        if "_id" in others: return others
        obj: dict = {}
        if self.uid and self.uid not in others.values(): obj.update({'uid': self.uid})
        if self.marketplace and self.marketplace not in others.values(): obj.update({'marketplace': self.marketplace})
        obj.update(**others)
        return obj
    
    def getCollateDataReduceDef(self, datakey: str="data"):
        return { "$reduce": { "input": f"${datakey}", "initialValue": {}, "in": { "$arrayToObject": { "$filter": { "input": { "$map": { "input": { "$setUnion": [ { "$map": { "input": { "$objectToArray": "$$value" }, "as": "v", "in": "$$v.k" } }, { "$map": { "input": { "$objectToArray": "$$this" }, "as": "t", "in": "$$t.k" } } ] }, "as": "key", "in": { "k": "$$key", "v": { "$round": [ { "$add": [ { "$ifNull": [ { "$getField": { "field": "$$key", "input": "$$value" } }, 0 ] }, { "$ifNull": [ { "$getField": { "field": "$$key", "input": "$$this" } }, 0 ] } ] }, 2 ] } } } }, "as": "item", "cond": { "$ne": ["$$item.v", 0] } } } } } }
    
    def collateData(self, datakey: str="data"):
        return {"$set": { f'{datakey}':  self.getCollateDataReduceDef(datakey)}}

    def matchMarketplace(self, others: dict = {}):
        return { '$match': self.getLetDict(others)}
    
    def matchAllEQExpressions(self, keys: list[str]):
        return self.matchAllExpressions(list(map(lambda x: LookUpPipelineMatchExpression(key=x), keys)))

    def getDatesBetweenTwoDates(self, startDate: datetime, endDate: datetime) -> dict:
        return { '$let': { 'vars': { 'startDate': startDate, 'endDate': endDate }, 'in': { '$reduce': { 'input': { '$range': [ 0, { '$sum': [ { '$dateDiff': { 'startDate': '$$startDate', 'endDate': '$$endDate', 'unit': 'day' } }, 1 ] } ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateAdd': { 'startDate': '$$startDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } } } }

    def getNDatesBeforeADate(self, endDate: datetime, days: int) -> dict:
        startDate = endDate - timedelta(days=days)
        return self.getDatesBetweenTwoDates(startDate, endDate)
    
    def openMarketplaceMonths(self):
        pipeline: list[dict] = [{ '$match': { '_id': self.marketplace } }]
        pipeline.extend([ { '$addFields': { 'months': { '$reduce': { 'input': { '$range': [ 0, { '$add': [ { '$multiply': [ { '$subtract': [ { '$year': '$dates.enddate' }, { '$year': '$dates.startdate' } ] }, 12 ] }, { '$subtract': [ { '$month': '$dates.enddate' }, { '$month': '$dates.startdate' } ] }, 1 ] } ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$let': { 'vars': { 'currentMonth': { '$add': [ { '$month': '$dates.startdate' }, '$$this' ] }, 'currentYear': { '$add': [ { '$year': '$dates.startdate' }, { '$floor': { '$divide': [ { '$add': [ { '$month': '$dates.startdate' }, '$$this', -1 ] }, 12 ] } } ] } }, 'in': { '$let': { 'vars': { 'adjustedMonth': { '$cond': [ { '$gt': [ '$$currentMonth', 12 ] }, { '$subtract': [ '$$currentMonth', 12 ] }, '$$currentMonth' ] }, 'adjustedYear': { '$cond': [ { '$gt': [ '$$currentMonth', 12 ] }, { '$add': [ '$$currentYear', 1 ] }, '$$currentYear' ] } }, 'in': { '$let': { 'vars': { 'firstDayOfMonth': { '$dateFromParts': { 'year': '$$adjustedYear', 'month': '$$adjustedMonth', 'day': 1 } }, 'lastDayOfMonth': { '$dateSubtract': { 'startDate': { '$dateAdd': { 'startDate': { '$dateFromParts': { 'year': '$$adjustedYear', 'month': '$$adjustedMonth', 'day': 1 } }, 'unit': 'month', 'amount': 1 } }, 'unit': 'day', 'amount': 1 } } }, 'in': { '$let': { 'vars': { 'rangeStart': { '$max': [ '$$firstDayOfMonth', '$dates.startdate' ] }, 'rangeEnd': { '$min': [ '$$lastDayOfMonth', '$dates.enddate' ] } }, 'in': { 'month': { '$dateToString': { 'format': '%b %Y', 'date': '$$firstDayOfMonth' } }, 'period': { '$concat': [ { '$dateToString': { 'format': '%d %b', 'date': '$$rangeStart' } }, ' - ', { '$dateToString': { 'format': '%d %b', 'date': '$$rangeEnd' } } ] }, 'startdate': '$$rangeStart', 'enddate': '$$rangeEnd' } } } } } } } } } ] ] } } } } }, { '$unwind': "$months" }, { '$sort': { "months.startdate": -1 } }])
        return pipeline

    def matchAllExpressions(self, expressions: list[LookUpPipelineMatchExpression]):
        expr: list[dict] = []
        if self.uid: expr.append({"$eq": ["$uid",self.uid]})
        if self.marketplace: expr.append({"$eq": ["$marketplace",self.marketplace]})
        for e in expressions: 
            val = f'$${e.key}' if not e.value else e.value if not e.isValueVariable else f'$${e.value}'
            if e.operator==Operator.NOTIN: expr.append({"$not": {'$in': [f'${e.key}', val]}})
            else: expr.append({f'${e.operator.name.lower()}': [f'${e.key}', val]})
        return {"$match": {"$expr": {"$and": expr}}}
    
    def match(self, data: dict):
        if len(list(data.keys()))==0: raise ValueError("Match Dict cannot be empty")
        return { '$match': data}
    
    def lookup(self, collection: CollectionType, dataKey: str, pipeline: list[dict] = [], letExpressions: list[LookUpLetExpression]|None=None, localField: str|None=None, foreignField: str|None=None, letkeys: list[str]|None=None):
        if letkeys: letExpressions = list(map(lambda x: LookUpLetExpression(key=x), letkeys))
        if letExpressions: 
            letDict = {"uid": "$uid", "marketplace": "$marketplace", **{x.key: x.value or f'${x.key}' for x in letExpressions}}
            return { '$lookup': { 'from': collection.value, 'let': letDict, 'pipeline': pipeline, 'as': dataKey } }
        if None not in [localField, foreignField]: return { '$lookup': { 'from': collection.value, 'localField': localField, 'foreignField': foreignField,'pipeline': pipeline,  'as': dataKey } }
        return { '$lookup': { 'from': collection.value, 'pipeline': pipeline, 'as': dataKey } }
    

    def unwind(self, key: str):
        return {"$unwind": f'${key}' if not key.startswith('$') else key}

    def unset(self, keys: list[str]):
        return {"$unset": keys}

    def unsetField(self, root:dict|str, key: str):
        return {"$unsetField": {"input": root, "field":key}}
    
    def getSatCollation(self):
        return CollateSATs.execute()
    
    def collateSATs(self):
        field = self.unsetField(self.unsetField(self.unsetField("$$ROOT", "sales"),"ad"),"traffic")
        return self.replaceRoot(self.mergeObjects([field, self.getSatCollation()]))
    
    def mergeObjects(self, objects: list[dict|str]):
        return {"$mergeObjects": objects}
    
    def first(self, key:str):
        return {"$first": f'${key}' if not key.startswith('$') else key}

    def setCondtion(self, condition: bool|dict, ifTrue: Any, ifFalse: Any):
        return {"$cond": [condition, ifTrue, ifFalse]}
    
    def groupForSAT(self, key: SATKey, isAsin: bool = False):
        if not isAsin: return { '$group': { '_id': { 'marketplace': '$marketplace', 'date': '$date' }, key: { '$push': f'${key}' } } }
        return { '$group': { '_id': { 'marketplace': '$marketplace', 'date': '$date', "asin": "$asin" }, key: { '$push': f'${key}' } } }
    
    def openId(self):
        return self.replaceRoot(self.mergeObjects([ { "$unsetField": { "input": "$$ROOT", "field": "_id" } }, "$_id" ]))

    def replaceRoot(self, data: dict|str):
        return { '$replaceRoot': { 'newRoot': data}}

    def group(self, id: list[LookUpLetExpression]|str|None=None, groupings: dict={}, letkeys: list[str]|None=None):
        letDict: dict|str|None
        if letkeys: id = list(map(lambda x: LookUpLetExpression(key=x), letkeys))
        if not id: letDict = None
        elif isinstance(id,str): letDict=id
        else: letDict = self.getLetDict({x.key: x.value or f'${x.key}' for x in id})
        groupDict = {"_id": letDict, **groupings}
        return { '$group': groupDict}


    def replaceWith(self, data: dict|str):
        return {"$replaceWith": data}
    
    def setUidMarketplace(self):
        return self.set(self.getLetDict())
    
    def merge(self, collection: CollectionType, whenMatched: Literal["replace","merge","keepExisting","fail"]|None=None, whenNotMatched:  Literal["insert","discard","fail"]|None=None):
        mergeDict = {"into": collection.value}
        if whenMatched: mergeDict.update({"whenMatched": whenMatched})
        if whenNotMatched: mergeDict.update({"whenNotMatched": whenNotMatched})
        return {"$merge": mergeDict}
    
    def convertIntToDouble(self):
        return self.replaceRoot({ '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$ROOT' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': [ { '$eq': [ { '$type': '$$this.v' }, 'int' ] }, { '$toDouble': '$$this.v' }, '$$this.v' ] } } ] ] } } } })
    
    def sort(self, data: dict[str,Literal[1,-1]]):
        return {"$sort": data}
    
    def set(self, data: dict):
        return {"$set": data}
    
    def project(self, show: list[str]=[], hide:list[str]=[],obj: dict|None=None):
        if obj is not None: return {"$project": obj}
        projection = {k: 1 for k in show}
        projection.update({k: 0 for k in hide})
        return {"$project": projection}
    
    def limit(self, limit: int):
        return {"$limit": limit}
    
    def skip(self, skip: int):
        return {"$skip": skip}
    
    def openSATs(self, objectKey: str|None=None):
        return OpenSATs.open(objectKey)
    
    def convertDataArrayToDataObject(self):
        return self.set(ConvertDataArrayToDataObject.execute())
    
    def getCalculatedKeys(self):
        return GetCalculatedAnalyticsKeys.execute()
    
    def addCalculations(self, currPreGrowth: bool, objectKey: str = "data"):
        return AddCalculations.execute(currPreGrowth, objectKey)
    
    def addCurrPreGrowth(self, objectKey: str = "data"):
        return AddCurrPreGrowth.execute(objectKey)
    
    def collateCurrPreGrowth(self, objectKey: str = "data"):
        return CollateCurrPreGrowth.collate(objectKey)
    
    def addProduct(self):
        innerPipeline = [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$project': { 'title': 1, 'imageUrl': 1, 'productType': 1, 'asin': 1, 'variationDetails': 1, 'variationTheme': 1, '_id': 0 } } ]
        pipeline = [self.lookup(CollectionType.PRODUCTS, 'product', innerPipeline, [LookUpLetExpression(key='asin')])]
        pipeline.append(self.set({ 'product': { '$first': '$product' } }))
        return pipeline
    
    def breakDataToCurrPre(self, objectKey:str = "data", datesKey: str="dates"):
        return BreakDataToCurrPreByDates.execute(objectKey, datesKey)
    
    def getAsinQueries(self):
        return GetAsinQueries.getAsinQueries(self.marketplace)
    
    
    def addPercentKeys(self):
        return AddPercentKeys.execute(False)
    
    def groupAnalyticKeys(self):
        return GroupAnalyticKeys.execute()
    
    def collateListOfObjectsAsObject(self, key: str, dataKey:str|None=None):
        return self.set({key: CollateListOfObjectsAsObject.execute(dataKey or key)})
    
    def removeDataTypesFromObject(self, key: str, removeTypes: list[Literal['array','object','str','int','float']] = []):
        return { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': f'${key}' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { "$let": { "vars": { "objType": { '$type': '$$this.v' } }, "in": { '$cond': [ { '$not': { "$in": ["$$objType", removeTypes] } }, [ '$$this' ], [] ] } } } ] } } } }
    
    def roundAllDouble(self, decimalplaces:int=2):
        return self.replaceRoot({ "$arrayToObject": { "$reduce": { "input": {"$objectToArray": "$$ROOT"}, "initialValue": [], "in": { "$concatArrays": [ "$$value", [ { "k": "$$this.k", "v": { "$cond": { "if": { "$eq": [ {"$type": "$$this.v"}, "double" ] }, "then": {"$round": ["$$this.v",decimalplaces]}, "else": "$$this.v" } } } ] ] } } } })

    def mergeAllObjectsInObjectToObject(self, key: str):
        return { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': f'${key}' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$eq': [ { '$type': '$$this.v' }, 'object' ] }, { '$objectToArray': '$$this.v' }, [] ] } ] } } } }
    
    def getAdColumns(self):
        return [{ '$lookup': { 'from': 'analytics_calculation', 'pipeline': [ { '$match': { '$expr': { '$eq': [ '$value', 'ad' ] } } }, { '$replaceWith': { 'items': '$items' } }, { '$unwind': '$items' }, { '$replaceWith': '$items' }, { '$project': { 'querygroup': 0 } } ], 'as': 'columns' } }, { '$set': { 'columns': { '$reduce': { 'input': '$columns', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$let': { 'vars': { 'val': { '$replaceOne': { 'input': '$$this.label', 'find': 'Ad ', 'replacement': '' } }, 'leftparenthesesPos': { '$indexOfBytes': [ '$$this.label', '(' ] }, 'rightparenthesesPos': { '$indexOfBytes': [ '$$this.label', ')' ] } }, 'in': [ { '$mergeObjects': [ '$$this', { 'label': { '$cond': [ { '$eq': [ '$$leftparenthesesPos', -1 ] }, '$$val', { '$substr': [ '$$val', { '$sum': [ '$$leftparenthesesPos', 1 ] }, { '$subtract': [ { '$subtract': [ '$$rightparenthesesPos', '$$leftparenthesesPos' ] }, 1 ] } ] } ] } } ] } ] } } ] } } } } }]
        
