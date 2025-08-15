from typing import List, Optional

from dzgroshared.models.amazonapi.adapi.common.ams import CreateStreamSubscriptionRequest, CreateStreamSubscriptionResponse, GetStreamSubscriptionResponse, UpdateStreamSubscriptionResponse, ListStreamSubscriptionsRequest, ListStreamSubscriptionsResponse
from dzgroshared.amazonapi.client import BaseClient

class AMSClient(BaseClient):
    """Client for the AMS API."""

    async def createStreamSubscription(
        self, req: CreateStreamSubscriptionRequest
    ) -> CreateStreamSubscriptionResponse:
        return await self._request(
            method="POST",
            path=f"/streams/subscriptions",
            operation="createStreamSubscription",
            data={
                "clientRequestToken": req.clientRequestToken,
                "dataSetId": req.dataSetId.value,
                "destinationArn": req.queueARN,
            },
            response_model=CreateStreamSubscriptionResponse,
            headers={"Content-Type": "application/vnd.amazonmarketingstreamsubscriptions.v1+json", "Accept": "application/vnd.amazonmarketingstreamsubscriptions.v1+json"}
        )

    async def getStreamSubscription(
        self, subscriptionId:str
    ) -> CreateStreamSubscriptionResponse:
        return await self._request(
            method="GET",
            path=f"/streams/subscriptions/{subscriptionId}",
            operation="getStreamSubscription",
            response_model=GetStreamSubscriptionResponse,
            headers={"Content-Type": "application/vnd.amazonmarketingstreamsubscriptions.v1+json", "Accept": "application/vnd.amazonmarketingstreamsubscriptions.v1+json"}
        )

    async def updateStreamSubscription(
        self, subscriptionId:str
    ) -> CreateStreamSubscriptionResponse:
        return await self._request(
            method="PUT",
            path=f"/streams/subscriptions/{subscriptionId}",
            operation="updateStreamSubscription",
            data={
                "status": "ARCHIVED"
            },
            response_model=UpdateStreamSubscriptionResponse,
            headers={"Content-Type": "application/vnd.amazonmarketingstreamsubscriptions.v1+json", "Accept": "application/vnd.amazonmarketingstreamsubscriptions.v1+json"}
        )
    
    async def listStreamSubscription(
        self, req:ListStreamSubscriptionsRequest
    ) -> ListStreamSubscriptionsResponse:
        return await self._request(
            method="GET",
            path=f"/streams/subscriptions",
            operation="listStreamSubscriptions",
            params=req.model_dump(exclude_none=True, by_alias=True),
            response_model=ListStreamSubscriptionsResponse,
            headers={"Content-Type": "application/vnd.amazonmarketingstreamsubscriptions.v1+json", "Accept": "application/vnd.amazonmarketingstreamsubscriptions.v1+json"}
        )
