from api.routers import spapi
from bson import ObjectId
from dzgroshared.models.collections.user import TempAccountRequest
from dzgroshared.models.model import Paginator, PyObjectId, RenameAccountRequest, SuccessResponse
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.enums import AmazonAccountType, CollectionType, CountryCode, MarketplaceId 
from dzgroshared.models.collections.spapi_accounts import MarketplaceParticipations, SPAPIAccount, SPAPIAccountList, SPAPIAccountRequest, SPAPIAccountUrlResponse
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.amazonapi.spapi import SpApiClient

class SPAPIAccountsHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.SPAPI_ACCOUNTS.value), uid=client.uid)

    async def getSeller(self, sellerid: str):
        return SPAPIAccount.model_validate(await self.db.findOne({"sellerid": sellerid}))
    
    async def getUrl(self, req: TempAccountRequest):
        redirect_uri = self.client.secrets.AUTH_REDIRECT_URL
        import string,random
        req.state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        params = f'/apps/authorize/consent?application_id={self.client.secrets.SPAPI_APPLICATION_ID}&state={req.state}&redirect_uri={redirect_uri}'
        country = await self.client.db.country_details.getCountryDetailsByCountryCode(req.countrycode)
        url = f"{country.spapi_auth_url}{params}"
        await self.client.db.user.createTempAccountAdditionRequest(req)
        return SPAPIAccountUrlResponse(url=url)
    
    async def authoriseSeller(self, data: SPAPIAccountRequest):
        try:
            return self.getSeller(sellerid=data.sellerid)
        except Exception as e:
            tempReq = await self.client.db.user.getTempAccountAdditionRequest()
            from dzgroshared.amazonapi.auth import Onboard
            manager = Onboard(self.client.secrets.SPAPI_CLIENT_ID, self.client.secrets.SPAPI_CLIENT_SECRET, self.client.secrets.AUTH_REDIRECT_URL)
            refreshtoken = manager.generateRefreshToken(data.code)
            await self.db.insertOne({"sellerid": data.sellerid, "refreshtoken": refreshtoken, "uid": self.client.uid, "name": tempReq.name, "countrycode": tempReq.countrycode})
            return self.getSeller(sellerid=data.sellerid)

    async def getSellerAccounts(self, paginator: Paginator):
        data = await self.db.find({"uid": self.client.uid}, skip=paginator.skip, limit=paginator.limit, projectionExc=["refreshtoken"])
        count = None if paginator.skip!=0 else await self.db.count({"uid": self.client.uid})
        return SPAPIAccountList.model_validate({"data": data, "count": count})

    async def rename(self, body: RenameAccountRequest):
        count = await self.db.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
        
    async def getAccountApiClient(self, id: PyObjectId):
        urlKey = '$spapi_url'
        pipeline = [ self.db.pp.matchMarketplace({'_id': id}), { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken"} }]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        return SpApiClient(**{**data[0], "client_id":self.client.secrets.SPAPI_CLIENT_ID, "client_secret":self.client.secrets.SPAPI_CLIENT_SECRET, "isad": False})

    async def isSellerAlreadyAdded(self, sellerId: str)->bool:
        seller = await self.db.findOne({"sellerId": sellerId, "uid": self.client.uid})
        if not seller: return False
        return True
    
    async def updateSeller(self, sellerId: str, updateDict: dict, upsert: bool=False):
       await self.db.updateOne({"sellerId": sellerId, "uid": self.client.uid}, updateDict, upsert=upsert)

    async def getMarketplaceParticipations(self, id: PyObjectId):
        client = await self.getAccountApiClient(id)
        sellerMarketplaces = await client.sellers.get_marketplace_participations()
        if not sellerMarketplaces.payload: raise ValueError('No marketplaces found')
        return MarketplaceParticipations.model_validate({"data": list(filter(lambda x: x.marketplace.id in MarketplaceId.values(), sellerMarketplaces.payload))})

