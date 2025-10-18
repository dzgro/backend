
from datetime import datetime
from enum import Enum
from typing import List
from dzgroshared.db.enums import GstStateCode
from dzgroshared.db.model import ItemId, PyObjectId
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema


class MarketplaceGSTStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"

class MarketplaceGst(ItemId):
    gstin: PyObjectId
    marketplace: PyObjectId
    status: MarketplaceGSTStatus
    createdat: datetime
    archivedat: datetime|SkipJsonSchema[None]=None
    