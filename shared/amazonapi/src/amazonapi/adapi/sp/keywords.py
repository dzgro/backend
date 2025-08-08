from typing import List, Optional
from amazonapi.client import BaseClient
from models.amazonapi.adapi.sp.keywords import (
    SponsoredProductsListSponsoredProductsKeywordsRequestContent,
    SponsoredProductsListSponsoredProductsKeywordsResponseContent,
    SponsoredProductsDeleteSponsoredProductsKeywordsRequestContent,
    SponsoredProductsDeleteSponsoredProductsKeywordsResponseContent,
    SponsoredProductsCreateSponsoredProductsKeywordsRequestContent,
    SponsoredProductsCreateSponsoredProductsKeywordsResponseContent,
    SponsoredProductsUpdateSponsoredProductsKeywordsRequestContent,
    SponsoredProductsUpdateSponsoredProductsKeywordsResponseContent,
)

class SPKeywordsClient(BaseClient):
    """Client for the A+ Content API."""

    async def listKeywords(
        self, request: SponsoredProductsListSponsoredProductsKeywordsRequestContent
    ) -> SponsoredProductsListSponsoredProductsKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/keywords/list",
            operation="listKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spKeyword.v3+json", "Accept": "application/vnd.spKeyword.v3+json"}
        )

    async def deleteKeywords(
        self, request: SponsoredProductsDeleteSponsoredProductsKeywordsRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/keywords/delete",
            operation="deleteKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spKeyword.v3+json", "Accept": "application/vnd.spKeyword.v3+json"}
        )

    async def createKeywords(
        self, request: SponsoredProductsCreateSponsoredProductsKeywordsRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsKeywordsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/keywords",
            operation="createKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spKeyword.v3+json", "Accept": "application/vnd.spKeyword.v3+json"}
        )
    
    async def updateKeywords(
        self, request: SponsoredProductsUpdateSponsoredProductsKeywordsRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsKeywordsResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/keywords",
            operation="updateKeywords",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsKeywordsResponseContent,
            headers={"Content-Type": "application/vnd.spKeyword.v3+json", "Accept": "application/vnd.spKeyword.v3+json"}
        )