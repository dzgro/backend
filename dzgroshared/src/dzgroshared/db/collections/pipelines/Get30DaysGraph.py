
from dzgroshared.models.enums import CollateType, CollectionType
from dzgroshared.db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression, LookUpLetExpression
from dzgroshared.db.DataTransformer import Datatransformer


def pipeline(pp: PipelineProcessor, collateType: CollateType, key: str, value: str|None):
    matchStage = pp.match({"_id": pp.marketplace, "uid": pp.uid})
    project = {"$project": {"enddate":1,"uid": 1, "marketplace":"$_id", "_id": 0}}
    setDates = pp.set({"date": { '$reduce': { 'input': { '$range': [ 0, 30, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$enddate', 'amount': '$$this', 'unit': 'day' } } ] ] } } } })
    unwindDate = pp.unwind("date")
    letExpr = [LookUpLetExpression(key='date'),LookUpLetExpression(key='collatetype', value=collateType.value)]
    expr = [LookUpPipelineMatchExpression(key='collatetype'), LookUpPipelineMatchExpression(key='date')]
    if value: 
        letExpr.append(LookUpLetExpression(key='value', value=value))
        expr.append(LookUpPipelineMatchExpression(key='value'))
    innerpipeline:list[dict] = [pp.matchAllExpressions(expr), pp.project(['sales','ad','traffic'],['_id'])]
    innerpipeline.append(pp.replaceRoot({ '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$ROOT' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$objectToArray': { '$ifNull': [ '$$this.v', {} ] } } ] } } } }))
    lookUpAnalytics = pp.lookup(CollectionType.DATE_ANALYTICS, 'data', innerpipeline, letExpressions=letExpr)
    transformer = Datatransformer(pp)
    sortByDate = pp.sort({"date": 1})
    replaceRoot = pp.replaceRoot({ 'date': { '$dateToString': { 'date': '$date', 'format': '%b %d, %Y' } }, 'value': { '$round': [ { '$ifNull': [ f'$data.{key}', 0 ] }, 1 ] } })
    group = pp.group(None, {'dates': { '$push': '$date' }, 'values': { '$push': '$value' }})
    pipeline = [matchStage, project, setDates, unwindDate,lookUpAnalytics ]
    pipeline.extend(transformer.transformDataForQuery())
    pipeline.extend([sortByDate, replaceRoot, group])
    return pipeline