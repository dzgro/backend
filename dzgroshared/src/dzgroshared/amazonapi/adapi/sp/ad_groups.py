from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.adapi.sp.ad_groups import (
    SponsoredProductsListSponsoredProductsAdGroupsRequestContent,
    SponsoredProductsListSponsoredProductsAdGroupsResponseContent,
    SponsoredProductsDeleteSponsoredProductsAdGroupsRequestContent,
    SponsoredProductsDeleteSponsoredProductsAdGroupsResponseContent,
    SponsoredProductsCreateSponsoredProductsAdGroupsRequestContent,
    SponsoredProductsCreateSponsoredProductsAdGroupsResponseContent,
    SponsoredProductsUpdateSponsoredProductsAdGroupsRequestContent,
    SponsoredProductsUpdateSponsoredProductsAdGroupsResponseContent,
)

class SPAdGroupsClient(BaseClient):
    """Client for the A+ Content API."""

    async def listAdGroups(
        self, request: SponsoredProductsListSponsoredProductsAdGroupsRequestContent
    ) -> SponsoredProductsListSponsoredProductsAdGroupsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/adGroups/list",
            operation="listAdGroups",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsAdGroupsResponseContent,
            headers={"Content-Type": "application/vnd.spAdGroup.v3+json", "Accept": "application/vnd.spAdGroup.v3+json"}
        )

    async def deleteAdGroups(
        self, request: SponsoredProductsDeleteSponsoredProductsAdGroupsRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsAdGroupsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/adGroups/delete",
            operation="deleteAdGroups",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsAdGroupsResponseContent,
            headers={"Content-Type": "application/vnd.spAdGroup.v3+json", "Accept": "application/vnd.spAdGroup.v3+json"}
        )

    async def createAdGroups(
        self, request: SponsoredProductsCreateSponsoredProductsAdGroupsRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsAdGroupsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/adGroups",
            operation="createAdGroups",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsAdGroupsResponseContent,
            headers={"Content-Type": "application/vnd.spAdGroup.v3+json", "Accept": "application/vnd.spAdGroup.v3+json"}
        )
    
    async def updateAdGroups(
        self, request: SponsoredProductsUpdateSponsoredProductsAdGroupsRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsAdGroupsResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/adGroups",
            operation="updateAdGroups",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsAdGroupsResponseContent,
            headers={"Content-Type": "application/vnd.spAdGroup.v3+json", "Accept": "application/vnd.spAdGroup.v3+json"}
        )