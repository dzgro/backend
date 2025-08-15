from typing import Any, Dict, Optional
import httpx
from razorpay.error import razorpay_error_wrapper
from dzgroshared.models.razorpay.plan import Plan, CreatePlan

class RazorpayPlanHelper:

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.base_url = "https://api.razorpay.com/v1"

    @razorpay_error_wrapper
    async def create_plan(self, data: CreatePlan) -> Plan:
        response = await self.client.post(f"{self.base_url}/plans", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return Plan(**response.json())

    @razorpay_error_wrapper
    async def fetch_plan(self, plan_id: str) -> Plan:
        response = await self.client.get(f"{self.base_url}/plans/{plan_id}")
        response.raise_for_status()
        return Plan(**response.json())

    @razorpay_error_wrapper
    async def fetch_all_plans(self, params: Optional[Dict[str, Any]] = None) -> list[Plan]:
        response = await self.client.get(f"{self.base_url}/plans", params=params)
        response.raise_for_status()
        return [Plan(**item) for item in response.json().get("items", [])]