
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.models.enums import CollectionType
class Datatransformer:
    pp: PipelineProcessor
    datakey: str
    
    def __init__(self, pp: PipelineProcessor, datakey: str = 'data'):
        self.pp = pp
        self.datakey = datakey

    
    def collateData(self):
        return self.pp.set({ f'{self.datakey}': { "$reduce": { "input": f"${self.datakey}", "initialValue": {}, "in": { "$arrayToObject": { "$filter": { "input": { "$map": { "input": { "$setUnion": [ { "$map": { "input": { "$objectToArray": "$$value" }, "as": "v", "in": "$$v.k" } }, { "$map": { "input": { "$objectToArray": "$$this" }, "as": "t", "in": "$$t.k" } } ] }, "as": "key", "in": { "k": "$$key", "v": { "$round": [ { "$add": [ { "$ifNull": [ { "$getField": { "field": "$$key", "input": "$$value" } }, 0 ] }, { "$ifNull": [ { "$getField": { "field": "$$key", "input": "$$this" } }, 0 ] } ] }, 2 ] } } } }, "as": "item", "cond": { "$ne": ["$$item.v", 0] } } } } } } })

    def addPercentKeys(self):
        return self.pp.set({ 'percentkeys': { '$reduce': { 'input': '$keys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$eq': [ { '$ifNull': [ '$$this.ispercent', False ] }, True ] }, [ '$$this.value' ], [] ] } ] } } } })

    def addAnalyticKeys(self):
        groupStage = self.pp.group(None, {'keys': { '$push': { '$unsetField': { 'input': '$$ROOT', 'field': '_id' } } }})
        setMoreKeys = { '$reduce': { 'input': '$keys', 'initialValue': { 'allkeys': [], 'projectkeys': [], 'percentkeys': [], 'calculatedkeys': [],'reversegrowthkeys':[], 'querykeys':[] }, 'in': { '$mergeObjects': [ '$$value', { '$reduce': { 'input': '$$this.items', 'initialValue': '$$value', 'in': { '$mergeObjects': [ '$$value', { 'allkeys': { '$concatArrays': [ '$$value.allkeys', [ '$$this' ] ] } }, { 'projectkeys': { '$cond': [ { '$eq': [ { '$ifNull': [ '$$this.project', True ] }, True ] }, { '$concatArrays': [ '$$value.projectkeys', [ '$$this.value' ] ] }, '$$value.projectkeys' ] } },{ 'querykeys': { '$cond': [ { '$ne': [ {"$strLenCP": { '$ifNull': [ '$$this.querygroup', '' ] }}, 0 ] }, { '$concatArrays': [ '$$value.querykeys', [ '$$this.value' ] ] }, '$$value.querykeys' ] } },{ 'reversegrowthkeys': { '$cond': [ { '$eq': [ { '$ifNull': [ '$$this.reversegrowth', False ] }, True ] }, { '$concatArrays': [ '$$value.reversegrowthkeys', [ '$$this.value' ] ] }, '$$value.reversegrowthkeys' ] } }, { 'percentkeys': { '$cond': [ { '$eq': [ { '$ifNull': [ '$$this.ispercent', False ] }, True ] }, { '$concatArrays': [ '$$value.percentkeys', [ '$$this.value' ] ] }, '$$value.percentkeys' ] } }, { 'calculatedkeys': { '$cond': [ { '$ne': [ { '$ifNull': [ '$$this.subkeys', None ] }, None ] }, { '$concatArrays': [ '$$value.calculatedkeys', [ '$$this.value' ] ] }, '$$value.calculatedkeys' ] } } ] } } } ] } } }
        lookupPipeline = [self.pp.sort({'index':1}), groupStage, self.pp.replaceRoot(self.pp.mergeObjects([{"keys":"$keys"}, setMoreKeys]))]
        lookupstage = self.pp.lookup(CollectionType.ANALYTICS_CALCULATION,'keys', lookupPipeline)
        return [lookupstage, self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", self.pp.first("keys")]))]
    
    def addMissingKeys(self):
        return self.pp.set({"data": { '$reduce': { 'input': '$allkeys', 'initialValue': '$data', 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$this.value', 'v': { '$ifNull': [ { '$getField': { 'input': '$data', 'field': '$$this.value' } }, 0 ] } } ] ] } ] } } }})
    
    def addCalculatedKeysToData(self):
        return self.pp.set({self.datakey: { '$reduce': { 'input': '$allkeys', 'initialValue': f'${self.datakey}', 'in': { '$cond': [ { '$not': { '$in': [ '$$this.value', '$calculatedkeys' ] } }, '$$value', { '$mergeObjects': [ '$$value', { '$let': { 'vars': { 'key': '$$this', 'val': '$$value', 'num': { '$getField': { 'input': '$$value', 'field': { '$arrayElemAt': [ '$$this.subkeys', 0 ] } } }, 'denom': { '$getField': { 'input': '$$value', 'field': { '$arrayElemAt': [ '$$this.subkeys', 1 ] } } } }, 'in': { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$$num', None ] }, None ] }, { '$ne': [ { '$ifNull': [ '$$denom', None ] }, None ] } ] }, { '$arrayToObject': [ [ { 'k': '$$key.value', 'v': { '$let': { 'vars': { 'isPercent': '$$key.isPercent', 'isDivide': { '$eq': [ '$$key.operation', 'divide' ] }, 'isAdd': { '$eq': [ '$$key.operation', 'add' ] }, 'isSubtract': { '$eq': [ '$$key.operation', 'subtract' ] } }, 'in': { '$cond': [ '$$isAdd', { '$sum': [ '$$num', '$$denom' ] }, { '$cond': [ '$$isSubtract', { '$subtract': [ '$$num', '$$denom' ] }, { '$cond': [ { '$eq': [ '$$denom', 0 ] }, 0, { '$multiply': [ { '$divide': [ '$$num', '$$denom' ] }, { '$cond': [ '$$isPercent', 100, 1 ] } ] } ] } ] } ] } } } } ] ] }, {} ] } } } ] } ] } } }})
    
    def addValueAndRawValue(self):
        return self.pp.set({self.datakey: { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': f'${self.datakey}' }, 'initialValue': [], 'in': { '$let': { 'vars': { 'val': '$$this.v' }, 'in': { '$let': { 'vars': { 'ispercent': { '$in': [ '$$this.k', '$percentkeys' ] } }, 'in': { '$let': { 'vars': { 'calculatedVal': self.getCalculatedValue('val') }, 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': [ '$$ispercent', { 'rawvalue': { '$round': [ { '$multiply': [ '$$val', 100 ] }, 3 ] }, 'value': { '$concat': [ { '$toString': { '$round': [ { '$multiply': [ '$$val', 100 ] }, 1 ] } }, '%' ] } }, { 'rawvalue': { '$round': [ '$$val', 2 ] }, 'value': { '$ifNull': [ '$$calculatedVal', { '$toString': { '$round': [ '$$val', 2 ] } } ] } } ] } } ] ] } } } } } } } } } }})
    
    def addValue(self):
        return self.pp.set({self.datakey: { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': f'${self.datakey}' }, 'initialValue': [], 'in': { '$let': { 'vars': { 'val': '$$this.v', 'ispercent': { '$in': [ '$$this.k', '$percentkeys' ] } }, 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': [ '$$ispercent', { '$round': [ { '$multiply': [ '$$val', 100 ] }, 2 ] }, { '$round': [ '$$val', 2 ] } ] } } ] ] } } } } } } })

    def convertValuesToString(self):
        return self.pp.set({self.datakey: { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': f'${self.datakey}' }, 'initialValue': [], 'in': { '$let': { 'vars': { 'val': '$$this.v' }, 'in': { '$let': { 'vars': { 'ispercent': { '$in': [ '$$this.k', '$percentkeys' ] } }, 'in': { '$let': { 'vars': { 'calculatedVal': self.getCalculatedValue('val') }, 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': [ '$$ispercent', { '$concat': [ { '$toString': { '$round': [ { '$multiply': [ '$$val', 100 ] }, 1 ] } }, '%' ] } , { '$ifNull': [ '$$calculatedVal', { '$toString': { '$round': [ '$$val', 2 ] } } ] } ] } } ] ] } } } } } } } } } }})
    
    def groupData(self):
        return self.pp.set({self.datakey: { '$reduce': { 'input': '$keys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'label': '$$this.label', 'items': { '$reduce': { 'input': '$$this.items', 'initialValue': [], 'in': { '$cond': [ { '$in': [ '$$this.value', '$projectkeys' ] }, { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ { 'label': '$$this.label','key': '$$this.value', 'value': { '$getField': { 'input': f'${self.datakey}', 'field': '$$this.value' } } } ] } ] ] }, '$$value' ] } } } } ] ] } } }})
    
    def hideKeys(self):
        return self.pp.project([], ['keys','allkeys','projectkeys','percentkeys','calculatedkeys','reversegrowthkeys','querykeys'])
    
    def addGrowth(self):
        setCurrPreValue = self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", { '$let': { 'vars': { 'cIdx': { '$indexOfArray': [ '$tag', 'curr' ] } }, 'in': { '$let': { 'vars': { 'pIdx': { '$cond': [ { '$eq': [ '$$cIdx', 0 ] }, 1, 0 ] } }, 'in': { 'cIdx': '$$cIdx', 'pIdx': '$$pIdx', 'curr': { '$cond': [ { '$in': [ '$$cIdx', [ 0, 1 ] ] }, { '$arrayElemAt': [ '$data', '$$cIdx' ] }, None ] }, 'pre': { '$cond': [ { '$in': [ '$$pIdx', [ 0, 1 ] ] }, { '$arrayElemAt': [ '$data', '$$pIdx' ] }, None ] } } } } } }]))
        setData = self.pp.set({self.datakey: { '$arrayToObject': { '$reduce': { 'input': '$allkeys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$in': [ '$$this.value', '$querykeys' ] }, { '$let': { 'vars': { 'data': { '$let': { 'vars': { 'ck': { '$getField': { 'input': '$curr', 'field': '$$this.value' } }, 'pk': { '$getField': { 'input': '$pre', 'field': '$$this.value' } } }, 'in': { '$cond': [ { '$and': [ { '$eq': [ { '$ifNull': [ '$$ck', None ] }, None ] }, { '$eq': [ { '$ifNull': [ '$$pk', None ] }, None ] } ] }, [], { '$concatArrays': [ { '$cond': [ { '$eq': [ { '$ifNull': [ '$$ck', None ] }, None ] }, [], [ { 'k': 'curr', 'v': { '$round': [ { '$ifNull': [ '$$ck', 0 ] }, 2 ] } } ] ] }, { '$cond': [ { '$eq': [ { '$ifNull': [ '$$pk', None ] }, None ] }, [], [ { 'k': 'pre', 'v': { '$round': [ { '$ifNull': [ '$$pk', 0 ] }, 2 ] } } ] ] }, { '$cond': [ { '$or': [ { '$eq': [ { '$ifNull': [ '$$ck', 0 ] }, 0 ] }, { '$eq': [ { '$ifNull': [ '$$pk', 0 ] }, 0 ] } ] }, [], [ { 'k': 'growth', 'v': { '$cond': [ { '$in': [ '$$this.value', '$percentkeys' ] }, { '$round': [ { '$subtract': [ '$$ck', '$$pk' ] }, 2 ] }, { '$round': [ { '$multiply': [ {'$subtract': [{ '$divide': [ '$$ck', '$$pk' ] },1]}, 100 ] }, 2 ] } ] } }, { 'k': 'growing', 'v': { '$gt': [ '$$ck', '$$pk' ] } } ] ] } ] } ] } } } }, 'in': { '$cond': [ { '$eq': [ { '$size': '$$data' }, 0 ] }, [], [ { 'k': '$$this.value', 'v': { '$arrayToObject': '$$data' } } ] ] } } }, [] ] } ] } } } } })
        return [setCurrPreValue, setData]
    
    def getCalculatedValue(self, key: str, returnValue: bool=False):
        return { '$ifNull': [ { '$reduce': { 'input': [ { 'val': 10000000, 'key': 'Cr' }, { 'val': 100000, 'key': 'Lacs' }, { 'val': 1000, 'key': 'K' } ], 'initialValue': None, 'in': { '$cond': [ { '$and': [ { '$eq': [ '$$value', None ] }, { '$gte': [ f'$${key}', '$$this.val' ] } ] }, { '$concat': [ { '$toString': { '$round': [ { '$divide': [ f'$${key}', '$$this.val' ] }, 2 ] } }, ' ', '$$this.key' ] }, '$$value' ] } } }, {"$round": [f"$${key}",1]} if returnValue else None ] }
    
    def convertCurrPreToString(self, key: str|None=None):
        return { '$set': { self.datakey: { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': f'${self.datakey}' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': { 'if': { '$cond': [ { '$eq': [ key, None ] }, False, { '$ne': [ '$$this.k', key ] } ] }, 'then': [], 'else': [ { 'k': '$$this.k', 'v': { '$let': { 'vars': { 'ispercent': { '$in': [ '$$this.k', '$percentkeys' ] } }, 'in': { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$this.v' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': { 'if': { '$in': [ '$$this.k', [ 'curr', 'pre' ] ] }, 'then': { '$let': { 'vars': { 'val': { '$ifNull': [ '$$this.v', 0 ] } }, 'in': { '$ifNull': [ { '$reduce': { 'input': [ { 'val': 10000000, 'key': 'Cr' }, { 'val': 100000, 'key': 'Lacs' }, { 'val': 1000, 'key': 'K' } ], 'initialValue': None, 'in': { '$cond': [ { '$and': [ { '$eq': [ '$$value', None ] }, { '$gte': [ '$$val', '$$this.val' ] } ] }, { '$concat': [ { '$toString': { '$round': [ { '$divide': [ '$$val', '$$this.val' ] }, 2 ] } }, ' ', '$$this.key' ] }, '$$value' ] } } }, { '$concat': [ { '$toString': { '$round': [ { '$multiply': [ '$$val', { '$cond': [ '$$ispercent', 100, 1 ] } ] }, { '$cond': [ '$$ispercent', 2, 1 ] } ] } }, { '$cond': { 'if': '$$ispercent', 'then': '%', 'else': '' } } ] } ] } } }, 'else': { '$cond': { 'if': { '$eq': [ '$$this.k', 'growth' ] }, 'then': { '$concat': [ { '$toString': { '$multiply': [ { '$round': [ { '$ifNull': [ '$$this.v', 0 ] }, { '$cond': [ '$$ispercent', 2, 1 ] } ] }, { '$cond': [ '$$ispercent', 100, 1 ] } ] } }, { '$cond': { 'if': '$$ispercent', 'then': '', 'else': '%' } } ] }, 'else': '$$this.v' } } } } } ] ] } } } } } } } ] } } ] } } } } } }
    
    def convertDataForPerformanceAsQueryGroup(self):
        setkeys = self.pp.set({"keys": { '$sortArray': { 'input': { '$reduce': { 'input': { '$reduce': { 'input': '$keys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', '$$this.items' ] } } }, 'initialValue': [], 'in': { '$cond': [ { '$eq': [ { '$ifNull': [ '$$this.querygroup', None ] }, None ] }, '$$value', { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.label', '$$this.querygroup' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ { 'label': '$$this.querygroup', 'items': [ '$$this' ] } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.label', '$$this.querygroup' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'items': { '$concatArrays': [ '$$v.items', [ '$$this' ] ] } } ] } ] } } } ] } ] } } }, 'sortBy': { 'label': -1 } }}})
        setData = self.pp.set({"data": { '$reduce': { 'input': '$keys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'label': '$$this.label', 'items': { '$reduce': { 'input': '$$this.items', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'label': '$$this.label', 'data': { '$getField': { 'input': '$data', 'field': '$$this.value' } } } ] ] } } } } ] ] } } } })
        return [setkeys, setData]
    
    def addAbsentAdKeys(self): return self.pp.set({ 'ad': { '$let': { 'vars': { 'keys': { '$reduce': { 'input': '$keys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$eq': [ '$$this.value', 'ad' ] }, '$$this.items', [] ] } ] } } } }, 'in': { '$reduce': { 'input': '$$keys', 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$this.value', 'v': { '$round': [ { '$multiply': [ { '$ifNull': [ { '$getField': { 'input': '$ad', 'field': '$$this.value' } }, 0 ] }, { '$cond': [ { '$in': [ '$$this.value', '$percentkeys' ] }, 100, 1 ] } ] }, 2 ] } } ] ] } ] } } } } } })
    
    def transformDataForAllKeys(self):
        pipeline: list[dict] = [self.collateData()]
        pipeline.extend(self.addAnalyticKeys())
        pipeline.append(self.addMissingKeys())
        pipeline.extend([self.addCalculatedKeysToData(), self.addValueAndRawValue()])
        return pipeline
    
    def groupDataAsKeysGroup(self):
        pipeline = self.transformDataForAllKeys()
        pipeline.extend([self.groupData(), self.hideKeys()])
        return pipeline
    
    def transformDataForQuery(self):
        pipeline: list[dict] = [self.collateData()]
        pipeline.extend(self.addAnalyticKeys())
        pipeline.append(self.addCalculatedKeysToData())
        return pipeline
    
    def transformDataForAdRule(self):
        pipeline: list[dict] = [self.collateData()]
        pipeline.extend(self.addAnalyticKeys())
        pipeline.append(self.addCalculatedKeysToData())
        return pipeline
    
    def getQueryResultForTable(self, key: str):
        pipeline = self.addAnalyticKeys()
        pipeline.append(self.convertCurrPreToString(key))
        return pipeline
        
    def convertResultsForPerformance(self):
        pipeline = self.addAnalyticKeys()
        pipeline.append(self.convertCurrPreToString())
        pipeline.extend(self.convertDataForPerformanceAsQueryGroup())
        pipeline.append(self.hideKeys())
        return pipeline
        
    def transformDataForAdRuleResult(self):
        pipeline: list[dict] = [self.collateData()]
        pipeline.extend(self.addAnalyticKeys())
        pipeline.append(self.addAbsentAdKeys())
        pipeline.append(self.addCalculatedKeysToData())
        pipeline.append(self.addValueAndRawValue())
        pipeline.append(self.hideKeys())
        return pipeline

