from amazonapi.client import BaseClient
from models.amazonapi.spapi.datakiosk import (
    DataKioskCreateQueryRequest, DataKioskCreateQueryResponse, GetQueriesResponse, DataKioskQueryResponse, DataKioskDocumentResponse
    
)
from typing import Optional

class DataKioskClient(BaseClient):
    """Client for the Amazon Data Kiosk API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def create_query(self, request: DataKioskCreateQueryRequest) -> DataKioskCreateQueryResponse:
        return await self._request(
            method="POST",
            path="/dataKiosk/2023-11-15/queries",
            operation="createQuery",
            data=request.body.model_dump(exclude_none=True),
            response_model=DataKioskCreateQueryResponse,
        )

    async def get_query(self, query_id: str) -> DataKioskQueryResponse:
        return await self._request(
            method="GET",
            path=f"/dataKiosk/2023-11-15/queries/{query_id}",
            operation="getQuery",
            response_model=DataKioskQueryResponse,
        )

    async def list_queries(self, next_token: Optional[str] = None) -> GetQueriesResponse:
        params = {"nextToken": next_token} if next_token else None
        return await self._request(
            method="GET",
            path="/dataKiosk/2023-11-15/queries",
            operation="listQueries",
            params=params,
            response_model=GetQueriesResponse,
        )


    async def get_query_result_document(self, result_document_id: str) -> DataKioskDocumentResponse:
        return await self._request(
            method="GET",
            path=f"/dataKiosk/2023-11-15/documents/{result_document_id}",
            operation="getQueryResultDocument",
            response_model=DataKioskDocumentResponse,
        )