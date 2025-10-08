from datetime import datetime, timezone
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.dzgro_reports.model import KeyMetricsRequest, DzgroReport
from dzgroshared.db.enums import DzgroReportType, DzroReportPaymentReconSettlementRangeType, Operator,CollectionType
from dzgroshared.db.PipelineProcessor import LookUpLetExpression, LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.db.model import PyObjectId

class KeyMetricsReportCreator:
    client: DzgroSharedClient
    reportId: PyObjectId
    options: KeyMetricsRequest
    reporttype: DzgroReportType

    def __init__(self, client: DzgroSharedClient, report: DzgroReport, options: KeyMetricsRequest) -> None:
        self.client = client
        self.reportId = report.id
        self.reporttype = report.reporttype
        self.options = options

    async def execute(self):
        date_analytics = self.client.db.date_analytics
        pipeline = self.pipeline(date_analytics.db.pp)
        await date_analytics.db.aggregate(pipeline)

    def pipeline(self, pp: PipelineProcessor):
        dates = pp.getDatesBetweenTwoDates(self.options.dates.startDate, self.options.dates.endDate)
        pipeline: list[dict] = [pp.matchAllExpressions([LookUpPipelineMatchExpression(key='date', value=dates, operator=Operator.IN), LookUpPipelineMatchExpression(key='collatetype', value=self.options.collatetype.value)])]
        dt = Datatransformer(pp)
        group = pp.group(id='$value', groupings={"data": {"$push": "$$ROOT"}})
        setData = pp.set({ 'data': { '$arrayToObject': { '$map': { 'input': { '$setUnion': { '$map': { 'input': { '$reduce': { 'input': '$data', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$objectToArray': { '$mergeObjects': [ '$$this.sales', '$$this.ad', '$$this.traffic' ] } } ] } } }, 'as': 'kv', 'in': '$$kv.k' } } }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$sum': { '$map': { 'input': '$data', 'as': 'd', 'in': { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': { '$mergeObjects': [ '$$d.sales', '$$d.ad', '$$d.traffic' ] } } }, 0 ] } } } } } } } } })
        pipeline.extend([group, setData])
        pipeline.extend(dt.addAnalyticKeys())
        replaceRoot = pp.replaceRoot(pp.mergeObjects([ '$data', { 'value': '$_id', 'collatetype': self.options.collatetype.value, 'startdate': self.options.dates.startDate, 'enddate': self.options.dates.endDate, 'reportid': self.reportId } ]))
        merge= pp.merge(CollectionType.DZGRO_REPORT_DATA)
        pipeline.extend([dt.addMissingKeys(), dt.addCalculatedKeysToData(), dt.addValue(), dt.hideKeys(), replaceRoot, merge])
        return pipeline
