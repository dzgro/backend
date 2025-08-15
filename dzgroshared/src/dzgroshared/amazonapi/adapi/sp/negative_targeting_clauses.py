from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.adapi.sp.negative_targeting_clauses import (
    SponsoredProductsListSponsoredProductsNegativeTargetingClausesRequestContent,
    SponsoredProductsListSponsoredProductsNegativeTargetingClausesResponseContent,
    SponsoredProductsDeleteSponsoredProductsNegativeTargetingClausesRequestContent,
    SponsoredProductsDeleteSponsoredProductsNegativeTargetingClausesResponseContent,
    SponsoredProductsCreateSponsoredProductsNegativeTargetingClausesRequestContent,
    SponsoredProductsCreateSponsoredProductsNegativeTargetingClausesResponseContent,
    SponsoredProductsUpdateSponsoredProductsNegativeTargetingClausesRequestContent,
    SponsoredProductsUpdateSponsoredProductsNegativeTargetingClausesResponseContent,
)

class SPNegativeTargetingClausesClient(BaseClient):
    """Client for the A+ Content API."""

    async def listNegativeTargetingClauses(
        self, request: SponsoredProductsListSponsoredProductsNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsListSponsoredProductsNegativeTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/negativeTargets/list",
            operation="listNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeTargetingClause.v3+json", "Accept": "application/vnd.spNegativeTargetingClause.v3+json"}
        )

    async def deleteNegativeTargetingClauses(
        self, request: SponsoredProductsDeleteSponsoredProductsNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsNegativeTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/negativeTargets/delete",
            operation="deleteNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeTargetingClause.v3+json", "Accept": "application/vnd.spNegativeTargetingClause.v3+json"}
        )

    async def createNegativeTargetingClauses(
        self, request: SponsoredProductsCreateSponsoredProductsNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsNegativeTargetingClausesResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/negativeTargets",
            operation="createNegativeTargetingClauses",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeTargetingClause.v3+json", "Accept": "application/vnd.spNegativeTargetingClause.v3+json"}
        )
    
    async def updateNegativeTargetingClauses(
        self, request: SponsoredProductsUpdateSponsoredProductsNegativeTargetingClausesRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsNegativeTargetingClausesResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/targets",
            operation="negativeTargets",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsNegativeTargetingClausesResponseContent,
            headers={"Content-Type": "application/vnd.spNegativeTargetingClause.v3+json", "Accept": "application/vnd.spNegativeTargetingClause.v3+json"}
        )