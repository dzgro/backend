from fastapi import APIRouter, Request
from dzgroshared.db.model import AnalyticKeyGroup
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get('/keys', response_model=list[AnalyticKeyGroup], response_model_exclude_none=True, response_model_by_alias=False)
async def getAnalyticKeyGroups(request: Request):
    from dzgroshared.analytics import controller
    return controller.getAnalyticsGroups()

