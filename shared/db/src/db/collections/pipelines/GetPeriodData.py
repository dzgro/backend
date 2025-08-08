
from models.enums import CollateType,CollectionType
from db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression, PipelineProcessor, LookUpLetExpression
from db.DataTransformer import Datatransformer


def pipeline(pp: PipelineProcessor, collateType: CollateType, value: str|None):
    matchStage = {"$match": {"_id": pp.marketplace}}
    setDates = pp.set({ 'dates': { '$let': { 'vars': { 'tm': { '$month': '$enddate' }, 'date': { '$dayOfMonth': '$enddate' }, 'ty': { '$year': '$enddate' } }, 'in': { '$let': { 'vars': { 'lm': { '$cond': [ { '$eq': [ '$$tm', 12 ] }, 1, { '$subtract': [ '$$tm', 1 ] } ] }, 'ly': { '$cond': [ { '$eq': [ '$$tm', 1 ] }, { '$subtract': [ '$$ty', 1 ] }, '$$ty' ] } }, 'in': { '$let': { 'vars': { 'dates': { '$reduce': { 'input': { '$range': [ 0, 63, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$let': { 'vars': { 'date': { '$dateSubtract': { 'startDate': '$enddate', 'amount': '$$this', 'unit': 'day' } } }, 'in': { '$let': { 'vars': { 'dm': { '$month': '$$date' }, 'dy': { '$year': '$$date' } }, 'in': { '$cond': [ { '$or': [ { '$and': [ { '$eq': [ '$$dm', '$$tm' ] }, { '$eq': [ '$$dy', '$$ty' ] } ] }, { '$and': [ { '$eq': [ '$$dm', '$$lm' ] }, { '$eq': [ '$$dy', '$$ly' ] } ] } ] }, [ '$$date' ], [] ] } } } } } ] } } } }, 'in': { '$reduce': { 'input': '$$dates', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'date': '$$this', 'durations': { '$concatArrays': [ [], { '$cond': [ { '$eq': [ { '$month': '$$this' }, '$$tm' ] }, [ { 'index': 1, 'label': 'This Month' } ], [] ] }, { '$cond': [ { '$eq': [ { '$month': '$$this' }, '$$lm' ] }, [ { 'index': 3, 'label': 'Last Month (Complete)' } ], [] ] }, { '$cond': [ { '$and': [ { '$eq': [ { '$month': '$$this' }, '$$lm' ] }, { '$lte': [ { '$dayOfMonth': '$$this' }, '$$date' ] } ] }, [ { 'index': 2, 'label': 'Last Month (Till Date)' } ], [] ] }, { '$cond': [ { '$lt': [ { '$dateDiff': { 'startDate': '$$this', 'endDate': '$enddate', 'unit': 'day' } }, 30 ] }, [ { 'index': 4, 'label': 'Past 30 Days' } ], [] ] } ] } } ] ] } } } } } } } } } })
    unwindDates = pp.unwind("dates")
    replaceRoot= pp.replaceRoot(pp.mergeObjects([{ 'uid': '$uid', 'marketplace': '$_id' }, "$dates"]))
    expr = [LookUpPipelineMatchExpression(key='collatetype', value=collateType.value), LookUpPipelineMatchExpression(key='date'),LookUpPipelineMatchExpression(key=collateType.value, value=value)]
    letkeys=['date',collateType.value, 'value']
    if collateType==CollateType.MARKETPLACE: 
        expr.pop(-1)
        letkeys.pop(-1)
    pipeline:list[dict] = [pp.matchAllExpressions(expr)]
    pipeline.append(pp.project(['sales','ad','traffic'],['_id']))
    pipeline.append(pp.replaceRoot({ '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$ROOT' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$objectToArray': { '$ifNull': [ '$$this.v', {} ] } } ] } } } }))
    lookUpAnalytics = pp.lookup(CollectionType.DATE_ANALYTICS,'data', pipeline, letkeys=letkeys)
    setData = pp.set({"data": pp.first("data")})
    unwindDuration = pp.unwind("durations")
    groupByDuration = pp.group([LookUpLetExpression(key="durations")], groupings={'data': { '$push': '$data' }, 'dates': { '$push': '$date' }})
    setDatesAsDurations = pp.set({"date": { 'dates': { '$let': { 'vars': { 'dates': { '$sortArray': { 'input': '$dates', 'sortBy': 1 } } }, 'in': { '$concat': [ { '$dateToString': { 'date': { '$first': '$$dates' }, 'format': '%b %d' } }, ' - ', { '$dateToString': { 'date': { '$last': '$$dates' }, 'format': '%b %d' } } ] } } } }})
    pipeline = [matchStage, setDates, unwindDates, replaceRoot, lookUpAnalytics, setData, unwindDuration, groupByDuration, setDatesAsDurations]
    pipeline.extend(Datatransformer(pp).groupDataAsKeysGroup())
    sort = pp.sort({"_id.durations.index": 1})
    replaceRoot = pp.replaceRoot({ "data": "$data", "period": "$_id.durations.label", "dates": "$date.dates" })
    pipeline.extend([sort, replaceRoot])
    return pipeline
