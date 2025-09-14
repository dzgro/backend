from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from dzgroshared.db.enums import AdProduct, AdState

# Enums
class ExportStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TargetType(str, Enum):
    AUTO = "AUTO"
    KEYWORD = "KEYWORD"
    PRODUCT_CATEGORY = "PRODUCT_CATEGORY"
    PRODUCT = "PRODUCT"
    PRODUCT_CATEGORY_AUDIENCE = "PRODUCT_CATEGORY_AUDIENCE"
    PRODUCT_AUDIENCE = "PRODUCT_AUDIENCE"
    AUDIENCE = "AUDIENCE"
    THEME = "THEME"

class TargetLevel(str, Enum):
    CAMPAIGN = "CAMPAIGN"
    AD_GROUP = "AD_GROUP"

# Error model
class UniversalApiError(BaseModel):
    errorCode: Optional[str]
    message: str

# Response model
class ExportResponse(BaseModel):
    exportId: str
    status: ExportStatus
    createdAt: Optional[str] = None
    fileSize: Optional[float] = None
    urlExpiresAt: Optional[str] = None
    generatedAt: Optional[str] = None
    url: Optional[str] = None
    error: Optional[UniversalApiError] = None

# Request models
class ExportRequest(BaseModel):
    stateFilter: Optional[List[AdState]] = None
    adProductFilter: Optional[List[AdProduct]] = None

class TargetsExportRequest(ExportRequest):
    targetTypeFilter: Optional[List[TargetType]] = None
    targetLevelFilter: Optional[List[TargetLevel]] = None
    negativeFilter: Optional[List[bool]] = None
