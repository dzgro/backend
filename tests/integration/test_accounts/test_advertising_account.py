from dzgroshared.db.model import Paginator
from httpx import AsyncClient
import pytest
import json
import sys
import os

# Add root test directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.test_helpers.assertions import assert_ok_response, assert_list_response

class ROUTER:
    ADVERTISING_ACCOUNTS = "/advertising-account"

@pytest.mark.asyncio
async def test_advertising_account_list(client: AsyncClient, paginator: Paginator):
    """Test advertising account list endpoint"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    resp = await client.post(f"{endpoint}/", json=paginator.model_dump(mode="json"))
    label = endpoint.replace('/', '').replace("_", " ").title()
    data = assert_list_response(resp, key='data', label=label, paginator=paginator)
    
    if not data: 
        return
    
    # Test pagination
    pagination_paginator = Paginator(skip=1, limit=paginator.limit)
    resp = await client.post(f"{endpoint}/", json=pagination_paginator.model_dump(mode="json"))
    label = endpoint.replace('/', '').replace("_", " ").title()
    newData = assert_list_response(resp, key='data', label=label, paginator=pagination_paginator)
    
    if not newData: 
        return
    
    assert data[0] != newData[0], "Pagination not working"

@pytest.mark.asyncio
async def test_advertising_account_list_with_different_limits(client: AsyncClient):
    """Test advertising account list with different page limits"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    # Test with small limit
    small_paginator = Paginator(skip=0, limit=5)
    resp = await client.post(f"{endpoint}/", json=small_paginator.model_dump(mode="json"))
    label = endpoint.replace('/', '').replace("_", " ").title()
    data = assert_list_response(resp, key='data', label=label, paginator=small_paginator)
    
    if data:
        assert len(data) <= 5, "Small limit not respected"

@pytest.mark.asyncio
async def test_advertising_account_list_empty_pagination(client: AsyncClient):
    """Test advertising account list with high skip value (empty results)"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    # Test with very high skip to get empty results
    high_skip_paginator = Paginator(skip=1000, limit=10)
    resp = await client.post(f"{endpoint}/", json=high_skip_paginator.model_dump(mode="json"))
    
    assert_ok_response(resp)
    res = resp.json()
    data = res.get('data', [])
    # Should return empty list or handle gracefully
    assert isinstance(data, list), "Should return list even when empty"

@pytest.mark.asyncio
async def test_advertising_account_list_invalid_pagination(client: AsyncClient):
    """Test advertising account list with invalid pagination parameters"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    # Test with negative skip
    invalid_paginator = Paginator(skip=-1, limit=10)
    resp = await client.post(f"{endpoint}/", json=invalid_paginator.model_dump(mode="json"))
    
    # Should handle invalid pagination gracefully
    assert resp.status_code in [200, 400, 422], "Should handle invalid pagination"

@pytest.mark.asyncio
async def test_advertising_account_list_large_limit(client: AsyncClient):
    """Test advertising account list with very large limit"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    # Test with large limit
    large_limit_paginator = Paginator(skip=0, limit=1000)
    resp = await client.post(f"{endpoint}/", json=large_limit_paginator.model_dump(mode="json"))
    
    # Should handle large limit gracefully (may cap it or return error)
    assert resp.status_code in [200, 400, 422], "Should handle large limit"

@pytest.mark.asyncio
async def test_advertising_account_list_malformed_json(client: AsyncClient):
    """Test advertising account list with malformed JSON"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    resp = await client.post(
        f"{endpoint}/", 
        content="{'invalid': json}",  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    
    # Should return JSON parsing error
    assert resp.status_code in [400, 422], "Should handle malformed JSON"

@pytest.mark.asyncio
async def test_advertising_account_list_missing_body(client: AsyncClient):
    """Test advertising account list with missing request body"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    resp = await client.post(f"{endpoint}/")
    
    # Should handle missing body gracefully
    assert resp.status_code in [200, 400, 422], "Should handle missing request body"

@pytest.mark.asyncio
async def test_advertising_account_list_concurrent_requests(client: AsyncClient, paginator: Paginator):
    """Test concurrent requests to advertising account list endpoint"""
    import asyncio
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    # Make multiple concurrent requests
    tasks = []
    for _ in range(3):
        task = client.post(f"{endpoint}/", json=paginator.model_dump(mode="json"))
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    for resp in responses:
        assert resp.status_code == 200
        data = resp.json()
        assert 'data' in data

@pytest.mark.asyncio
async def test_advertising_account_list_response_structure(client: AsyncClient, paginator: Paginator):
    """Test advertising account list response structure"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    resp = await client.post(f"{endpoint}/", json=paginator.model_dump(mode="json"))
    assert_ok_response(resp)
    
    data = resp.json()
    
    # Verify expected response structure - no count field in POST /
    assert 'data' in data, "Response should contain 'data' field"
    assert 'count' not in data, "Response should not contain 'count' field in POST /"
    assert isinstance(data['data'], list), "'data' should be a list"

@pytest.mark.asyncio
async def test_advertising_account_count(client: AsyncClient):
    """Test advertising account count endpoint"""
    endpoint = ROUTER.ADVERTISING_ACCOUNTS
    
    resp = await client.get(f"{endpoint}/count")
    assert_ok_response(resp)
    
    data = resp.json()
    
    # Verify count response structure
    assert 'count' in data, "Count endpoint should return 'count' field"
    assert isinstance(data['count'], int), "'count' should be an integer"
    assert data['count'] >= 0, "'count' should be non-negative"