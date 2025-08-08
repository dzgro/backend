from typing import List, Optional
from amazonapi.client import BaseClient
from models.amazonapi.adapi.sp.targeting_clauses import (
    SponsoredProductsListSponsoredProductsTargetingClausesRequestContent,
    SponsoredProductsListSponsoredProductsTargetingClausesResponseContent,
    SponsoredProductsDeleteSponsoredProductsTargetingClausesRequestContent,
    SponsoredProductsDeleteSponsoredProductsTargetingClausesResponseContent,
    SponsoredProductsCreateSponsoredProductsTargetingClausesRequestContent,
    SponsoredProductsCreateSponsoredProductsTargetingClausesResponseContent,
    SponsoredProductsUpdateSponsoredProductsTargetingClausesRequestContent,
    SponsoredProductsUpdateSponsoredProductsTargetingClausesResponseContent,
)

class SPTargetingClausesClient(BaseClient):
    """Client for the A+ Content API."""

    async def listTargetingClauses(
        self, request: SponsoredProductsListSponsoredProductsTargetingClausesRequestContent
    ) -> SponsoredProductsListSponsoredProductsTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/targets/list",
            operation="listTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spTargetingClause.v3+json", "Accept": "application/vnd.spTargetingClause.v3+json"}
        )

    async def deleteTargetingClauses(
        self, request: SponsoredProductsDeleteSponsoredProductsTargetingClausesRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/targets/delete",
            operation="deleteTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spTargetingClause.v3+json", "Accept": "application/vnd.spTargetingClause.v3+json"}
        )

    async def createTargetingClauses(
        self, request: SponsoredProductsCreateSponsoredProductsTargetingClausesRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/targets",
            operation="createTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spTargetingClause.v3+json", "Accept": "application/vnd.spTargetingClause.v3+json"}
        )
    
    async def updateTargetingClauses(
        self, request: SponsoredProductsUpdateSponsoredProductsTargetingClausesRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsTargetingClausesResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/targets",
            operation="updateTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spTargetingClause.v3+json", "Accept": "application/vnd.spTargetingClause.v3+json"}
        )