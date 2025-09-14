from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.model import CountryDetails
from dzgroshared.db.country_details.model import CountriesByRegionList, CountryUrls, CountriesByRegion
from dzgroshared.db.enums import CountryCode,AmazonAccountType, CollectionType
from dzgroshared.client import DzgroSharedClient


class CountryDetailsHelper:
    db: DbManager

    def __init__(self, client:DzgroSharedClient):
        self.db = DbManager(client.db.database.get_collection(CollectionType.COUNTRY_DETAILS.value))

    async def getCountryDetails(self):
        return [CountryDetails(**x) for x in await self.db.find({})]
    
    async def getCountryDetailsByCountryCode(self, countryCode: CountryCode):
        countryDetail = await self.db.findOne({"_id": countryCode.value})
        return CountryUrls.model_validate(countryDetail)

    async def getCountriesByRegion(self):
        data = await self.db.aggregate([ { '$group': { '_id': '$regionName', 'countries': { '$push': { 'countryCode': '$_id', 'country': '$country' } } } }, { '$project': { 'region': '$_id', 'countries': 1, '_id': 0 } } ])
        return CountriesByRegionList.model_validate({"regions": data})