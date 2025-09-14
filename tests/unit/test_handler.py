from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import ENVIRONMENT
from dzgroshared.db.model import PyObjectId, StartEndDate
import pytest


env = ENVIRONMENT.LOCAL


@pytest.fixture(scope="session")
def dates()->StartEndDate:
    enddate = datetime(2025, 8, 31)
    startdate= datetime(2025, 7, 3)
    return StartEndDate(startdate=startdate, enddate=enddate)

@pytest.fixture(scope="session")
def queryId()->PyObjectId:
    return PyObjectId("686750af5ec9b6bf57fe9060")


@pytest.fixture(scope="session")
def uid()->str:
    return "41e34d1a-6031-70d2-9ff3-d1a704240921"

@pytest.fixture(scope="session")
def marketplace()->PyObjectId:
    return PyObjectId("6895638c452dc4315750e826")

@pytest.fixture(scope="session")
async def dzgroshared(marketplace, uid)->DzgroSharedClient:
    from motor.motor_asyncio import AsyncIOMotorClient
    shared = DzgroSharedClient(env)
    shared.setMongoClient(AsyncIOMotorClient(shared.secrets.MONGO_DB_CONNECT_URI, appname="dzgro-api"))
    shared.setUid(uid)
    m = await shared.mongoClient[shared.DB_NAME]['marketplaces'].find_one({"_id": marketplace, "uid": uid})
    shared.setMarketplace(marketplace)
    return shared

@pytest.mark.user
async def getMarketplaces(dzgroshared: DzgroSharedClient):
    assert await dzgroshared.db.user.getMarketplaces()