from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from .model import (
    SponsoredProductsListSponsoredProductsNegativeKeywordsRequestContent,
    SponsoredProductsListSponsoredProductsNegativeKeywordsResponseContent,
    SponsoredProductsDeleteSponsoredProductsNegativeKeywordsRequestContent,
    SponsoredProductsDeleteSponsoredProductsNegativeKeywordsResponseContent,
    SponsoredProductsCreateSponsoredProductsNegativeKeywordsRequestContent,
    SponsoredProductsCreateSponsoredProductsNegativeKeywordsResponseContent,
    SponsoredProductsUpdateSponsoredProductsNegativeKeywordsRequestContent,
    SponsoredProductsUpdateSponsoredProductsNegativeKeywordsResponseContent,
)

class SPNegativeKeywordsClient(BaseClient):
    """Client for the A+ Content API."""

    async def listNegativeKeywords(
        self, request: SponsoredProductsListSponsoredProductsNegativeKeywordsRequestContent
    ) -> SponsoredProductsListSponsoredProductsNegativeKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/negativeKeywords/list",
            operation="listNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeKeyword.v3+json", "Accept": "application/vnd.spNegativeKeyword.v3+json"}
        )

    async def deleteNegativeKeywords(
        self, request: SponsoredProductsDeleteSponsoredProductsNegativeKeywordsRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsNegativeKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/negativeKeywords/delete",
            operation="deleteNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeKeyword.v3+json", "Accept": "application/vnd.spNegativeKeyword.v3+json"}
        )

    async def createNegativeKeywords(
        self, request: SponsoredProductsCreateSponsoredProductsNegativeKeywordsRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsNegativeKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/negativeKeywords",
            operation="createNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeKeyword.v3+json", "Accept": "application/vnd.spNegativeKeyword.v3+json"}
        )
    
    async def updateNegativeKeywords(
        self, request: SponsoredProductsUpdateSponsoredProductsNegativeKeywordsRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsNegativeKeywordsResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/negativeKeywords",
            operation="updateNegativeKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsNegativeKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeKeyword.v3+json", "Accept": "application/vnd.spNegativeKeyword.v3+json"}
        )