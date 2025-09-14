from bson import ObjectId
from dzgroshared.amazonapi.model import AmazonApiObject
from dzgroshared.db.users.model import TempAccountRequest
from dzgroshared.db.enums import CollectionType, CountryCode 
from dzgroshared.db.advertising_accounts.model import AdAccountsList, AdvertisingAccountRequest, AdvertisingAccountUrlResponse, AdAccount, AdvertisingAccount, AdvertisingAccountList
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.model import Paginator, PyObjectId, RenameAccountRequest, SuccessResponse
from dzgroshared.client import DzgroSharedClient
from dzgroshared.amazonapi.adapi import AdApiClient

class AdvertisingAccountsHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADVERTISING_ACCOUNTS.value), uid=client.uid)

    async def rename(self, body: RenameAccountRequest):
        count = await self.db.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
    
    async def getAccountApiClient(self, id: PyObjectId):
        urlKey = '$ad_url'
        pipeline = [ self.db.pp.matchMarketplace({'_id': self.db.convertToObjectId(id)}), { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken"} }]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        obj = AmazonApiObject.model_validate({**data[0], "client_id":self.client.secrets.ADS_CLIENT_ID, "client_secret":self.client.secrets.ADS_CLIENT_SECRET, "isad": True})
        return AdApiClient(obj)

    async def getAdvertisingAccount(self, id: PyObjectId):
        account = await self.db.findOne({"_id": id, "uid": self.client.uid})
        if not account: raise ValueError("Invalid Advertising Account")
        return AdvertisingAccount.model_validate(**account)
    
    async def renameAccount(self, body: RenameAccountRequest):
        count = await self.db.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
    
    async def addAdvertisingAccount(self, refreshtoken: str, countryCode: CountryCode, name: str):
        data = {"name": name, "uid": self.client.uid, "countrycode": countryCode, "refreshtoken": refreshtoken}
        id =  await self.db.insertOne(data)
        return await self.getAdvertisingAccount(PyObjectId(str(id)))
    
    async def deleteAdvertisingAccount(self, id: str):
        await self.db.deleteOne({"_id": ObjectId(id), "uid": self.client.uid})
    
    async def getAdvertisingAccounts(self, paginator: Paginator):
        accounts = await self.db.find({"uid": self.client.uid}, skip=paginator.skip, limit=paginator.limit, projectionExc=['refreshtoken'])
        count = None if paginator.skip!=0 else await self.db.count({"uid": self.client.uid})
        return AdvertisingAccountList.model_validate({"data": accounts, "count": count})
        
    async def getUrl(self, req: TempAccountRequest):
        redirect_uri = self.client.secrets.AUTH_REDIRECT_URL
        params = f'?client_id={self.client.secrets.ADS_CLIENT_ID}&scope=advertising::campaign_management&redirect_uri={redirect_uri}&response_type=code'
        country = await self.client.db.country_details.getCountryDetailsByCountryCode(req.countrycode)
        url = f"{country.ad_auth_url}{params}"
        await self.client.db.users.createTempAccountAdditionRequest(req)
        return AdvertisingAccountUrlResponse(url=url)

    async def authoriseAccount(self, data: AdvertisingAccountRequest):
        tempReq = await self.client.db.users.getTempAccountAdditionRequest()
        from dzgroshared.amazonapi.auth import Onboard
        manager = Onboard(self.client.secrets.ADS_CLIENT_ID, self.client.secrets.ADS_CLIENT_SECRET, self.client.secrets.AUTH_REDIRECT_URL)
        refreshtoken = manager.generateRefreshToken(data.code)
        id = await self.db.insertOne({"refreshtoken": refreshtoken, "uid": self.client.uid, "name": tempReq.name, "countrycode": tempReq.countrycode})
        return self.getAdvertisingAccount(PyObjectId(id))
    
    async def getAdAccounts(self, id: PyObjectId):
        client = await self.getAccountApiClient(id)
        response = await client.common.adsAccountsClient.listAccounts()
        accounts: list[AdAccount] = []
        for acc in list(filter(lambda x: x.status in ["CREATED", "ACTIVE"], response.adsAccounts)):
            for code in list(filter(lambda x: x in CountryCode.values(), acc.countryCodes)):
                profileId = next((x.profileId for x in acc.alternateIds if x.countryCode==code and x.entityId is None), None)
                entityId = next((x.entityId for x in acc.alternateIds if x.countryCode==code and x.profileId is None), None)
                if profileId and entityId:
                    adAccount = AdAccount(adsaccountid=acc.adsAccountId, accountname=acc.accountName, countryCode=CountryCode(code), profileid=profileId, entityid=entityId)
                    accounts.append(adAccount)
        return AdAccountsList.model_validate({"data": accounts})
