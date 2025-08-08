from typing import List, Optional
from amazonapi.client import BaseClient
from models.amazonapi.adapi.common.portfolios import ListPortfoliosRequestContent, ListPortfoliosResponseContent, CreatePortfoliosRequestContent, CreatePortfoliosResponseContent, UpdatePortfoliosRequestContent, UpdatePortfoliosResponseContent


class PortfoliosClient(BaseClient):
    """Client for the Portfolios API."""

    async def list_portfolios(
        self, request: ListPortfoliosRequestContent
    ) -> ListPortfoliosResponseContent:
        return await self._request(
            method="POST",
            path="/portfolios/list",
            operation="list_portfolios",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=ListPortfoliosResponseContent,
            headers={
                "Content-Type": "application/vnd.spPortfolio.v3+json",
                "Accept": "application/vnd.spPortfolio.v3+json"
            }
        )
    
    async def create_portfolios(
        self, request: CreatePortfoliosRequestContent
    ) -> CreatePortfoliosResponseContent:
        return await self._request(
            method="POST",
            path="/portfolios",
            operation="create_portfolios",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=CreatePortfoliosResponseContent,
            headers={
                "Content-Type": "application/vnd.spPortfolio.v3+json",
                "Accept": "application/vnd.spPortfolio.v3+json"
            }
        )
    
    async def update_portfolios(
        self, request: UpdatePortfoliosRequestContent
    ) -> UpdatePortfoliosResponseContent:
        return await self._request(
            method="PUT",
            path="/portfolios",
            operation="update_portfolios",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=UpdatePortfoliosResponseContent,
            headers={
                "Content-Type": "application/vnd.spPortfolio.v3+json",
                "Accept": "application/vnd.spPortfolio.v3+json"
            }
        )
    


    