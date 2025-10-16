
from datetime import datetime
from enum import Enum
from typing import List
from dzgroshared.db.enums import GstStateCode
from dzgroshared.db.model import ItemId, PyObjectId
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema


class MarketplaceGSTStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class MarketplaceGst(ItemId):
    gstin: PyObjectId
    marketplace: PyObjectId
    active: MarketplaceGSTStatus
    createdat: datetime
    archivedat: datetime|SkipJsonSchema[None]=None
    