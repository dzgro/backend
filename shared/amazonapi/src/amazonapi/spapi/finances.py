from datetime import datetime
from typing import List, Optional, Dict, Any
from amazonapi.client import BaseClient
from models.amazonapi.spapi.finances import ListTransactionsResponse, TransactionsPayload, Transaction, ErrorList

class FinancesClient(BaseClient):
    """Client for the Finances API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def list_financial_event_groups(
        self, max_results_per_page: Optional[int] = None, financial_event_group_started_before: Optional[datetime] = None, financial_event_group_started_after: Optional[datetime] = None, next_token: Optional[str] = None
    ) -> ListTransactionsResponse:
        params = {}
        if max_results_per_page:
            params["MaxResultsPerPage"] = max_results_per_page
        if financial_event_group_started_before:
            params["FinancialEventGroupStartedBefore"] = financial_event_group_started_before.isoformat()
        if financial_event_group_started_after:
            params["FinancialEventGroupStartedAfter"] = financial_event_group_started_after.isoformat()
        if next_token:
            params["NextToken"] = next_token
        return await self._request(
            method="GET",
            path="/finances/v0/financialEventGroups",
            operation="listFinancialEventGroups",
            params=params,
            response_model=ListTransactionsResponse,
        )

    async def list_financial_events_by_group_id(
        self, event_group_id: str, max_results_per_page: Optional[int] = None, posted_before: Optional[datetime] = None, posted_after: Optional[datetime] = None, next_token: Optional[str] = None
    ) -> ListTransactionsResponse:
        params = {}
        if max_results_per_page:
            params["MaxResultsPerPage"] = max_results_per_page
        if posted_before:
            params["PostedBefore"] = posted_before.isoformat()
        if posted_after:
            params["PostedAfter"] = posted_after.isoformat()
        if next_token:
            params["NextToken"] = next_token
        return await self._request(
            method="GET",
            path=f"/finances/v0/financialEventGroups/{event_group_id}/financialEvents",
            operation="listFinancialEventsByGroupId",
            params=params,
            response_model=ListTransactionsResponse,
        )

    async def list_financial_events_by_order_id(
        self, order_id: str, max_results_per_page: Optional[int] = None, next_token: Optional[str] = None
    ) -> ListTransactionsResponse:
        params = {}
        if max_results_per_page:
            params["MaxResultsPerPage"] = max_results_per_page
        if next_token:
            params["NextToken"] = next_token
        return await self._request(
            method="GET",
            path=f"/finances/v0/orders/{order_id}/financialEvents",
            operation="listFinancialEventsByOrderId",
            params=params,
            response_model=ListTransactionsResponse,
        ) 