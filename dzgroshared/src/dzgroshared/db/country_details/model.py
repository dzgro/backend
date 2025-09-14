
from pydantic import BaseModel, Field
from pydantic import HttpUrl
from dzgroshared.db.model import CountryDetails
from dzgroshared.db.enums import CountryCode, Region

class BidMinMax(BaseModel):
    min: float = 0
    max: float

class SBImageBid(BaseModel):
    cpc_image: BidMinMax
    vcpm_image_bis: BidMinMax
    vcpm_image_ntb: BidMinMax

class SBVIdeoBid(BaseModel):
    cpc_video: BidMinMax
    vcpm_video_bis: BidMinMax
    vcpm_video_ntb: BidMinMax

class SBBid(BaseModel):
    image: SBImageBid
    video: SBVIdeoBid

class SDBid(BaseModel):
    cpc: BidMinMax
    vcpm: BidMinMax

class AdProductBids(BaseModel):
    sp: BidMinMax
    sd: SDBid
    sb: SBBid


class CountryBids(BaseModel):
    bids: dict[str, dict]

class CountryDetailsWithBids(CountryDetails, CountryBids):
    pass

class CountryUrls(CountryDetails):
    auth_url:str
    ad_url:str
    ad_auth_url: str
    spapi_url: str
    spapi_auth_url: str

class CountryCodeName(BaseModel):
    countryCode:CountryCode
    country:str

class CountriesByRegion(BaseModel):
    region: str
    countries: list[CountryCodeName]

class CountriesByRegionList(BaseModel):
    regions: list[CountriesByRegion]