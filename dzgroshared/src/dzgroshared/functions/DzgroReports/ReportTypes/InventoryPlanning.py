from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.dzgro_reports.model import DzgroInventoryPlanningRequest, DzgroReportDates
from dzgroshared.db.enums import QueryTag, CollectionType, DzgroInventoryPlanningRequestConfiguration, Operator
from dzgroshared.db.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.functions.DzgroReports.ReportTypes import InventoryGroups
from dzgroshared.db.model import PyObjectId
from dzgroshared.utils import date_util

class InventoryPlannerReport:
    client: DzgroSharedClient
    reportId: PyObjectId
    req: DzgroInventoryPlanningRequest

    def __init__(self, client: DzgroSharedClient, reportId: PyObjectId, req: DzgroInventoryPlanningRequest ) -> None:
        self.client = client
        self.reportId = reportId
        self.req = req

    async def execute(self):
        pipeline = await self.pipeline(self.client.db.query_results.db.pp)
        await self.client.db.date_analytics.db.aggregate(pipeline)
    
    
    async def pipeline(self, pp: PipelineProcessor):
        if not self.req.dayCount: raise ValueError("Day count is required")
        if self.req.configuration==DzgroInventoryPlanningRequestConfiguration.DAYS and self.req.days:
            marketplace = await self.client.db.marketplaces.getMarketplace(self.client.marketplace)
            if not marketplace.enddate: raise ValueError("Marketplace end date is required")
            self.req.dates = DzgroReportDates(startDate=date_util.subtract(marketplace.enddate, self.req.days), endDate=marketplace.enddate)
        if not self.req.dates: raise ValueError("Invalid date range")
        dates = pp.getDatesBetweenTwoDates(self.req.dates.startDate, self.req.dates.endDate)
        matchstage = pp.matchAllExpressions([LookUpPipelineMatchExpression(key='date', value=dates, operator=Operator.IN), LookUpPipelineMatchExpression(key='collatetype', value='sku')])
        group = pp.group(letkeys=['sku','asin'], groupings={'soldqty': { '$sum': "$sales.quantity" }})
        filterSoldProducts = pp.match({ 'soldqty': { '$gt': 0 } })
        openId = pp.openId()
        letkeys=['sku','asin']
        innerpipeline = [pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key) for key in letkeys]), pp.project(['quantity'])]
        getQuantity = pp.lookup(CollectionType.PRODUCTS,'result',letkeys=letkeys, pipeline=innerpipeline)
        replaceRoot = pp.replaceRoot(pp.mergeObjects(["$$ROOT", pp.first('result')]))
        setdays = pp.set({"inventorydays": { '$toInt': { '$divide': [ '$quantity', { '$divide': [ '$soldqty', self.req.dayCount ] } ] } }})
        setTag = pp.set({"inventorytag": { '$switch': { 'branches': [ { 'case': { '$or': [ { '$eq': [ '$quantity', 0 ] }, { '$eq': [ '$inventorydays', 0 ] } ] }, 'then': 'Out of Stock' }, { 'case': { '$lte': [ '$inventorydays', 7 ] }, 'then': 'Under a Week' }, { 'case': { '$lte': [ '$inventorydays', 15 ] }, 'then': '1-2 Weeks' }, { 'case': { '$lte': [ '$inventorydays', 30 ] }, 'then': '15-30 Days' }, { 'case': { '$lte': [ '$inventorydays', 60 ] }, 'then': '1-2 months' } ], 'default': 'Over 2 Months' } }})
        setReportId = pp.set({"reportid": self.reportId, "inventorydays": { "$cond": { "if": { "$gt": [ "$inventorydays", 60 ] }, "then": ">60 Days", "else": "$inventorydays" } }, "startdate": self.req.dates.startDate, "enddate": self.req.dates.endDate })
        project = pp.project([],["_id","uid","marketplace", "result"])
        merge  = pp.merge(CollectionType.DZGRO_REPORT_DATA)
        pipeline = [matchstage, group, filterSoldProducts, openId, getQuantity, replaceRoot, setdays, setTag, setReportId, project, merge]
        return pipeline

