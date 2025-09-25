"""
Shared pytest fixtures for all test files.
This file contains all the fixtures from test_bed.py to be shared across all test modules.
"""
from dzgroshared.db.enums import ENVIRONMENT, CollateType
from dzgroshared.db.model import Paginator, PyObjectId, MonthDataRequest, PeriodDataRequest
from dzgroshared.db.state_analytics.model import StateRequest
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

# Import TestDataFactory - SINGLE SOURCE OF TRUTH for all test constants
from src.test_helpers.fixtures import TestDataFactory

class ROUTER(str, Enum):
    MARKETPLACES = "/marketplace"
    SELLING_ACCOUNTS = "/selling-account"
    ADVERTISING_ACCOUNTS = "/advertising-account"

@pytest.fixture(scope="session")
def secrets()->DzgroSecrets:
    return SecretManager(env).secrets

@pytest.fixture(scope="session")
def email()->str:
    return TestDataFactory.EMAIL

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
    return TestDataFactory.MARKETPLACE_ID

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
    return PyObjectId(TestDataFactory.QUERY_ID)

@pytest.fixture(scope="session")
def paginator()->Paginator:
    return TestDataFactory.create_paginator()

# Analytics Request Model Fixtures
@pytest.fixture
def sample_month_request() -> MonthDataRequest:
    """Sample month data request for testing"""
    return TestDataFactory.create_month_request()

@pytest.fixture
def sample_period_request() -> PeriodDataRequest:
    """Sample period data request for testing"""
    return TestDataFactory.create_period_request()

@pytest.fixture
def sample_state_detailed_request() -> StateRequest:
    """Sample state detailed data request for testing"""
    return TestDataFactory.create_state_detailed_request()

@pytest.fixture
def sku_month_request() -> MonthDataRequest:
    """Sample month data request for SKU collate type testing"""
    return TestDataFactory.create_sku_month_request()

@pytest.fixture
def sku_period_request() -> PeriodDataRequest:
    """Sample period data request for SKU collate type testing"""
    return TestDataFactory.create_sku_period_request()

# Note: invalid_month_request fixture removed - invalid data should be tested via raw JSON

@pytest.fixture
def invalid_state_request() -> StateRequest:
    """Sample state detailed data request with invalid state for testing"""
    return TestDataFactory.create_invalid_state_request()

# Performance Results Test Fixtures
@pytest.fixture(scope="session")
def test_asin() -> str:
    """Test ASIN for performance results testing"""
    return TestDataFactory.TEST_ASIN

@pytest.fixture(scope="session")
def test_category() -> str:
    """Test category for performance results testing"""
    return TestDataFactory.TEST_CATEGORY

@pytest.fixture(scope="session")
def test_parent_sku() -> str:
    """Test parent SKU for performance results testing"""
    return TestDataFactory.TEST_PARENT_SKU


# Import helper functions from the centralized test helpers
from src.test_helpers.assertions import assert_ok_response, assert_list_response, assert_analytics_response

# Export all fixtures
__all__ = [
    'secrets', 'email', 'token', 'marketplace', 'client', 'queryId', 'paginator',
    'sample_month_request', 'sample_period_request', 'sample_state_detailed_request',
    'sku_month_request', 'sku_period_request', 'invalid_state_request',
    'test_asin', 'test_category', 'test_parent_sku',
    'assert_ok_response', 'assert_list_response', 'assert_analytics_response'
]