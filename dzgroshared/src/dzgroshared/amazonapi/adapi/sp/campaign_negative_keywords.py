from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.adapi.sp.campaign_negative_keywords import (
    SponsoredProductsListSponsoredProductsCampaignNegativeKeywordsRequestContent,
    SponsoredProductsListSponsoredProductsCampaignNegativeKeywordsResponseContent,
    SponsoredProductsDeleteSponsoredProductsCampaignNegativeKeywordsRequestContent,
    SponsoredProductsDeleteSponsoredProductsCampaignNegativeKeywordsResponseContent,
    SponsoredProductsCreateSponsoredProductsCampaignNegativeKeywordsRequestContent,
    SponsoredProductsCreateSponsoredProductsCampaignNegativeKeywordsResponseContent,
    SponsoredProductsUpdateSponsoredProductsCampaignNegativeKeywordsRequestContent,
    SponsoredProductsUpdateSponsoredProductsCampaignNegativeKeywordsResponseContent,
)

class SPCampaignNegativeKeywordsClient(BaseClient):
    """Client for the A+ Content API."""

    async def listCampaignNegativeKeywords(
        self, request: SponsoredProductsListSponsoredProductsCampaignNegativeKeywordsRequestContent
    ) -> SponsoredProductsListSponsoredProductsCampaignNegativeKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaignNegativeTargets/list",
            operation="listCampaignNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsCampaignNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeKeyword.v3+json", "Accept": "application/vnd.spCampaignNegativeKeyword.v3+json"}
        )

    async def deleteCampaignNegativeKeywords(
        self, request: SponsoredProductsDeleteSponsoredProductsCampaignNegativeKeywordsRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsCampaignNegativeKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaignNegativeTargets/delete",
            operation="deleteCampaignNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsCampaignNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeKeyword.v3+json", "Accept": "application/vnd.spCampaignNegativeKeyword.v3+json"}
        )

    async def createCampaignNegativeKeywords(
        self, request: SponsoredProductsCreateSponsoredProductsCampaignNegativeKeywordsRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsCampaignNegativeKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/campaignNegativeTargets",
            operation="createCampaignNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsCampaignNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeKeyword.v3+json", "Accept": "application/vnd.spCampaignNegativeKeyword.v3+json"}
        )
    
    async def updateCampaignNegativeKeywords(
        self, request: SponsoredProductsUpdateSponsoredProductsCampaignNegativeKeywordsRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsCampaignNegativeKeywordsResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/campaignNegativeTargets",
            operation="updateCampaignNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsCampaignNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spCampaignNegativeKeyword.v3+json", "Accept": "application/vnd.spCampaignNegativeKeyword.v3+json"}
        )