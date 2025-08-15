from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.model import CountryDetails
from dzgroshared.models.collections.country_details import CountryUrls, CountriesByRegion
from dzgroshared.models.enums import CountryCode,AmazonAccountType, CollectionType
from dzgroshared.client import DzgroSharedClient


class CountryDetailsHelper:
    db: DbManager

    def __init__(self, client:DzgroSharedClient):
        self.db = DbManager(client.db.database.get_collection(CollectionType.COUNTRY_DETAILS.value))

    async def getCountryDetails(self):
        return [CountryDetails(**x) for x in await self.db.find({})]
    
    async def getCountryDetailsByCountryCode(self, countryCode: CountryCode):
        return CountryUrls(**(await self.db.findOne({"_id": countryCode})))

    async def getCountriesByRegion(self, accountType: AmazonAccountType, params: str):
        urlkey = {"$concat": ["$spapi_auth_url" if accountType==AmazonAccountType.SPAPI else '$ad_auth_url', params]}
        data = await self.db.aggregate([ { '$group': { '_id': '$regionName', 'countries': { '$push': { 'countryCode': '$_id', 'country': '$country', 'url': urlkey } } } }, { '$project': { 'region': '$_id', 'countries': 1, '_id': 0 } } ])
        return [CountriesByRegion(**x) for x in data]