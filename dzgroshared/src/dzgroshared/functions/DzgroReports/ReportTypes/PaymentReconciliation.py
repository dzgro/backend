from datetime import datetime, timezone
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.dzgro_reports import DzroReportPaymentReconRequest
from dzgroshared.models.enums import Operator,CollectionType
from dzgroshared.db.PipelineProcessor import LookUpLetExpression, LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.models.model import PyObjectId

class PaymentReconReportCreator:
    client: DzgroSharedClient
    reportId: PyObjectId
    options: DzroReportPaymentReconRequest

    def __init__(self, client: DzgroSharedClient, reportId: PyObjectId, options: DzroReportPaymentReconRequest ) -> None:
        self.client = client
        self.reportId = reportId
        self.options = options

    def getProjection(self)->list[dict]:
        return [
            {
                "$project": {
                    'Order Id': "$orderid",
                    'Order Date': '$orderdate',
                    'SKU': '$sku',
                    'ASIN': '$asin',
                    'Price': '$price',
                    'Tax': '$tax',
                    'Gift Wrap Price': '$giftwrapprice',
                    'Gift Wrap Tax': '$giftwraptax',
                    'Shipping Price': '$shippingprice',
                    'Shipping Tax': '$shippingtax',
                    'Shipping Promotion Discount': '$shippromotiondiscount',
                    'Item Promotion Discount': '$itempromotiondiscount',
                    'Net Price': '$netprice',
                    'Net Tax': '$nettax',
                    'Expense': '$expense',
                    'Net Proceeds': '$netproceeds'
                }
            },
            {
                "$project": {
                    '_id': 0,
                    'uid': 0,
                    'marketplace': 0,
                    'reportid': 0,
                    'createdat': 0
                }
            }
        ]

    async def execute(self):
        orders = self.client.db.orders
        timezone = (await self.client.db.marketplaces.getCountryBidsByMarketplace(self.client.marketplace)).timezone
        pipeline = self.pipeline(orders.db.pp, timezone)
        await orders.db.aggregate(pipeline)
        count = await self.client.db.dzgro_reports_data.count(self.reportId)
        return count, self.getProjection()

    def pipeline(self, pp: PipelineProcessor, timezone: str):
        dates = pp.getDatesBetweenTwoDates(self.options.dates.startDate, self.options.dates.endDate)
        pipeline: list[dict] = [pp.matchAllExpressions([LookUpPipelineMatchExpression(key='date', value=dates, operator=Operator.IN)])]
        lookupOrderItems =  pp.lookup(CollectionType.ORDER_ITEMS, 'item', localField="_id", foreignField="order", pipeline=[
            pp.group(letkeys=['sku','asin'], groupings={'price': { '$sum': '$price' }, 'tax': { '$sum': '$tax' }, 'shippingprice': { '$sum': '$shippingprice' }, 'shippingtax': { '$sum': '$shippingtax' }, 'giftwrapprice': { '$sum': '$giftwrapprice' }, 'giftwraptax': { '$sum': '$giftwraptax' }, 'itempromotiondiscount': { '$sum': '$itempromotiondiscount' }, 'shippromotiondiscount': { '$sum': '$shippromotiondiscount' } }),
            pp.replaceRoot(pp.mergeObjects(['$$ROOT', '$_id'])),
            pp.project([],['_id'])
        ])
        lookupSettlements = pp.lookup(CollectionType.SETTLEMENTS, 'settlements', letkeys=['orderid'], pipeline=[
            pp.matchAllExpressions(expressions=[
                LookUpPipelineMatchExpression(key='orderid', value='$$orderid'),
                LookUpPipelineMatchExpression(key='amounttype', value='ItemPrice', operator=Operator.NE),
            ]),
            pp.project([],['_id'])
        ])
        setProducts = pp.set({'products': { '$reduce': { 'input': '$item', 'initialValue': [ { 'expense': { '$reduce': { 'input': { '$filter': { 'input': '$settlements', 'as': 's', 'cond': { '$eq': [ { '$ifNull': [ '$$s.sku', None ] }, None ] } } }, 'initialValue': 0, 'in': { '$sum': [ '$$value', '$$this.amount' ] } } } } ], 'in': { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ '$$this', { 'expense': { '$reduce': { 'input': { '$filter': { 'input': '$settlements', 'as': 's', 'cond': { '$eq': [ '$$this.sku', '$$s.sku' ] } } }, 'initialValue': 0, 'in': { '$sum': [ '$$value', '$$this.amount' ] } } } } ] } ] ] } } }})
        projectProjects = pp.project(['orderid','orderdate','products'], ['_id'])
        unwindProducts = pp.unwind('products')
        setNewRoot = pp.replaceRoot(pp.mergeObjects([{ '$unsetField': { 'input': '$$ROOT', 'field': 'products' } }, '$products']))
        roundAllDouble = pp.roundAllDouble(2)
        setPrice = pp.set({ 'netprice': { '$subtract': [ { '$sum': [ '$price', '$shippingprice', '$giftwrapprice' ] }, { '$sum': [ '$itempromotiondiscount', '$shippromotiondiscount' ] } ] }, 'nettax': { '$sum': [ '$tax', '$shippingtax', '$giftwraptax' ] } })
        filteroutNull = pp.match({ "$expr": { "$or": [ { "$ne": [ { "$ifNull": [ "$sku", None ] }, None ] }, { "$gt": [ "$expense", 0 ] } ] }})
        setProceeds = pp.set({ 'netproceeds': { '$round': [ { '$add': [ '$netprice', '$expense' ] }, 2 ] }, 'createdat': "$$NOW", 'reportid': self.reportId, "orderdate": { "$dateToString": { "date": "$orderdate", "timezone": timezone } } })
        sortByDate = pp.sort({ 'orderdate': 1 })
        merge = pp.merge(CollectionType.DZGRO_REPORT_DATA, whenMatched="merge", whenNotMatched="insert")
        pipeline.extend([lookupOrderItems, lookupSettlements, setProducts, projectProjects, unwindProducts, setNewRoot, roundAllDouble, setPrice, filteroutNull, setProceeds, sortByDate, merge])
        return pipeline
