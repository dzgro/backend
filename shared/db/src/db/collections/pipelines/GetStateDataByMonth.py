
from models.enums import CollateType,CollectionType
from db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression, PipelineProcessor, LookUpLetExpression
from db.DataTransformer import Datatransformer


def pipeline(pp: PipelineProcessor, collateType: CollateType, month: str, value: str|None):
    pipeline: list[dict] = [pp.match({"_id": pp.marketplace, "uid": pp.uid})]
    pipeline.extend(pp.getMonths())
    matchMonth = pp.match({"monthStr": month})
    unwindDate = pp.unwind("date")
    expr = [LookUpPipelineMatchExpression(key='collatetype', value=collateType.value),LookUpPipelineMatchExpression(key='date'),  LookUpPipelineMatchExpression(key=collateType.value, value=value)]
    if collateType==CollateType.MARKETPLACE: expr.pop(-1)
    innerPipeline:list[dict] = [pp.matchAllExpressions(expr),pp.project(['sales','state'],['_id'])]
    letExpr = [LookUpLetExpression(key="date"), LookUpLetExpression(key="type", value=collateType.value), LookUpLetExpression(key="value", value=value)]
    lookUpAnalytics = pp.lookup(CollectionType.STATE_ANALYTICS,'sales', innerPipeline, letExpr)
    unwindSales = pp.unwind('sales')
    replaceRoot = pp.replaceRoot(pp.mergeObjects(["$$ROOT","$sales"]))
    groupByState = pp.group([LookUpLetExpression(key="state")], groupings={'data': { '$push': '$sales' }})
    sortByRevenue = pp.sort({"data.revenue": -1})
    pipeline.extend([matchMonth,unwindDate, lookUpAnalytics, unwindSales, replaceRoot, groupByState, sortByRevenue])
    pipeline.extend(Datatransformer(pp).groupDataAsKeysGroup())
    replaceRoot =pp.replaceRoot({ 'state': '$_id.state', 'data': { '$slice': [ { '$getField': { 'input': { '$arrayElemAt': [ '$data', 0 ] }, 'field': 'items' } }, 10 ] } })
    setData = pp.set({ 'data': { '$reduce': { 'input': '$data', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { "label": "$$this.label", "value": "$$this.value.value" } ] ] } } } })
    pipeline.extend([replaceRoot, setData])
    return pipeline
