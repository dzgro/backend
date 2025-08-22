from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import SPAPIReportType, ProcessingStatus
from dzgroshared.models.amazonapi.spapi.reports import SPAPICreateReportSpecification

class SPAPIReportProcessingFinishedNotification(BaseModel):
    sellerId: str
    accountId: str
    reportId: str
    reportType: SPAPIReportType
    processingStatus: ProcessingStatus
    reportDocumentId: str

class Payload(BaseModel):
    reportProcessingFinishedNotification: SPAPIReportProcessingFinishedNotification

class NotificationMetadata(BaseModel):
    applicationId: str
    subscriptionId: str
    publishTime: str
    notificationId: str

class SpapiReportNotification(BaseModel):
    notificationVersion: str
    notificationType: str
    payloadVersion: str
    eventTime: str|SkipJsonSchema[None]=None
    payload: Payload
    metadata: NotificationMetadata


class AmazonSpapiReport(BaseModel):
    reportOptions: dict[str, str]|SkipJsonSchema[None]=None
    reporttype: SPAPIReportType
    dataStartTime: datetime|SkipJsonSchema[None]=None
    dataEndTime: datetime|SkipJsonSchema[None]=None
    reportId: str|SkipJsonSchema[None]=None
    reportDocumentId: str|SkipJsonSchema[None]=None
    processingStatus: ProcessingStatus|SkipJsonSchema[None]=None