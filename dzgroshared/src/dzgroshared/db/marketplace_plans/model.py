
from datetime import datetime
from enum import Enum
from typing import List
from dzgroshared.db.enums import GstStateCode
from dzgroshared.db.model import ItemId, MarketplacePlan, PyObjectId
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema

class MarketplacePlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

    
class MarketplacePlanDb(MarketplacePlan, ItemId):
    active: MarketplacePlanStatus
    gstin: PyObjectId
    createdat: datetime
    archivedat: datetime|SkipJsonSchema[None]=None
    