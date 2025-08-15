from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.spapi.aplus import (
    GetContentDocumentResponse,
    PostContentDocumentRequest,
    PostContentDocumentResponse,
    SearchContentDocumentsResponse,
)

class AplusClient(BaseClient):
    """Client for the A+ Content API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_content_document(
        self, content_reference_key: str, marketplace_id: str, included_data_set: List[str]
    ) -> GetContentDocumentResponse:
        params = {"marketplaceId": marketplace_id, "includedDataSet": ",".join(included_data_set)}
        return await self._request(
            method="GET",
            path=f"/aplus/2020-11-01/contentDocuments/{content_reference_key}",
            operation="getContentDocument",
            params=params,
            response_model=GetContentDocumentResponse,
        )

    async def create_content_document(
        self, marketplace_id: str, content_document: PostContentDocumentRequest
    ) -> PostContentDocumentResponse:
        params = {"marketplaceId": marketplace_id}
        return await self._request(
            method="POST",
            path="/aplus/2020-11-01/contentDocuments",
            operation="createContentDocument",
            params=params,
            data=content_document.dict(),
            response_model=PostContentDocumentResponse,
        )

    async def update_content_document(
        self, content_reference_key: str, marketplace_id: str, content_document: PostContentDocumentRequest
    ) -> PostContentDocumentResponse:
        params = {"marketplaceId": marketplace_id}
        return await self._request(
            method="POST",
            path=f"/aplus/2020-11-01/contentDocuments/{content_reference_key}",
            operation="updateContentDocument",
            params=params,
            data=content_document.dict(),
            response_model=PostContentDocumentResponse,
        )

    async def search_content_documents(
        self, marketplace_id: str, page_token: Optional[str] = None
    ) -> SearchContentDocumentsResponse:
        params = {"marketplaceId": marketplace_id}
        if page_token:
            params["pageToken"] = page_token
        return await self._request(
            method="GET",
            path="/aplus/2020-11-01/contentDocuments",
            operation="searchContentDocuments",
            params=params,
            response_model=SearchContentDocumentsResponse,
        ) 