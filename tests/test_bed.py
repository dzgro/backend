from dzgroshared.models.enums import ENVIRONMENT
from dzgroshared.models.model import DzgroSecrets, Paginator, PyObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import pytest, json
env = ENVIRONMENT.LOCAL
from api.main import app
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from enum import Enum

class ROUTER(str, Enum):
    MARKETPLACES = "/marketplace"
    SELLING_ACCOUNTS = "/selling-account"
    ADVERTISING_ACCOUNTS = "/advertising-account"

@pytest.fixture(scope="session")
def secrets()->DzgroSecrets:
    from boto3.session import Session
    client = Session().client(
            service_name='secretsmanager',
            region_name='ap-south-1'
    )
    key = f'dzgro/prod' if env == ENVIRONMENT.PROD else f'dzgro/test'
    secrets = json.loads(client.get_secret_value(SecretId=key)['SecretString'])
    secrets = DzgroSecrets(**secrets)
    MONGO_DB_FED_CONNECT_URI = secrets.MONGO_DB_FED_CONNECT_URI.replace('fed', f'fed-{env.value.lower()}')
    secrets.MONGO_DB_FED_CONNECT_URI = MONGO_DB_FED_CONNECT_URI
    return secrets

@pytest.fixture(scope="session")
def email()->str:
    return "dzgrotechnologies@gmail.com"

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
            'PASSWORD': secrets.TEST_PASSWORD
        }
    )
    accesstoken = response['AuthenticationResult'].get('AccessToken', None)
    assert accesstoken is not None, "Access Token Not Generated"
    return accesstoken

@pytest.fixture(scope="session")
def marketplace()->str:
    return "6895638c452dc4315750e826"

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
    return PyObjectId("686750af5ec9b6bf57fe9060")

@pytest.fixture(scope="session")
def paginator()->Paginator:
    return Paginator(skip=0, limit=10)


def assert_ok_response(resp):
    assert resp.status_code == 200
    
def assert_list_response(resp, key: str, label: str, paginator: Paginator):
    assert_ok_response(resp)
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


@pytest.mark.parametrize("endpoint", [ROUTER.MARKETPLACES, ROUTER.SELLING_ACCOUNTS, ROUTER.ADVERTISING_ACCOUNTS])
async def test_list(client, endpoint: ROUTER, paginator: Paginator):
    resp = await client.post(f"{endpoint.value}/list", json=paginator.model_dump(mode="json"))
    label = endpoint.value.replace('/','').replace("_", " ").title()
    data = assert_list_response(resp, key='data', label=label, paginator=paginator)
    if not data: return
    paginator.skip=1
    resp = await client.post(f"{endpoint.value}/list", json=paginator.model_dump(mode="json"))
    newData = assert_list_response(resp, key='data', label=label, paginator=paginator)
    if not newData: return
    assert data[0]!=newData[0], "Pagination not working"

    