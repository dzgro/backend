from enum import Enum
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import ObjectIdStr
from dzgroshared.db.products.model import Product

class AdGroupMappingType(str, Enum):
    KEYWORD = "KEYWORD"
    PRODUCT = "PRODUCT"

class AdGroupMappingOption(BaseModel):
    type: AdGroupMappingType
    adGroups: list[str]

class AdGroupMappingData(BaseModel):
    adGroupId: str
    campaignId: str
    adGroupName: str
    campaignName: str
    targetType: str
    targetDetails: list[str]
    options: AdGroupMappingOption|SkipJsonSchema[None]=None
    portfolioId: str|SkipJsonSchema[None]=None
    count: int=0
    
class AdGroupMappings(BaseModel):
    products: list[Product]
    data: list[AdGroupMappingData]
    count: int=0

class AdGroupMapping(ObjectIdStr):
    adgroupid: str
    type: AdGroupMappingType
    