from dzgroshared.models.amazonapi.adapi.common.exports import ExportRequest, ExportResponse
from dzgroshared.amazonapi.client import BaseClient

class ExportsClient(BaseClient):
    """Client for the Amazon Ads API Exports."""

    async def export_ads(
        self, request: ExportRequest
    ) -> ExportResponse:
        return await self._request(
            method="POST",
            path="/ads/export",
            operation="export_ads",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.adsexport.v1+json",
                "Accept": "application/vnd.adsexport.v1+json"
            }
        )

    async def export_campaigns(
        self, request: ExportRequest
    ) -> ExportResponse:
        return await self._request(
            method="POST",
            path="/campaigns/export",
            operation="export_campaigns",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.campaignsexport.v1+json",
                "Accept": "application/vnd.campaignsexport.v1+json"
            }
        )

    async def export_ad_groups(
        self, request: ExportRequest
    ) -> ExportResponse:
        return await self._request(
            method="POST",
            path="/adGroups/export",
            operation="export_ad_groups",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.adgroupsexport.v1+json",
                "Accept": "application/vnd.adgroupsexport.v1+json"
            }
        )

    async def export_targets(
        self, request: ExportRequest
    ) -> ExportResponse:
        return await self._request(
            method="POST",
            path="/targets/export",
            operation="export_targets",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.targetsexport.v1+json",
                "Accept": "application/vnd.targetsexport.v1+json"
            }
        )

    async def get_campaign_export_status(
        self, export_id: str
    ) -> ExportResponse:
        return await self._request(
            method="GET",
            path=f"/exports/{export_id}",
            operation="get_campaign_export_status",
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.campaignsexport.v1+json",
                "Accept": "application/vnd.campaignsexport.v1+json"
            }
        )

    async def get_adgroup_export_status(
        self, export_id: str
    ) -> ExportResponse:
        return await self._request(
            method="GET",
            path=f"/exports/{export_id}",
            operation="get_adgroup_export_status",
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.adgroupsexport.v1+json",
                "Accept": "application/vnd.adgroupsexport.v1+json"
            }
        )

    async def get_ads_export_status(
        self, export_id: str
    ) -> ExportResponse:
        return await self._request(
            method="GET",
            path=f"/exports/{export_id}",
            operation="get_ads_export_status",
            response_model=ExportResponse,
            headers={
                "Content-Type": "application/vnd.adsexport.v1+json",
                "Accept": "application/vnd.adsexport.v1+json"
            }
        )

    async def get_targets_export_status(
        self, export_id: str
    ) -> ExportResponse:
        return await self._request(
            method="GET",
            path=f"/exports/{export_id}",
            operation="get_targets_export_status",
            response_model=ExportResponse,
            headers={
                "Accept": "application/vnd.targetsexport.v1+json",
                "Content-Type": "application/vnd.targetsexport.v1+json"
            }
        )
