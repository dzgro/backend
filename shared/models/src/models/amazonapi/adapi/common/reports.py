from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from models.enums import AdProduct, AdReportType

class ReportStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ReportFormat(str, Enum):
    GZIP_JSON = "GZIP_JSON"

class TimeUnit(str, Enum):
    SUMMARY = "SUMMARY"
    DAILY = "DAILY"

class AsyncReportFilter(BaseModel):
    field: str
    values: List[str]

class AdReportConfiguration(BaseModel):
    adProduct: AdProduct
    columns: List[str]
    reportTypeId: AdReportType
    format: ReportFormat
    groupBy: List[str]
    filters: Optional[List[AsyncReportFilter]] = None
    timeUnit: TimeUnit

class AdReportRequest(BaseModel):
    startDate: str
    endDate: str
    configuration: AdReportConfiguration
    name: Optional[str] = None

class AdReport(BaseModel):
    reportId: str
    startDate: str
    endDate: str
    status: ReportStatus
    createdAt: str
    updatedAt: str
    configuration: AdReportConfiguration
    urlExpiresAt: Optional[str] = None
    url: Optional[str] = None
    fileSize: Optional[float] = None
    failureReason: Optional[str] = None
    name: Optional[str] = None
    generatedAt: Optional[str] = None
