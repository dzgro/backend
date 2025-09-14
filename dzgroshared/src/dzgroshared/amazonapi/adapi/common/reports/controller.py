from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.amazonapi.adapi.common.reports.model import AdReportRequest, AdReport


class ReportsClient(BaseClient):
    """Client for the Reports API."""

    async def create_report(
        self, request: AdReportRequest
    ) -> AdReport:
        return await self._request(
            method="POST",
            path="/reporting/reports",
            operation="create_report",
            data=request.model_dump(mode="json",exclude_none=True, by_alias=True),
            response_model=AdReport,
            headers={
                "Content-Type": "application/vnd.createAdReportrequest.v3+json",
                "Accept": "application/vnd.createAdReportresponse.v3+json"
            }
        )

    async def get_report(
        self, report_id: str
    ) -> AdReport:
        return await self._request(
            method="GET",
            path=f"/reporting/reports/{report_id}",
            operation="get_report",
            response_model=AdReport,
            headers={
                "Content-Type": "application/vnd.getAdReportresponse.v3+json",
                "Accept": "application/vnd.getAdReportresponse.v3+json"
            }
        )

    async def delete_report(
        self, report_id: str
    ) -> dict:
        return await self._request(
            method="DELETE",
            path=f"/reporting/reports/{report_id}",
            operation="delete_report",
            response_model=dict,
            headers={
                "Content-Type": "application/vnd.deleteAdReportresponse.v3+json",
                "Accept": "application/vnd.deleteAdReportresponse.v3+json"
            }
        )
