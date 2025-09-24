"""
Shared pytest fixtures for all test files.
This file contains all the fixtures from test_bed.py to be shared across all test modules.
"""
from dzgroshared.db.enums import ENVIRONMENT, CollateType
from dzgroshared.db.model import Paginator, PyObjectId, MonthDataRequest, PeriodDataRequest
from dzgroshared.db.state_analytics.model import StateDetailedDataByStateRequest
from dzgroshared.secrets.model import DzgroSecrets
from dzgroshared.secrets.client import SecretManager
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import pytest, json
env = ENVIRONMENT.LOCAL
from api.main import app
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from enum import Enum

# ==================================================================================
# TEST CONFIGURATION - Edit all hardcoded values here in one place
# ==================================================================================
class TestConfig:
    """Centralized test configuration - all hardcoded values in one place"""
    
    # Authentication & Marketplace
    EMAIL = "dzgrotechnologies@gmail.com"
    MARKETPLACE_ID = "6895638c452dc4315750e826"
    QUERY_ID = "686750af5ec9b6bf57fe9060"
    
    # Test Data Values
    TEST_MONTH = "Dec 2024"
    TEST_SKU = "TEST-SKU-123"
    TEST_STATE = "Karnataka"
    
    # Invalid Test Values (for error testing)
    INVALID_MONTH = "Invalid Month"
    INVALID_STATE = "InvalidState"
    
    # Pagination
    PAGINATOR_SKIP = 0
    PAGINATOR_LIMIT = 10
    
    # Default Collate Types
    DEFAULT_COLLATE_TYPE = CollateType.MARKETPLACE
    SKU_COLLATE_TYPE = CollateType.SKU
# ==================================================================================

class ROUTER(str, Enum):
    MARKETPLACES = "/marketplace"
    SELLING_ACCOUNTS = "/selling-account"
    ADVERTISING_ACCOUNTS = "/advertising-account"

@pytest.fixture(scope="session")
def secrets()->DzgroSecrets:
    return SecretManager(env).secrets

@pytest.fixture(scope="session")
def email()->str:
    return TestConfig.EMAIL

@pytest.fixture(scope="session")
def token(email, secrets: DzgroSecrets)->str:
    from boto3.session import Session
    client = Session().client(
            service_name='cognito-idp',
            region_name='ap-south-1'
    )
    response = client.initiate_auth(
        ClientId=secrets.COGNITO_APP_CLIENT_ID,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': email,
            'PASSWORD': secrets.USER_DUMMY_PASSWORD
        }
    )
    accesstoken = response['AuthenticationResult'].get('AccessToken', None)
    assert accesstoken is not None, "Access Token Not Generated"
    return accesstoken

@pytest.fixture(scope="session")
def marketplace()->str:
    return TestConfig.MARKETPLACE_ID

@pytest.fixture
async def client(token, marketplace, secrets: DzgroSecrets)-> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    import jwt
    jwks_url = f"https://cognito-idp.ap-south-1.amazonaws.com/{secrets.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    app.state.env = env
    app.state.jwtClient = jwt.PyJWKClient(jwks_url)
    app.state.secrets = secrets
    app.state.mongoClient = AsyncIOMotorClient(secrets.MONGO_DB_CONNECT_URI, appname="dzgro-api")
    async with AsyncClient(
            transport=transport,
            base_url="http://127.0.0.1",
            headers={"Authorization": f"Bearer {token}", "marketplace": marketplace}
        ) as ac:
        yield ac

@pytest.fixture(scope="session")
def queryId()->PyObjectId:
    return PyObjectId(TestConfig.QUERY_ID)

@pytest.fixture(scope="session")
def paginator()->Paginator:
    return Paginator(skip=TestConfig.PAGINATOR_SKIP, limit=TestConfig.PAGINATOR_LIMIT)

# Analytics Request Model Fixtures
@pytest.fixture
def sample_month_request() -> MonthDataRequest:
    """Sample month data request for testing"""
    return MonthDataRequest(
        collatetype=TestConfig.DEFAULT_COLLATE_TYPE,
        value=None,
        month=TestConfig.TEST_MONTH
    )

@pytest.fixture
def sample_period_request() -> PeriodDataRequest:
    """Sample period data request for testing"""
    return PeriodDataRequest(
        collatetype=TestConfig.DEFAULT_COLLATE_TYPE,
        value=None
    )

@pytest.fixture
def sample_state_detailed_request() -> StateDetailedDataByStateRequest:
    """Sample state detailed data request for testing"""
    return StateDetailedDataByStateRequest(
        collatetype=TestConfig.DEFAULT_COLLATE_TYPE,
        value=None,
        state=TestConfig.TEST_STATE
    )

@pytest.fixture
def sku_month_request() -> MonthDataRequest:
    """Sample month data request for SKU collate type testing"""
    return MonthDataRequest(
        collatetype=TestConfig.SKU_COLLATE_TYPE,
        value=TestConfig.TEST_SKU,
        month=TestConfig.TEST_MONTH
    )

@pytest.fixture
def sku_period_request() -> PeriodDataRequest:
    """Sample period data request for SKU collate type testing"""
    return PeriodDataRequest(
        collatetype=TestConfig.SKU_COLLATE_TYPE,
        value=TestConfig.TEST_SKU
    )

@pytest.fixture
def invalid_month_request() -> MonthDataRequest:
    """Sample month data request with invalid month for testing"""
    return MonthDataRequest(
        collatetype=TestConfig.DEFAULT_COLLATE_TYPE,
        value=None,
        month=TestConfig.INVALID_MONTH
    )

@pytest.fixture
def invalid_state_request() -> StateDetailedDataByStateRequest:
    """Sample state detailed data request with invalid state for testing"""
    return StateDetailedDataByStateRequest(
        collatetype=TestConfig.DEFAULT_COLLATE_TYPE,
        value=None,
        state=TestConfig.INVALID_STATE
    )


# Import helper functions from the centralized test helpers
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from src.test_helpers.assertions import assert_ok_response, assert_list_response, assert_analytics_response
from src.test_helpers.fixtures import TestDataFactory

# Keep the original functions for backward compatibility
def assert_ok_response_legacy(resp):
    """Legacy function - use assert_ok_response from test_helpers instead"""
    assert resp.status_code == 200
    
def assert_list_response_legacy(resp, key: str, label: str, paginator: Paginator):
    """Legacy function - use assert_list_response from test_helpers instead"""
    assert_ok_response_legacy(resp)
    res = resp.json()
    data = res.get(key,None)
    assert data is not None, "Incorrect Response"
    accountsCount = len(data)
    if paginator.skip==0:
        assert accountsCount>0, f"{label} count not be Fetched"
        assert accountsCount<=paginator.limit, "Data count exceeds limit"
        count = res.get('count',None)
        assert count is not None, f"{label} count not be Fetched"
        if count<=paginator.limit:
            assert count==accountsCount, f"{label} count mismatch"
    return data