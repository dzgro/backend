"""
Shared test assertions and helper functions.
Centralized location for all test assertion utilities.
"""

from dzgroshared.db.model import Paginator
from httpx import Response
from typing import Any, Dict, Optional


def assert_ok_response(resp: Response) -> None:
    """Assert that response has 200 status code."""
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


def assert_error_response(resp: Response, expected_status: int) -> None:
    """Assert that response has expected error status code."""
    assert resp.status_code == expected_status, f"Expected {expected_status}, got {resp.status_code}: {resp.text}"


def assert_list_response(resp: Response, key: str, label: str, paginator: Paginator) -> list:
    """
    Assert list response structure and pagination.
    
    Args:
        resp: HTTP response
        key: Key containing the data list
        label: Label for error messages
        paginator: Paginator used in request
        
    Returns:
        The data list from response
    """
    assert_ok_response(resp)
    res = resp.json()
    data = res.get(key, None)
    assert data is not None, "Incorrect Response"
    
    accounts_count = len(data)
    if paginator.skip == 0 and accounts_count > 0:
        assert accounts_count <= paginator.limit, "Data count exceeds limit"
    
    # Count field is no longer returned in POST "/" responses
    assert 'count' not in res, "POST / should not return count field"
    
    return data


def assert_analytics_response(resp: Response) -> Any:
    """
    Assert analytics response structure.
    
    Args:
        resp: HTTP response
        
    Returns:
        The response data (dict or list)
    """
    assert_ok_response(resp)
    data = resp.json()
    assert isinstance(data, (dict, list)), "Analytics response should be dict or list"
    return data


def assert_pagination_working(original_data: list, paginated_data: list) -> None:
    """Assert that pagination is working by comparing data sets."""
    if not paginated_data:
        return
    
    assert original_data[0] != paginated_data[0], "Pagination not working"


def assert_response_contains_fields(resp: Response, required_fields: list) -> Dict[str, Any]:
    """Assert response contains all required fields."""
    assert_ok_response(resp)
    data = resp.json()
    
    for field in required_fields:
        assert field in data, f"Response missing required field: {field}"
    
    return data


def assert_concurrent_requests_success(responses: list) -> None:
    """Assert all concurrent requests succeeded."""
    for i, resp in enumerate(responses):
        assert resp.status_code == 200, f"Request {i} failed with status {resp.status_code}"
        data = resp.json()
        assert isinstance(data, (dict, list)), f"Request {i} returned invalid data type"