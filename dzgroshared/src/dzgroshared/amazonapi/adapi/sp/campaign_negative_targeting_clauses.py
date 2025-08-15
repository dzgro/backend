from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.adapi.sp.campaign_negative_targeting_clauses import (
    SponsoredProductsListSponsoredProductsCampaignNegativeTargetingClausesRequestContent,
    SponsoredProductsListSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
    SponsoredProductsDeleteSponsoredProductsCampaignNegativeTargetingClausesRequestContent,
    SponsoredProductsDeleteSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
    SponsoredProductsCreateSponsoredProductsCampaignNegativeTargetingClausesRequestContent,
    SponsoredProductsCreateSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
    SponsoredProductsUpdateSponsoredProductsCampaignNegativeTargetingClausesRequestContent,
    SponsoredProductsUpdateSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
)

class SPCampaignNegativeTargetingClausesClient(BaseClient):
    """Client for the A+ Content API."""

    async def listCampaignNegativeTargetingClauses(
        self, request: SponsoredProductsListSponsoredProductsCampaignNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsListSponsoredProductsCampaignNegativeTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaignNegativeTargets/list",
            operation="listCampaignNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeTargetingClause.v3+json", "Accept": "application/vnd.spCampaignNegativeTargetingClause.v3+json"}
        )

    async def deleteCampaignNegativeTargetingClauses(
        self, request: SponsoredProductsDeleteSponsoredProductsCampaignNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsCampaignNegativeTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaignNegativeTargets/delete",
            operation="deleteCampaignNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeTargetingClause.v3+json", "Accept": "application/vnd.spCampaignNegativeTargetingClause.v3+json"}
        )

    async def createCampaignNegativeTargetingClauses(
        self, request: SponsoredProductsCreateSponsoredProductsCampaignNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsCampaignNegativeTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaignNegativeTargets",
            operation="createCampaignNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeTargetingClause.v3+json", "Accept": "application/vnd.spCampaignNegativeTargetingClause.v3+json"}
        )
    
    async def updateCampaignNegativeTargetingClauses(
        self, request: SponsoredProductsUpdateSponsoredProductsCampaignNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsCampaignNegativeTargetingClausesResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/campaignNegativeTargets",
            operation="updateCampaignNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsCampaignNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeTargetingClause.v3+json", "Accept": "application/vnd.spCampaignNegativeTargetingClause.v3+json"}
        )