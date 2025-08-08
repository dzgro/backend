from typing import List, Optional
from amazonapi.client import BaseClient
from models.amazonapi.adapi.sp.campaigns import (
    SponsoredProductsListSponsoredProductsCampaignsRequestContent,
    SponsoredProductsListSponsoredProductsCampaignsResponseContent,
    SponsoredProductsDeleteSponsoredProductsCampaignsRequestContent,
    SponsoredProductsDeleteSponsoredProductsCampaignsResponseContent,
    SponsoredProductsCreateSponsoredProductsCampaignsRequestContent,
    SponsoredProductsCreateSponsoredProductsCampaignsResponseContent,
    SponsoredProductsUpdateSponsoredProductsCampaignsRequestContent,
    SponsoredProductsUpdateSponsoredProductsCampaignsResponseContent,
)

class SPCampaignsClient(BaseClient):
    """Client for the A+ Content API."""

    async def listCampaigns(
        self, request: SponsoredProductsListSponsoredProductsCampaignsRequestContent
    ) -> SponsoredProductsListSponsoredProductsCampaignsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaigns/list",
            operation="listCampaigns",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsCampaignsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaign.v3+json", "Accept": "application/vnd.spCampaign.v3+json"}
        )

    async def deleteCampaigns(
        self, request: SponsoredProductsDeleteSponsoredProductsCampaignsRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsCampaignsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaigns/delete",
            operation="deleteCampaigns",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsCampaignsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaign.v3+json", "Accept": "application/vnd.spCampaign.v3+json"}
        )

    async def createCampaigns(
        self, request: SponsoredProductsCreateSponsoredProductsCampaignsRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsCampaignsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaigns",
            operation="createCampaigns",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsCampaignsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaign.v3+json", "Accept": "application/vnd.spCampaign.v3+json"}
        )
    
    async def updateCampaigns(
        self, request: SponsoredProductsUpdateSponsoredProductsCampaignsRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsCampaignsResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/campaigns",
            operation="updateCampaigns",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsCampaignsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaign.v3+json", "Accept": "application/vnd.spCampaign.v3+json"}
        )