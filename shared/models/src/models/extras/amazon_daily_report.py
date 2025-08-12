from datetime import datetime, timedelta
from typing import Literal, get_args
from amazonapi import AmazonApiObject
from models.model import CountryDetails, ErrorDetail, ErrorList, ItemId, ItemIdWithDate, PyObjectId
from models.enums import AdExportType, AmazonDailyReportAggregationStep, AmazonParentReportTaskStatus, CollateTypeTag, MarketplaceId, MarketplaceStatus
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from models.amazonapi.adapi.common.reports import AdReportRequest, AdReport
from models.amazonapi.adapi.common.exports import ExportRequest, ExportResponse
from models.amazonapi.spapi.reports import SPAPIReport, SPAPICreateReportSpecification, SPAPIReportDocument
from models.amazonapi.spapi.datakiosk import DataKioskCreateQueryRequest, DataKioskQueryResponse, DataKioskDocumentResponse

class AdUnitParents(BaseModel):
    portfolioId: str|SkipJsonSchema[None]=None
    campaignId: str|SkipJsonSchema[None]=None
    adGroupId: str|SkipJsonSchema[None]=None

class AdUnitPerformance(BaseModel):
    impressions: int|SkipJsonSchema[None]=None
    viewableimpressions: int|SkipJsonSchema[None]=None
    newtobrandpurchases: int|SkipJsonSchema[None]=None
    newtobrandsales: float|SkipJsonSchema[None]=None
    videofirstquartileviews: int|SkipJsonSchema[None]=None
    videocompleteviews: int|SkipJsonSchema[None]=None
    videomidpointviews: int|SkipJsonSchema[None]=None
    videothirdquartileviews: int|SkipJsonSchema[None]=None
    videounmutes: int|SkipJsonSchema[None]=None
    clicks: int|SkipJsonSchema[None]=None
    cost: float|SkipJsonSchema[None]=None
    sales: float|SkipJsonSchema[None]=None
    orders: int|SkipJsonSchema[None]=None
    units: int|SkipJsonSchema[None]=None
    acos: float|SkipJsonSchema[None]=None
    roas: float|SkipJsonSchema[None]=None
    cpc: float|SkipJsonSchema[None]=None
    cvr: float|SkipJsonSchema[None]=None
    topofsearchimpressionshare: float|SkipJsonSchema[None]=None

    @model_validator(mode="before")
    def setNoneWhereZero(cls, data):
        data = {k:v for k, v in data.items() if v and v>0}
        return data

class SpSearchTerm():
    matchType: Literal["BROAD", "PHRASE", "EXACT", "TARGETING_EXPRESSION", "TARGETING_EXPRESSION_PREDEFINED"]|SkipJsonSchema[None]=None
    targeting: str|SkipJsonSchema[None]=None
    searchTerm: str


class AdReportRow(AdUnitPerformance, AdUnitParents):
    id: str = Field(alias="_id")
    # type: Literal['PORTFOLIO','CAMPAIGN','AD_GROUP','AD','SEARCH_TERM','TARGET','ADVERTISED_PRODUCT','PURCHASED_PRODUCT']
    date: datetime
    matchType: Literal["BROAD", "PHRASE", "EXACT", "TARGETING_EXPRESSION", "TARGETING_EXPRESSION_PREDEFINED"]|SkipJsonSchema[None]=None
    placementClassification: str|SkipJsonSchema[None]=None
    targeting: str|SkipJsonSchema[None]=None
    searchTerm: str|SkipJsonSchema[None]=None
    advertisedSku: str|SkipJsonSchema[None]=None
    advertisedAsin: str|SkipJsonSchema[None]=None
    purchasedSku: str|SkipJsonSchema[None]=None
    purchasedAsin: str|SkipJsonSchema[None]=None

class ReportStatus(ItemId):
    filepath: str|SkipJsonSchema[None]=None
    error: ErrorList|SkipJsonSchema[None]=None

    
class AmazonAdReport(BaseModel):
    req: AdReportRequest|SkipJsonSchema[None]=None
    res: AdReport|SkipJsonSchema[None]=None
    
    
class AmazonExportReport(BaseModel):
    exportType: AdExportType
    req: ExportRequest|SkipJsonSchema[None]=None
    res: ExportResponse|SkipJsonSchema[None]=None

class AmazonSpapiReport(BaseModel):
    req: SPAPICreateReportSpecification|SkipJsonSchema[None]=None
    res: SPAPIReport|SkipJsonSchema[None]=None
    document: SPAPIReportDocument|SkipJsonSchema[None]=None
    
class AmazonDataKioskReport(BaseModel):
    req: DataKioskCreateQueryRequest|SkipJsonSchema[None]=None
    res: DataKioskQueryResponse|SkipJsonSchema[None]=None
    document: DataKioskDocumentResponse|SkipJsonSchema[None]=None

class AmazonSpapiReportDB(AmazonSpapiReport, ReportStatus):
    pass

class AmazonAdReportDB(AmazonAdReport, ReportStatus):
    pass

class AmazonAdExportDB(AmazonExportReport, ReportStatus):
    pass
class AmazonDataKioskReportDB(AmazonDataKioskReport, ReportStatus):
    pass


class QueryBuilderValue(ItemId):
    tag: CollateTypeTag

class AmazonDailyReportMessages(BaseModel):
    messageid: str
    step: AmazonDailyReportAggregationStep
    params: dict|SkipJsonSchema[None]=None
    status: AmazonParentReportTaskStatus = AmazonParentReportTaskStatus.PENDING

class AmazonParentReport(ItemIdWithDate):
    startdate: datetime
    enddate: datetime
    spapi: list[AmazonSpapiReportDB] = []
    ad: list[AmazonAdReportDB] = []
    adexport: list[AmazonAdExportDB] = []
    kiosk: list[AmazonDataKioskReportDB] = []
    messages: list[AmazonDailyReportMessages] = []
    dates: list[datetime] = []
    progress: float
    productsComplete: bool = False

    @model_validator(mode="after")
    def setStatus(self):
        if self.startdate and self.enddate: self.dates = [self.startdate+timedelta(days=i, milliseconds=1) for i in range((self.enddate-self.startdate).days+1)]
        return self


class MarketplaceObjectForReport(ItemId):
    uid:str
    status: MarketplaceStatus
    marketplaceid: MarketplaceId
    spapi: AmazonApiObject
    ad: AmazonApiObject
    startdate: datetime|SkipJsonSchema[None]=None
    enddate: datetime|SkipJsonSchema[None]=None
    lastrefresh: datetime|SkipJsonSchema[None]=None
    details: CountryDetails
    profileid: int
    sellerid:str