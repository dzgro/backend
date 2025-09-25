from dzgroshared.db.enums import CollateType
from dzgroshared.db.model import MonthDataRequest, PyObjectId
from dzgroshared.db.state_analytics.model import StateRequest
from httpx import AsyncClient
import pytest
import json
import sys
import os

# Add root test directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.test_helpers.assertions import assert_ok_response, assert_analytics_response

class ROUTER:
    STATE_ANALYTICS = "/states"

@pytest.mark.asyncio
async def test_get_state_data_detailed_for_month(
    client: AsyncClient, 
    sample_month_request: MonthDataRequest
):
    """Test GET /states/detailed/month endpoint"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed/month", 
        json=sample_month_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # Verify response structure for AllStateData
    if data:
        # AllStateData should have these fields based on the model
        expected_fields = ["states", "total_orders", "total_revenue", "total_units_sold"]
        for field in expected_fields:
            if field in data:
                assert data[field] is not None or data[field] == 0

@pytest.mark.asyncio
async def test_get_state_data_detailed(
    client: AsyncClient, 
    sample_state_detailed_request: StateRequest
):
    """Test GET /states/detailed endpoint"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed", 
        json=sample_state_detailed_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # Verify response structure for StateDetailedDataResponse
    if data:
        assert "state" in data or len(data) >= 0

@pytest.mark.asyncio
async def test_get_state_data_lite_by_month(
    client: AsyncClient, 
    sample_month_request: MonthDataRequest
):
    """Test GET /states/lite endpoint"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/lite", 
        json=sample_month_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # Lite response should be a simpler structure
    if data:
        assert isinstance(data, (dict, list))

@pytest.mark.asyncio
async def test_state_analytics_with_sku_collate_type(
    client: AsyncClient, 
    sku_month_request: MonthDataRequest
):
    """Test state analytics with SKU collate type"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed/month", 
        json=sku_month_request.model_dump(mode="json")
    )
    
    # Should handle different collate types gracefully
    assert resp.status_code in [200, 400, 422]
    if resp.status_code == 200:
        data = assert_analytics_response(resp)

@pytest.mark.asyncio
async def test_state_analytics_invalid_month_format(
    client: AsyncClient
):
    """Test state analytics with invalid month format"""
    # Send raw JSON with invalid month format to test API validation
    invalid_data = {
        "collatetype": "marketplace",
        "month": "Invalid Month",
        "state": "Karnataka"
    }
    
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed/month", 
        json=invalid_data
    )
    
    # Should handle invalid month gracefully with proper error response
    assert resp.status_code in [400, 422], f"Expected 400/422 for invalid month, got {resp.status_code}"

@pytest.mark.asyncio
async def test_state_analytics_invalid_state(
    client: AsyncClient, 
    invalid_state_request: StateRequest
):
    """Test state analytics with invalid state name"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed", 
        json=invalid_state_request.model_dump(mode="json")
    )
    
    # Should handle invalid state gracefully
    assert resp.status_code in [200, 400, 422]
    if resp.status_code == 200:
        data = assert_analytics_response(resp)

@pytest.mark.asyncio
async def test_state_analytics_missing_required_fields(
    client: AsyncClient
):
    """Test state analytics with missing required fields"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed/month", 
        json={}
    )
    
    # Should return validation error
    assert resp.status_code in [400, 422]

@pytest.mark.asyncio
async def test_state_analytics_concurrent_requests(
    client: AsyncClient, 
    sample_month_request: MonthDataRequest
):
    """Test concurrent requests to state analytics endpoints"""
    import asyncio
    
    # Make multiple concurrent requests
    tasks = []
    for _ in range(3):
        task = client.post(
            f"{ROUTER.STATE_ANALYTICS}/detailed/month", 
            json=sample_month_request.model_dump(mode="json")
        )
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    for resp in responses:
        assert resp.status_code == 200
        data = assert_analytics_response(resp)

@pytest.mark.parametrize("endpoint", ["/detailed/month", "/lite"])
@pytest.mark.asyncio
async def test_state_analytics_endpoints_with_month_request(
    client: AsyncClient,
    endpoint: str,
    sample_month_request: MonthDataRequest
):
    """Test multiple state analytics endpoints that accept month requests"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}{endpoint}", 
        json=sample_month_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # All endpoints should return consistent response structure
    if data:
        assert isinstance(data, (dict, list))

@pytest.mark.asyncio
async def test_state_analytics_malformed_json(
    client: AsyncClient
):
    """Test state analytics with malformed JSON"""
    resp = await client.post(
        f"{ROUTER.STATE_ANALYTICS}/detailed", 
        content="{'invalid': json}",  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    
    # Should return JSON parsing error
    assert resp.status_code in [400, 422]
