from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from dzgroshared.models.enums import SPAPIReportType
from pydantic import BaseModel, Field, RootModel
from pydantic.json_schema import SkipJsonSchema

class ProcessingStatus(str, Enum):
    """Report processing status values."""
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    FATAL = "FATAL"
    IN_PROGRESS = "IN_PROGRESS"
    IN_QUEUE = "IN_QUEUE"

class ReportPeriod(str, Enum):
    """Report schedule period values."""
    PT5M = "PT5M"  # 5 minutes
    PT15M = "PT15M"  # 15 minutes
    PT30M = "PT30M"  # 30 minutes
    PT1H = "PT1H"  # 1 hour
    PT2H = "PT2H"  # 2 hours
    PT4H = "PT4H"  # 4 hours
    PT8H = "PT8H"  # 8 hours
    PT12H = "PT12H"  # 12 hours
    P1D = "P1D"  # 1 day
    P2D = "P2D"  # 2 days
    P3D = "P3D"  # 3 days
    PT84H = "PT84H"  # 84 hours
    P7D = "P7D"  # 7 days
    P14D = "P14D"  # 14 days
    P15D = "P15D"  # 15 days
    P18D = "P18D"  # 18 days
    P30D = "P30D"  # 30 days
    P1M = "P1M"  # 1 month

class CompressionAlgorithm(str, Enum):
    """Report compression algorithm values."""
    GZIP = "GZIP"

class ReportOptions(RootModel[Dict[str, str]]):
    pass

class SPAPIReport(BaseModel):
    """Report information."""
    marketplace_ids: Optional[List[str]] = Field(None, alias="marketplaceIds")
    report_id: str = Field(..., alias="reportId")
    report_type: str = Field(..., alias="reportType")
    data_start_time: Optional[datetime] = Field(None, alias="dataStartTime")
    data_end_time: Optional[datetime] = Field(None, alias="dataEndTime")
    report_schedule_id: Optional[str] = Field(None, alias="reportScheduleId")
    created_time: datetime = Field(..., alias="createdTime")
    processing_status: ProcessingStatus = Field(..., alias="processingStatus")
    processing_start_time: Optional[datetime] = Field(None, alias="processingStartTime")
    processing_end_time: Optional[datetime] = Field(None, alias="processingEndTime")
    report_document_id: Optional[str] = Field(None, alias="reportDocumentId")

class SPAPIReportSchedule(BaseModel):
    """Report schedule information."""
    report_schedule_id: str = Field(..., alias="reportScheduleId")
    report_type: SPAPIReportType = Field(..., alias="reportType")
    marketplace_ids: Optional[List[str]] = Field(None, alias="marketplaceIds")
    report_options: Optional[ReportOptions] = Field(None, alias="reportOptions")
    period: ReportPeriod
    next_report_creation_time: Optional[datetime] = Field(None, alias="nextReportCreationTime")

class SPAPIReportDocument(BaseModel):
    """Report document information."""
    report_document_id: str = Field(..., alias="reportDocumentId")
    url: str
    compression_algorithm: Optional[CompressionAlgorithm] = Field(None, alias="compressionAlgorithm")

# Request models
class SPAPICreateReportSpecification(BaseModel):
    """Specification for creating a report."""
    report_options: ReportOptions|SkipJsonSchema[None] = Field(None, alias="reportOptions")
    report_type: SPAPIReportType = Field(..., alias="reportType")
    data_start_time: datetime|SkipJsonSchema[None] = Field(None, alias="dataStartTime")
    data_end_time: datetime|SkipJsonSchema[None] = Field(None, alias="dataEndTime")
    marketplace_ids: List[str] = Field(..., alias="marketplaceIds")

class SPAPICreateReportScheduleSpecification(BaseModel):
    """Specification for creating a report schedule."""
    report_type: SPAPIReportType = Field(..., alias="reportType")
    marketplace_ids: List[str] = Field(..., alias="marketplaceIds")
    report_options: Optional[ReportOptions] = Field(None, alias="reportOptions")
    period: ReportPeriod
    next_report_creation_time: Optional[datetime] = Field(None, alias="nextReportCreationTime")

# Response models
class SPAPICreateReportResponse(BaseModel):
    """Response for create_report operation."""
    report_id: str = Field(..., alias="reportId")

class SPAPIGetReportsResponse(BaseModel):
    """Response for get_reports operation."""
    reports: List[SPAPIReport]
    next_token: Optional[str] = Field(None, alias="nextToken")

class SPAPICreateReportScheduleResponse(BaseModel):
    """Response for create_report_schedule operation."""
    report_schedule_id: str = Field(..., alias="reportScheduleId")

class SPAPIReportScheduleList(BaseModel):
    """Response for get_report_schedules operation."""
    report_schedules: List[SPAPIReportSchedule] = Field(..., alias="reportSchedules")
