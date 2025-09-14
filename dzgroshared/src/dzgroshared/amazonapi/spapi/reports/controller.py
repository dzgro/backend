from datetime import datetime
from typing import List, Optional, Dict, Any, Type

from pydantic import BaseModel
from dzgroshared.amazonapi.client import BaseClient
from .model import (
    SPAPIGetReportsResponse, SPAPICreateReportResponse, SPAPIReport, SPAPIReportDocument,
    SPAPICreateReportSpecification
)

class ReportsClient(BaseClient):
    """Client for the Reports API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_reports(
        self, report_types: Optional[List[str]] = None, processing_statuses: Optional[List[str]] = None, marketplace_ids: Optional[List[str]] = None, page_size: Optional[int] = None, created_since: Optional[datetime] = None, created_until: Optional[datetime] = None, next_token: Optional[str] = None
    ) -> SPAPIGetReportsResponse:
        params = {}
        if next_token:
            params["nextToken"] = next_token
        else:
            if report_types:
                params["reportTypes"] = ",".join(report_types)
            if processing_statuses:
                params["processingStatuses"] = ",".join(processing_statuses)
            if marketplace_ids:
                params["marketplaceIds"] = ",".join(marketplace_ids)
            if page_size:
                params["pageSize"] = page_size
            if created_since:
                params["createdSince"] = created_since.isoformat()
            if created_until:
                params["createdUntil"] = created_until.isoformat()

        return await self._request(
            method="GET",
            path="/reports/2021-06-30/reports",
            operation="getReports",
            params=params,
            response_model=SPAPIGetReportsResponse,
        )

    async def create_report(self, body: SPAPICreateReportSpecification) -> SPAPICreateReportResponse:
        data = body.model_dump(exclude_none=True, by_alias=True)
        if 'dataStartTime'  in data: data['dataStartTime'] = data['dataStartTime'].isoformat()
        if 'dataEndTime' in data: data['dataEndTime'] = data['dataEndTime'].isoformat()
        return await self._request(
            method="POST",
            path="/reports/2021-06-30/reports",
            operation="createReport",
            data=data,
            response_model=SPAPICreateReportResponse,
        )

    async def get_report(self, report_id: str) -> SPAPIReport:
        return await self._request(
            method="GET",
            path=f"/reports/2021-06-30/reports/{report_id}",
            operation="getReport",
            response_model=SPAPIReport,
        )

    async def cancel_report(self, report_id: str) -> None:
        await self._request(
            method="DELETE",
            path=f"/reports/2021-06-30/reports/{report_id}",
            operation="cancelReport",
            response_model=BaseModel,
        )

    async def get_report_document(self, report_document_id: str) -> SPAPIReportDocument:
        return await self._request(
            method="GET",
            path=f"/reports/2021-06-30/documents/{report_document_id}",
            operation="getReportDocument",
            response_model=SPAPIReportDocument,
        ) 