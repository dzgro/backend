from app.HelperModules.Utils.enums import Operator
from app.HelperModules.Db.models import CollectionType
from app.HelperModules.Pipelines.Marketplace.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor

def execute(pp: PipelineProcessor, reportId: str):

    def lookupOrderItems():
        groupOrderItems = pp.group(None, groupings={'price': { '$sum': '$price' }, 'tax': { '$sum': '$tax' }, 'shippingprice': { '$sum': '$shippingprice' }, 'shippingtax': { '$sum': '$shippingtax' }, 'giftwrapprice': { '$sum': '$giftwrapprice' }, 'giftwraptax': { '$sum': '$giftwraptax' }, 'itempromotiondiscount': { '$sum': '$itempromotiondiscount' }, 'shippromotiondiscount': { '$sum': '$shippromotiondiscount' } })
        innerpipeline = [pp.matchAllExpressions(matchExprs), groupOrderItems, pp.project([],["_id"])]
        return pp.lookup(CollectionType.ORDER_ITEMS, 'price', letkeys=letkeys, pipeline=innerpipeline)

    def lookupSettlements():
        matchExprs.append(LookUpPipelineMatchExpression(key='amounttype', value='ItemPrice', operator=Operator.NE))
        groupOrderItems = pp.group(None, groupings={"expense": { "$sum": "$amount" }})
        innerpipeline = [pp.matchAllExpressions(matchExprs), groupOrderItems, pp.project([],["_id"])]
        return pp.lookup(CollectionType.SETTLEMENTS, 'expense', letkeys=letkeys, pipeline=innerpipeline)

    matchStage = pp.matchMarketplace()
    letkeys=['uid','marketplace','orderid']
    matchExprs = [LookUpPipelineMatchExpression(key=x) for x in letkeys]
    lookup1 = lookupOrderItems()
    lookup2 = lookupSettlements()
    setExpense = pp.set({ "expense": { "$cond": [ { "$eq": [ {"$size": "$expense"}, 0 ] }, 0, { "$first": "$expense.expense" } ] }})
    setPrice = pp.set({"price": { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': { '$first': '$price' } }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': [ { '$in': [ '$orderstatus', [ 'Cancelled', 'Shipped - Returned to Seller', 'Shipped - Returning to Seller' ] ] }, 0, '$$this.v' ] } } ] ] } } } } })
    mergePrice = pp.replaceRoot(pp.mergeObjects(['$$ROOT', '$price']))
    setNetPrice = pp.set({ 'netprice': { '$subtract': [ { '$sum': [ '$price', '$shippingprice', '$giftwrapprice' ] }, { '$sum': [ '$itempromotiondiscount', '$shippromotiondiscount' ] } ] }, 'nettax': { '$sum': [ '$tax', '$shippingtax', '$giftwraptax' ] } })
    setNetProceeds = pp.set({ 'netproceeds': { '$round': [ { '$sum': [ '$netprice', '$expense' ] }, 2 ] }, 'reportid': reportId })
    unsetFields = pp.unset([ '_id', 'date', 'country', 'city', 'code', 'uid', 'marketplace' ])
    convertDate = pp.set({ 'orderdate': { '$dateToString': { 'date': '$orderdate' } } })
    convertIntToDouble = pp.convertIntToDouble()
    merge = pp.merge(CollectionType.DZGRO_REPORT_DATA)
    pipeline = [matchStage, lookup1, lookup2, setExpense,setPrice,mergePrice, setNetPrice, setNetProceeds, unsetFields, convertDate, convertIntToDouble,merge]
    pp.execute(CollectionType.ORDERS, pipeline)
    
