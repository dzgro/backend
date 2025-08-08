
from models.enums import CollateType,CollectionType
from db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression, PipelineProcessor, LookUpLetExpression
from db.DataTransformer import Datatransformer


def pipeline(pp: PipelineProcessor, collateType: CollateType, value: str|None):
    pipeline: list[dict] = [pp.match({"_id": pp.marketplace, "uid": pp.uid})]
    pipeline.extend(pp.getMonths())
    unwindDate = pp.unwind("date")
    expr = [LookUpPipelineMatchExpression(key='collatetype', value=collateType.value),LookUpPipelineMatchExpression(key='date'),  LookUpPipelineMatchExpression(key=collateType.value, value=value)]
    if collateType==CollateType.MARKETPLACE: expr.pop(-1)
    innerPipeline:list[dict] = [pp.matchAllExpressions(expr),pp.project(['sales','ad','traffic'],['_id'])]
    innerPipeline.append(pp.replaceRoot({ '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$ROOT' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$objectToArray': { '$ifNull': [ '$$this.v', {} ] } } ] } } } }))
    letExpr = [LookUpLetExpression(key="date"), LookUpLetExpression(key="type", value=collateType.value)]
    lookUpAnalytics = pp.lookup(CollectionType.DATE_ANALYTICS,'data', innerPipeline, letExpr)
    setData = pp.set({"data": pp.first("data")})
    groupByDuration = pp.group([LookUpLetExpression(key="month"),LookUpLetExpression(key="year"),LookUpLetExpression(key="period")], groupings={'data': { '$push': '$data' }, 'dates': { '$push': '$date' }})
    pipeline.extend([unwindDate, lookUpAnalytics, setData, groupByDuration])
    pipeline.extend(Datatransformer(pp).groupDataAsKeysGroup())
    sort = pp.sort({ '_id.year': -1, '_id.month': -1 })
    replaceWith = pp.replaceWith({ 'data': '$data', 'month': { 'period': '$_id.period', 'month': '$_id.month', 'year': '$_id.year', 'dates': '$date.dates' } })
    group = pp.group(None, {'data': { '$push': '$data' }})
    setData = pp.set({"data": { '$reduce': { 'input': { '$range': [ 0, { '$size': '$data' }, 1 ] }, 'initialValue': [], 'in': { '$let': { 'vars': { 'month': { '$arrayElemAt': [ '$months', '$$this' ] }, 'data': { '$arrayElemAt': [ '$data', '$$this' ] } }, 'in': { '$reduce': { 'input': { '$reduce': { 'input': '$$data', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', '$$this.items' ] } } }, 'initialValue': '$$value', 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.label', '$$this.label' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ { 'label': '$$this.label','key': '$$this.key', 'data': [ '$$this.value.value' ] } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.label', '$$this.label' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'data': { '$concatArrays': [ '$$v.data', [ '$$this.value.value' ] ] } } ] } ] } } } ] } } } } } } }})
    unwindData = pp.unwind("data")
    replaceData = pp.replaceWith("$data")
    pipeline.extend([sort, replaceWith, group, setData, unwindData, replaceData])
    return pipeline
