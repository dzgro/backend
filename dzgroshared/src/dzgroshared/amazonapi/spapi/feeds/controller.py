from datetime import datetime
from typing import List, Optional, Dict, Any
from dzgroshared.amazonapi.client import BaseClient
from .model import (
    FeedOptions,
    CreateFeedSpecification,
    CreateFeedDocumentSpecification,
    CreateFeedResponse,
    CreateFeedDocumentResponse,
    GetFeedsResponse,
    Feed,
    FeedDocument,
)

class FeedsClient(BaseClient):
    """Client for the Feeds API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_feeds(
        self, feed_types: Optional[List[str]] = None, marketplace_ids: Optional[List[str]] = None, page_size: Optional[int] = None, processing_statuses: Optional[List[str]] = None, created_since: Optional[datetime] = None, created_until: Optional[datetime] = None, next_token: Optional[str] = None
    ) -> GetFeedsResponse:
        params = {}
        if feed_types:
            params["feedTypes"] = ",".join(feed_types)
        if marketplace_ids:
            params["marketplaceIds"] = ",".join(marketplace_ids)
        if page_size:
            params["pageSize"] = page_size
        if processing_statuses:
            params["processingStatuses"] = ",".join(processing_statuses)
        if created_since:
            params["createdSince"] = created_since.isoformat()
        if created_until:
            params["createdUntil"] = created_until.isoformat()
        if next_token:
            params["nextToken"] = next_token
        return await self._request(
            method="GET",
            path="/feeds/2021-06-30/feeds",
            operation="getFeeds",
            params=params,
            response_model=GetFeedsResponse,
        )

    async def create_feed(self, feed: CreateFeedSpecification) -> CreateFeedResponse:
        return await self._request(
            method="POST",
            path="/feeds/2021-06-30/feeds",
            operation="createFeed",
            data=feed.dict(),
            response_model=CreateFeedResponse,
        )

    async def get_feed(self, feed_id: str) -> Feed:
        return await self._request(
            method="GET",
            path=f"/feeds/2021-06-30/feeds/{feed_id}",
            operation="getFeed",
            response_model=Feed,
        )

    async def create_feed_document(self, doc: CreateFeedDocumentSpecification) -> CreateFeedDocumentResponse:
        return await self._request(
            method="POST",
            path="/feeds/2021-06-30/documents",
            operation="createFeedDocument",
            data=doc.dict(),
            response_model=CreateFeedDocumentResponse,
        )

    async def get_feed_document(self, feed_document_id: str) -> FeedDocument:
        return await self._request(
            method="GET",
            path=f"/feeds/2021-06-30/documents/{feed_document_id}",
            operation="getFeedDocument",
            response_model=FeedDocument,
        ) 