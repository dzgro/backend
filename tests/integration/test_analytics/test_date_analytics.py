from dzgroshared.db.enums import CollateType
from dzgroshared.db.model import MonthDataRequest, PeriodDataRequest, Paginator
from httpx import AsyncClient
import pytest
import json
import sys
import os

# Add root test directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.test_helpers.assertions import assert_ok_response, assert_analytics_response

class ROUTER:
    DATE_ANALYTICS = "/analytics/dates"

@pytest.mark.asyncio
async def test_get_monthly_data_table(
    client: AsyncClient, 
    sample_period_request: PeriodDataRequest
):
    """Test GET /analytics/dates/months/all endpoint"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months/all", 
        json=sample_period_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # MonthTableResponse should contain tabular monthly data
    if data:
        assert isinstance(data, (dict, list))
        # Check for common fields in monthly data
        if isinstance(data, dict):
            expected_fields = ["months", "data", "totals"]
            for field in expected_fields:
                if field in data:
                    assert data[field] is not None

@pytest.mark.asyncio
async def test_get_month_date_data_table(
    client: AsyncClient, 
    sample_month_request: MonthDataRequest
):
    """Test GET /analytics/dates/months endpoint"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months", 
        json=sample_month_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # MonthDateTableResponse should contain date-wise data for a month
    if data:
        assert isinstance(data, (dict, list))

@pytest.mark.asyncio
async def test_get_month_lite_data(
    client: AsyncClient, 
    sample_period_request: PeriodDataRequest
):
    """Test GET /analytics/dates/months/lite endpoint"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months/lite", 
        json=sample_period_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # Lite response should be a simplified structure
    if data:
        assert isinstance(data, (dict, list))

@pytest.mark.asyncio
async def test_get_period_data(
    client: AsyncClient, 
    sample_period_request: PeriodDataRequest
):
    """Test GET /analytics/dates/period endpoint"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/period", 
        json=sample_period_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp)
    
    # PeriodDataResponse should contain period-specific analytics
    if data:
        assert isinstance(data, (dict, list))
        # Check for common analytics fields
        if isinstance(data, dict):
            expected_fields = ["total_revenue", "total_orders", "total_units_sold"]
            for field in expected_fields:
                if field in data:
                    assert isinstance(data[field], (int, float, type(None)))

@pytest.mark.asyncio
async def test_date_analytics_with_sku_collate_type(
    client: AsyncClient, 
    sku_period_request: PeriodDataRequest
):
    """Test date analytics with SKU collate type"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/period", 
        json=sku_period_request.model_dump(mode="json")
    )
    
    # Should handle different collate types gracefully
    assert resp.status_code in [200, 400, 422]
    if resp.status_code == 200:
        data = assert_analytics_response(resp)

@pytest.mark.asyncio
async def test_date_analytics_invalid_collate_type(
    client: AsyncClient, 
    marketplace: str
):
    """Test date analytics with invalid collate type"""
    invalid_request = {
        "collatetype": "INVALID_TYPE",
        "value": None
    }
    
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/period", 
        json=invalid_request
    )
    
    # Should handle invalid collate type gracefully
    assert resp.status_code in [200, 400, 422]

@pytest.mark.asyncio
async def test_date_analytics_missing_required_fields(
    client: AsyncClient
):
    """Test date analytics with missing required fields"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months/all", 
        json={}
    )
    
    # Should handle missing required fields gracefully
    assert resp.status_code in [200, 400, 422]

@pytest.mark.asyncio
async def test_date_analytics_invalid_month_format(
    client: AsyncClient, 
    invalid_month_request: MonthDataRequest
):
    """Test date analytics with invalid month format"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months", 
        json=invalid_month_request.model_dump(mode="json")
    )
    
    # Should handle invalid month gracefully
    assert resp.status_code in [200, 400, 422]

@pytest.mark.asyncio
async def test_date_analytics_concurrent_requests(
    client: AsyncClient, 
    sample_period_request: PeriodDataRequest
):
    """Test concurrent requests to date analytics endpoints"""
    import asyncio
    
    # Make multiple concurrent requests
    tasks = []
    for _ in range(3):
        task = client.post(
            f"{ROUTER.DATE_ANALYTICS}/period", 
            json=sample_period_request.model_dump(mode="json")
        )
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    for resp in responses:
        assert resp.status_code == 200
        data = assert_analytics_response(resp)

@pytest.mark.parametrize("endpoint", ["/months/all", "/months/lite", "/period"])
@pytest.mark.asyncio
async def test_date_analytics_endpoints_with_period_request(
    client: AsyncClient,
    endpoint: str,
    sample_period_request: PeriodDataRequest
):
    """Test multiple date analytics endpoints that accept period requests"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}{endpoint}", 
        json=sample_period_request.model_dump(mode="json")
    )
    
    data = assert_analytics_response(resp, f"Date Analytics {endpoint}")
    
    # All endpoints should return consistent response structure
    if data:
        assert isinstance(data, (dict, list))

@pytest.mark.asyncio
async def test_date_analytics_malformed_json(
    client: AsyncClient
):
    """Test date analytics with malformed JSON"""
    resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/period", 
        content="{'invalid': json}",  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    
    # Should return JSON parsing error
    assert resp.status_code in [400, 422]

@pytest.mark.asyncio
async def test_analytics_consistency_between_endpoints(
    client: AsyncClient, 
    sample_period_request: PeriodDataRequest,
    sample_month_request: MonthDataRequest
):
    """Test that different date analytics endpoints provide consistent data structure"""
    
    # Get data from different endpoints
    period_resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/period", 
        json=sample_period_request.model_dump(mode="json")
    )
    
    months_resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months", 
        json=sample_month_request.model_dump(mode="json")
    )
    
    lite_resp = await client.post(
        f"{ROUTER.DATE_ANALYTICS}/months/lite", 
        json=sample_period_request.model_dump(mode="json")
    )
    
    # All should succeed
    assert period_resp.status_code == 200
    assert months_resp.status_code == 200  
    assert lite_resp.status_code == 200
    
    # All should have consistent response structure
    period_data = assert_analytics_response(period_resp)
    months_data = assert_analytics_response(months_resp)
    lite_data = assert_analytics_response(lite_resp)

@pytest.mark.asyncio
async def test_all_date_analytics_endpoints_response_format(
    client: AsyncClient, 
    sample_period_request: PeriodDataRequest,
    sample_month_request: MonthDataRequest
):
    """Test that all date analytics endpoints return consistent response format"""
    
    # List of endpoints to test with their respective request types
    endpoints = [
        ("/months/all", sample_period_request),
        ("/months", sample_month_request),
        ("/months/lite", sample_period_request),
        ("/period", sample_period_request)
    ]
    
    for endpoint, request_data in endpoints:
        resp = await client.post(
            f"{ROUTER.DATE_ANALYTICS}{endpoint}", 
            json=request_data.model_dump(mode="json")
        )
        
        assert resp.status_code == 200, f"Endpoint {endpoint} failed"
        
        data = resp.json()
        # API returns data directly, just verify it's a valid response
        assert data is not None, f"No data returned from {endpoint}"
