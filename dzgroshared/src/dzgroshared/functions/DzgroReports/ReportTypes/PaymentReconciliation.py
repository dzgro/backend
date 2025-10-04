from datetime import datetime, timezone
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.dzgro_reports.model import DzgroPaymentReconRequest, DzgroReport
from dzgroshared.db.enums import DzgroReportType, DzroReportPaymentReconSettlementRangeType, Operator,CollectionType
from dzgroshared.db.PipelineProcessor import LookUpLetExpression, LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.db.model import PyObjectId

class PaymentReconReportCreator:
    client: DzgroSharedClient
    reportId: PyObjectId
    options: DzgroPaymentReconRequest
    reporttype: DzgroReportType

    def __init__(self, client: DzgroSharedClient, report: DzgroReport, options: DzgroPaymentReconRequest ) -> None:
        self.client = client
        self.reportId = report.id
        self.reporttype = report.reporttype
        self.options = options

    async def execute(self):
        orders = self.client.db.orders
        timezone = (await self.client.db.marketplaces.getCountryBidsByMarketplace(self.client.marketplace.id)).timezone
        pipeline = self.pipeline(orders.db.pp, timezone)
        await orders.db.aggregate(pipeline)

    def pipeline(self, pp: PipelineProcessor, timezone: str):
        dates = pp.getDatesBetweenTwoDates(self.options.dates.startDate, self.options.dates.endDate)
        pipeline: list[dict] = [pp.matchAllExpressions([LookUpPipelineMatchExpression(key='date', value=dates, operator=Operator.IN)])]
        letkeys = ['sku','asin'] if self.reporttype == DzgroReportType.PRODUCT_PAYMENT_RECON else None
        lookupOrderItems =  pp.lookup(CollectionType.ORDER_ITEMS, 'item', localField="_id", foreignField="order", pipeline=[
            pp.group(letkeys=letkeys, groupings={'price': { '$sum': '$price' }, 'tax': { '$sum': '$tax' }, 'shippingprice': { '$sum': '$shippingprice' }, 'shippingtax': { '$sum': '$shippingtax' }, 'giftwrapprice': { '$sum': '$giftwrapprice' }, 'giftwraptax': { '$sum': '$giftwraptax' }, 'itempromotiondiscount': { '$sum': '$itempromotiondiscount' }, 'shippromotiondiscount': { '$sum': '$shippromotiondiscount' } }),
            pp.replaceRoot(pp.mergeObjects(['$$ROOT', '$_id'])),
            pp.project([],['_id'])
        ])
        settlementPipeline = [
            pp.matchAllExpressions(expressions=[
                LookUpPipelineMatchExpression(key='orderid', value='$$orderid'),
                LookUpPipelineMatchExpression(key='amounttype', value='ItemPrice', operator=Operator.NE),
            ]),
            pp.project([],['_id'])
        ]
        settlementdates: dict|None = None
        if self.options.settlementRange==DzroReportPaymentReconSettlementRangeType.SAME_END_DATE: settlementdates=dates
        elif self.options.settlementRange==DzroReportPaymentReconSettlementRangeType.DIFFERENT_END_DATE and self.options.settlementDate: settlementdates=pp.getDatesBetweenTwoDates(self.options.dates.startDate, self.options.settlementDate)
        if settlementdates: settlementPipeline.append(pp.match({"$expr": {"$in": ["$date", settlementdates]}}))
        lookupSettlements = pp.lookup(CollectionType.SETTLEMENTS, 'settlements', letkeys=['orderid'], pipeline=settlementPipeline)
        setProducts = pp.set({'products': { '$reduce': { 'input': '$item', 'initialValue': [ { 'expense': { '$reduce': { 'input': { '$filter': { 'input': '$settlements', 'as': 's', 'cond': { '$eq': [ { '$ifNull': [ '$$s.sku', None ] }, None ] } } }, 'initialValue': 0, 'in': { '$sum': [ '$$value', '$$this.amount' ] } } } } ], 'in': { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ '$$this', { 'expense': { '$reduce': { 'input': { '$filter': { 'input': '$settlements', 'as': 's', 'cond': { '$eq': [ '$$this.sku', '$$s.sku' ] } } }, 'initialValue': 0, 'in': { '$sum': [ '$$value', '$$this.amount' ] } } } } ] } ] ] } } }})
        if self.reporttype == DzgroReportType.ORDER_PAYMENT_RECON:
            setProducts = pp.set({ 'products': { '$reduce': { 'input': '$item', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ '$$this', { 'expense': { '$reduce': { 'input': '$settlements', 'initialValue': 0, 'in': { '$sum': [ '$$value', '$$this.amount' ] } } } } ] } ] ] } } }})
        projectProjects = pp.project(['orderid','orderdate','products'], ['_id'])
        unwindProducts = pp.unwind('products')
        setNewRoot = pp.replaceRoot(pp.mergeObjects([{ '$unsetField': { 'input': '$$ROOT', 'field': 'products' } }, '$products']))
        roundAllDouble = pp.roundAllDouble(2)
        setPrice = pp.set({ 'netprice': { '$subtract': [ { '$sum': [ '$price', '$shippingprice', '$giftwrapprice' ] }, { '$sum': [ '$itempromotiondiscount', '$shippromotiondiscount' ] } ] }, 'nettax': { '$sum': [ '$tax', '$shippingtax', '$giftwraptax' ] } })
        filteroutNull = pp.match({ "$expr": { "$or": [ { "$ne": [ { "$ifNull": [ "$sku", None ] }, None ] }, { "$gt": [ "$expense", 0 ] } ] }})
        setProceeds = pp.set({ 'netproceeds': { '$round': [ { '$add': [ '$netprice', '$expense' ] }, 2 ] }, 'createdat': "$$NOW", 'reportid': self.reportId, "orderdate": { "$dateToString": { "date": "$orderdate", "timezone": timezone } } })
        sortByDate = pp.sort({ 'orderdate': 1 })
        merge = pp.merge(CollectionType.DZGRO_REPORT_DATA, whenMatched="merge", whenNotMatched="insert")
        pipeline.extend([lookupOrderItems, lookupSettlements, setProducts, projectProjects, unwindProducts, setNewRoot, roundAllDouble, setPrice])
        if self.reporttype == DzgroReportType.PRODUCT_PAYMENT_RECON: pipeline.append(filteroutNull)
        pipeline.extend([setProceeds, sortByDate, merge])
        return pipeline
