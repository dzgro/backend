from amazonapi.client import BaseClient
from models.amazonapi.spapi.datakiosk import (
    CreateQueryRequest, CreateQueryResponse,
    GetQueryResponse, ListQueriesResponse, CancelQueryResponse,
    GetQueryResultResponse, GetQueryResultDocumentResponse,
    GetSchemaResponse, ListSchemasResponse
)
from typing import Optional

class DataKioskClient(BaseClient):
    """Client for the Amazon Data Kiosk API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def create_query(self, request: CreateQueryRequest) -> CreateQueryResponse:
        return await self._request(
            method="POST",
            path="/dataKiosk/2023-11-15/queries",
            operation="createQuery",
            data=request.model_dump(by_alias=True),
            response_model=CreateQueryResponse,
        )

    async def get_query(self, query_id: str) -> GetQueryResponse:
        return await self._request(
            method="GET",
            path=f"/dataKiosk/2023-11-15/queries/{query_id}",
            operation="getQuery",
            response_model=GetQueryResponse,
        )

    async def list_queries(self, next_token: Optional[str] = None) -> ListQueriesResponse:
        params = {"nextToken": next_token} if next_token else None
        return await self._request(
            method="GET",
            path="/dataKiosk/2023-11-15/queries",
            operation="listQueries",
            params=params,
            response_model=ListQueriesResponse,
        )

    async def cancel_query(self, query_id: str) -> CancelQueryResponse:
        return await self._request(
            method="POST",
            path=f"/dataKiosk/2023-11-15/queries/{query_id}/cancel",
            operation="cancelQuery",
            response_model=CancelQueryResponse,
        )

    async def get_query_result(self, query_id: str) -> GetQueryResultResponse:
        return await self._request(
            method="GET",
            path=f"/dataKiosk/2023-11-15/queries/{query_id}/result",
            operation="getQueryResult",
            response_model=GetQueryResultResponse,
        )

    async def get_query_result_document(self, result_document_id: str) -> GetQueryResultDocumentResponse:
        return await self._request(
            method="GET",
            path=f"/dataKiosk/2023-11-15/resultDocuments/{result_document_id}",
            operation="getQueryResultDocument",
            response_model=GetQueryResultDocumentResponse,
        )

    async def get_schema(self, schema_name: str) -> GetSchemaResponse:
        return await self._request(
            method="GET",
            path=f"/dataKiosk/2023-11-15/schemas/{schema_name}",
            operation="getSchema",
            response_model=GetSchemaResponse,
        )

    async def list_schemas(self, next_token: Optional[str] = None) -> ListSchemasResponse:
        params = {"nextToken": next_token} if next_token else None
        return await self._request(
            method="GET",
            path="/dataKiosk/2023-11-15/schemas",
            operation="listSchemas",
            params=params,
            response_model=ListSchemasResponse,
        ) 