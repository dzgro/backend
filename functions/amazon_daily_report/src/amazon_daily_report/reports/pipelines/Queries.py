from app.HelperModules.Utils.enums import CollateType
from app.HelperModules.Pipelines.Marketplace.PipelineProcessor import LookUpLetExpression, LookUpPipelineMatchExpression, PipelineProcessor
from app.HelperModules.Pipelines.Marketplace.Pipelines.DataTransformer import Datatransformer
from app.HelperModules.Db.models import CollectionType


class QueryProcessor:
    pp: PipelineProcessor

    def __init__(self, pp: PipelineProcessor):
        self.pp = pp

    def execute(self):
        collateTypes=list(CollateType)
        pipeline: list[dict] = []
        queries = self.getAllQueryIds()
        total = len(queries)*len(collateTypes)
        i=0
        for query in queries:
            for collateType in collateTypes:
                pipeline = self.pipeline(query['queryId'], collateType)
                self.pp.execute(CollectionType.DASHBOARD, pipeline)
                i+=1
                print(f'{i} of {total} Completed - {collateType.value}')

    def getAllQueryIds(self):
        pipeline: list[dict] = [{ '$lookup': { 'from': 'queries', 'let': { 'marketplace': '$_id' }, 'pipeline': [ { '$match': { '$expr': { '$or': [ { '$eq': [ { '$ifNull': [ '$marketplace', None ] }, None ] }, { '$eq': [ '$marketplace', '$$marketplace' ] } ] } } } ], 'as': 'query' } }]
        pipeline.extend([self.pp.unwind("query"), self.pp.replaceWith({ "queryId": "$query._id" })])
        return self.pp.execute(CollectionType.DASHBOARD, pipeline).to_list()

    def getQueries(self):
        return [ { '$lookup': { 'from': 'queries', 'let': { 'marketplace': '$_id' }, 'pipeline': [ { '$match': { '$expr': { '$or': [ { '$eq': [ { '$ifNull': [ '$marketplace', None ] }, None ] }, { '$eq': [ '$marketplace', '$$marketplace' ] } ] } } } ], 'as': 'query' } }, { '$unwind': { 'path': '$query' } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$query', { 'marketplace': '$_id', 'uid': '$uid', 'endDate': '$endDate' } ] } } }, { '$set': { 'currParts': { '$dateToParts': { 'date': '$endDate' } } } }, { '$set': { 'dates': { '$cond': [ { '$eq': [ '$group', 'Days' ] }, { 'curr': { '$reduce': { 'input': { '$range': [ 1, { '$sum': [ '$days', 1 ] }, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$endDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } }, 'pre': { '$reduce': { 'input': { '$range': [ { '$sum': [ '$days', 1 ] }, { '$sum': [ { '$multiply': [ '$days', 2 ] }, 1 ] }, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$endDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } } }, '$dates' ] } } }, { '$set': { 'dates': { '$cond': [ { '$eq': [ '$group', 'Current Month' ] }, { 'curr': { '$reduce': { 'input': { '$range': [ { '$subtract': [ '$currParts.day', 1 ] }, 0, -1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateFromParts': { 'year': '$currParts.year', 'month': '$currParts.month', 'day': '$$this' } } ] ] } } }, 'pre': { '$let': { 'vars': { 'month': { '$cond': [ { '$eq': [ '$currParts.month', 1 ] }, 12, { '$subtract': [ '$currParts.month', 1 ] } ] }, 'year': { '$cond': [ { '$eq': [ '$currParts.month', 1 ] }, { '$subtract': [ '$currParts.year', 1 ] }, '$currParts.year' ] }, 'range': { '$cond': [ { '$eq': [ '$tag', 'Current vs Previous (Full)' ] }, { '$range': [ 0, 31, 1 ] }, { '$range': [ 0, { '$subtract': [ '$currParts.day', 1 ] }, 1 ] } ] } }, 'in': { '$let': { 'vars': { 'startDate': { '$dateFromParts': { 'year': '$$year', 'month': '$$month', 'day': 1 } } }, 'in': { '$reduce': { 'input': '$$range', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$let': { 'vars': { 'date': { '$dateAdd': { 'startDate': '$$startDate', 'unit': 'day', 'amount': '$$this' } } }, 'in': { '$cond': [ { '$eq': [ { '$month': '$$date' }, '$$month' ] }, [ '$$date' ], [] ] } } } ] } } } } } } } }, '$dates' ] } } }, { '$set': { 'dates': { '$cond': [ { '$eq': [ '$tag', 'Custom' ] }, { 'curr': { '$reduce': { 'input': { '$range': [ 0, { '$sum': [ { '$dateDiff': { 'startDate': '$curr.startDate', 'endDate': '$curr.endDate', 'unit': 'day' } }, 1 ] }, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateAdd': { 'startDate': '$curr.startDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } }, 'pre': { '$reduce': { 'input': { '$range': [ 0, { '$sum': [ { '$dateDiff': { 'startDate': '$pre.startDate', 'endDate': '$pre.endDate', 'unit': 'day' } }, 1 ] }, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateAdd': { 'startDate': '$pre.startDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } } }, '$dates' ] } } }, { '$set': { '_id': '$_id', 'marketplace': '$marketplace', 'dates': '$dates', 'allDates': { '$concatArrays': [ '$dates.curr', '$dates.pre' ] } } }, { '$replaceRoot': { 'newRoot': { 'queryId': '$_id', 'marketplace': '$marketplace', 'uid': '$uid', 'endDate': '$endDate', 'date': { '$reduce': { 'input': { '$objectToArray': '$dates' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'tag': '$$this.k', 'date': '$$this.v' } ] ] } } } } } }, { '$unwind': { 'path': '$date' } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', '$date' ] } } }, { '$unwind': { 'path': '$date' } } ]
    
    def getFields(self, collateType: CollateType):
        fields: list[str] = []
        if collateType==CollateType.SKU: fields = ['sku','asin','producttype','parentsku','parentasin']
        elif collateType==CollateType.ASIN: fields = ['asin','producttype','parentsku','parentasin']
        elif collateType==CollateType.PARENT: fields = ['producttype','parentsku','parentasin']
        elif collateType==CollateType.CATEGORY: fields = ['producttype']
        return fields
    
    def getProjections(self, collateType: CollateType):
        projections = ['sales','ad','traffic']
        projections.extend(self.getFields(collateType))
        return projections
    
    def getGroupStage(self, collateType: CollateType, withTag: bool):
        fields = self.getFields(collateType)
        fields.append('queryId')
        if withTag: fields.append('tag')
        exprs = list(map(lambda x: LookUpLetExpression(key=x), fields))
        groupings: dict = {'data': { '$push': '$data' }}
        if not withTag: groupings.update({'tag': { '$push': '$tag' }, 'allkeys': { '$first': '$allkeys' }, 'percentkeys': { '$first': '$percentkeys' }, 'reversegrowthkeys': { '$first': '$reversegrowthkeys' }, 'querykeys': { '$first': '$querykeys' }})
        return self.pp.group(exprs, groupings)
    
    def lookupDateAnalytics(self, collateType: CollateType):
        letExpr = [LookUpLetExpression(key='type', value=collateType.value), LookUpLetExpression(key="date")]
        expr = [LookUpPipelineMatchExpression(key='type'), LookUpPipelineMatchExpression(key='date')]
        pipeline:list[dict] = [self.pp.matchAllExpressions(expr)]
        pipeline.append(self.pp.project(self.getProjections(collateType),['_id']))
        pipeline.append(self.pp.replaceRoot({ '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$ROOT' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { "$cond": [ { "$eq": ["$$this.v", None] }, [], ["$$this"] ] } ] } } } }))
        return self.pp.lookup(CollectionType.DATE_ANALYTICS,'data', pipeline, letExpr)
    
    def pipeline(self, queryId: str, collateType: CollateType):
        pipeline: list[dict] = self.getQueries()
        filterQueryId = self.pp.match({"queryId": queryId})
        getData = self.lookupDateAnalytics(collateType)
        unwindData = self.pp.unwind("data")
        getNonObjectKeys = self.pp.removeDataTypesFromObject("data", ['object'])
        mergeSAT = {"data": self.pp.mergeAllObjectsInObjectToObject("data")}
        replaceRoot = self.pp.replaceRoot(self.pp.mergeObjects([self.pp.unsetField("$$ROOT","data"),getNonObjectKeys, mergeSAT]))
        groupWithTag = self.getGroupStage(collateType, True)
        dt = Datatransformer(self.pp,"data")
        transformData = dt.transformDataForQuery()
        openId = self.pp.replaceRoot(self.pp.mergeObjects([self.pp.unsetField("$$ROOT", "_id"), "$_id"]))
        groupWithoutTag = self.getGroupStage(collateType, False)
        growth = dt.addGrowth()
        setTypeDict = { "data": "$data",'type': collateType.value}
        if collateType==CollateType.SKU: setTypeDict.update({"value": '$_id.sku',"parent": "$_id.parentsku", "category": "$_id.producttype"})
        elif collateType==CollateType.ASIN: setTypeDict.update({"value": '$_id.asin', "parent": "$_id.parentsku", "category": "$_id.producttype"})
        elif collateType==CollateType.PARENT: setTypeDict.update({"value": '$_id.parentsku', "category": "$_id.producttype"})
        elif collateType==CollateType.CATEGORY: setTypeDict.update({"value": '$_id.producttype'})
        setData = self.pp.replaceRoot(self.pp.mergeObjects(["$_id", setTypeDict]))
        merge = self.pp.merge(CollectionType.QUERY_RESULTS)
        pipeline.extend([filterQueryId, getData, unwindData, replaceRoot, groupWithTag])
        pipeline.extend(transformData)
        pipeline.extend([openId, groupWithoutTag])
        pipeline.extend(growth)
        pipeline.extend([setData, merge])
        return pipeline
        

    
