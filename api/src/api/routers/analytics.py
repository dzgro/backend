from api.Util import RequestHelper
from fastapi import APIRouter, Request
from dzgroshared.db.model import AnalyticKeyGroup, SuccessResponse
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get('/keys', response_model=list[AnalyticKeyGroup], response_model_exclude_none=True, response_model_by_alias=False)
async def getAnalyticKeyGroups(request: Request):
    from dzgroshared.analytics import controller
    return controller.getAnalyticsGroups()

@router.post('/', response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def createAnalytics(request: Request):
    client = await RequestHelper(request).client
    dates = (await client.db.marketplaces.getUserMarketplace(client.marketplace.id)).dates
    if dates:
        from dzgroshared.functions.AmazonDailyReport.reports.pipelines.Analytics import AnalyticsProcessor
        await AnalyticsProcessor(client, dates).execute()
        # markeptlacedates = dates.model_copy()
        # from datetime import timedelta
        # dates.startdate = dates.startdate+timedelta(days=30)
        # await AnalyticsProcessor(client, dates, markeptlacedates).execute()
        await client.db.performance_periods.buildQueriesAndResults()
    return SuccessResponse(success=True)


