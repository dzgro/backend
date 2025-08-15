
from dzgroshared.models.enums import CollateType,CollectionType
from dzgroshared.db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression, LookUpLetExpression
from dzgroshared.db.DataTransformer import Datatransformer

def pipeline(pp: PipelineProcessor, collateType: CollateType, month:str, value: str|None):
    pipeline: list[dict] = [pp.match({"_id": pp.marketplace, "uid": pp.uid})]
    pipeline.extend(pp.getMonths(month))
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
    pipeline.extend(Datatransformer(pp).transformDataForAllKeys())
    replaceWith = pp.replaceWith({ 'keymetrics': [ { 'label': 'Revenue', 'value': '$data.revenue.value' }, { 'label': 'Units', 'value': '$data.netquantity.value' }, { 'label': 'Average price', 'value': '$data.avgprice.value' }, { 'label': 'Average price', 'value': '$data.avgprice.value' }, { 'label': 'Ad Spend', 'value': '$data.cost.value' }, { 'label': 'CPC', 'value': '$data.cpc.value' }, { 'label': 'Ad Sales', 'value': '$data.sales.value' }, { 'label': 'ROAS', 'value': '$data.roas.value' } ], 'bars': [ { 'label': 'TACoS', 'value': { '$round': [ '$data.tacos.rawvalue', 1 ] } }, { 'label': 'ACoS', 'value': { '$round': [ '$data.acos.rawvalue', 1 ] } }, { 'label': 'Return %', 'value': { '$round': [ '$data.returnpercent.rawvalue', 1 ] } }, { 'label': 'Net Proceeds %', 'value': { '$round': [ '$data.netproceedspercent.rawvalue', 1 ] } } ], 'groups': [ { 'label': 'Page Views', 'items': [ { 'label': 'Browser', 'color': '#84AE92', 'icon': 'pi pi-desktop', 'value': { '$round': [ '$data.browserpageviewspercent.rawvalue', 0 ] } }, { 'label': 'Mobile App', 'icon': 'pi pi-mobile', 'color': '#F97A00', 'value': { '$round': [ '$data.mobileapppageviewspercent.rawvalue', 0 ] } } ] }, { 'label': 'Revenue by Fulfillment', 'items': [ { 'label': 'Merchant', 'icon': 'pi pi-home', 'color': '#84AE92', 'value': { '$round': [ '$data.fbmrevenuepercent.rawvalue', 0 ] } }, { 'label': 'FBA / Flex / Others', 'icon': 'pi pi-warehouse', 'color': '#F97A00', 'value': { '$round': [ '$data.fbarevenuepercent.rawvalue', 0 ] } } ] }, { 'label': 'Sessions', 'items': [ { 'label': 'Browser', 'icon': 'pi pi-desktop', 'color': '#84AE92', 'value': { '$round': [ '$data.browsersessionspercent.rawvalue', 0 ] } }, { 'label': 'Mobile App', 'icon': 'pi pi-mobile', 'color': '#F97A00', 'value': { '$round': [ '$data.mobileappsessionspercent.rawvalue', 0 ] } } ] } ] })
    pipeline.append(replaceWith)
    return pipeline
