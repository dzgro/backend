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
    MARKETPLACES = "/marketplace"

@pytest.mark.asyncio
async def test_marketplace_list(client: AsyncClient, paginator: Paginator):
    """Test marketplace list endpoint"""
    endpoint = ROUTER.MARKETPLACES
    resp = await client.post(f"{endpoint}/list", json=paginator.model_dump(mode="json"))
    label = endpoint.replace('/', '').replace("_", " ").title()
    data = assert_list_response(resp, key='data', label=label, paginator=paginator)
    
    if not data: 
        return
    
    # Test pagination
    paginator.skip = 1
    resp = await client.post(f"{endpoint}/list", json=paginator.model_dump(mode="json"))
    newData = assert_list_response(resp, key='data', label=label, paginator=paginator)
    
    if not newData: 
        return
    
    assert data[0] != newData[0], "Pagination not working"

@pytest.mark.asyncio
async def test_marketplace_list_with_different_limits(client: AsyncClient):
    """Test marketplace list with different page limits"""
    endpoint = ROUTER.MARKETPLACES
    
    # Test with small limit
    small_paginator = Paginator(skip=0, limit=5)
    resp = await client.post(f"{endpoint}/list", json=small_paginator.model_dump(mode="json"))
    label = endpoint.replace('/', '').replace("_", " ").title()
    data = assert_list_response(resp, key='data', label=label, paginator=small_paginator)
    
    if data:
        assert len(data) <= 5, "Small limit not respected"

@pytest.mark.asyncio
async def test_marketplace_list_empty_pagination(client: AsyncClient):
    """Test marketplace list with high skip value (empty results)"""
    endpoint = ROUTER.MARKETPLACES
    
    # Test with very high skip to get empty results
    high_skip_paginator = Paginator(skip=1000, limit=10)
    resp = await client.post(f"{endpoint}/list", json=high_skip_paginator.model_dump(mode="json"))
    
    assert_ok_response(resp)
    res = resp.json()
    data = res.get('data', [])
    # Should return empty list or handle gracefully
    assert isinstance(data, list), "Should return list even when empty"

@pytest.mark.asyncio
async def test_marketplace_list_invalid_pagination(client: AsyncClient):
    """Test marketplace list with invalid pagination parameters"""
    endpoint = ROUTER.MARKETPLACES
    
    # Test with negative skip
    invalid_paginator = Paginator(skip=-1, limit=10)
    resp = await client.post(f"{endpoint}/list", json=invalid_paginator.model_dump(mode="json"))
    
    # Should handle invalid pagination gracefully
    assert resp.status_code in [200, 400, 422], "Should handle invalid pagination"

@pytest.mark.asyncio
async def test_marketplace_list_malformed_json(client: AsyncClient):
    """Test marketplace list with malformed JSON"""
    endpoint = ROUTER.MARKETPLACES
    
    resp = await client.post(
        f"{endpoint}/list", 
        content="{'invalid': json}",  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    
    # Should return JSON parsing error
    assert resp.status_code in [400, 422], "Should handle malformed JSON"