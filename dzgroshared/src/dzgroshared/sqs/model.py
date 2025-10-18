from dzgroshared.db.enums import QueueMessageModelType
from dzgroshared.db.model import DzgroError
from dzgroshared.db.model import ErrorDetail, ErrorList
from pydantic import BaseModel, model_validator, Field, computed_field, ConfigDict, conint
from pydantic.json_schema import SkipJsonSchema
from typing import Optional, Dict
from enum import Enum
from typing import Optional, Dict, List, Any
from enum import Enum
import json
from datetime import datetime

class QueueName(str, Enum):
    AMAZON_REPORTS = "AmazonReports"
    RAZORPAY_WEBHOOK = "RazorpayWebhook"
    DZGRO_REPORTS = "DzgroReports"
    AMS_CHANGE = "AmsChange"
    AMS_PERFORMANCE = "AmsPerformance"
    INVOICE_GENERATOR = "InvoiceGenerator"
    DAILY_REPORT_REFRESH_BY_COUNTRY_CODE = "DailyReportRefreshByCountryCode"

    @classmethod
    def all(cls):
        return list(cls)


# ================================
# 📥 RECEIVING FROM SQS (Lambda Input)
# ================================
class SQSAttributes(BaseModel):
    model_config = ConfigDict(extra="allow")  # allow unexpected attributes
    ApproximateReceiveCount: int
    SentTimestamp: datetime
    SenderId: str
    ApproximateFirstReceiveTimestamp: datetime
    MessageDeduplicationId: str|SkipJsonSchema[None] = None  # FIFO only
    MessageGroupId: str|SkipJsonSchema[None] = None          # FIFO only
    SequenceNumber: int|SkipJsonSchema[None] = None          # FIFO only

    @model_validator(mode="before")
    @classmethod
    def parse_timestamps(cls, data: dict) -> dict:
        if "SentTimestamp" in data:
            data["SentTimestamp"] = datetime.fromtimestamp(int(data["SentTimestamp"]) / 1000)
        if "ApproximateFirstReceiveTimestamp" in data:
            data["ApproximateFirstReceiveTimestamp"] = datetime.fromtimestamp(
                int(data["ApproximateFirstReceiveTimestamp"]) / 1000
            )
        if "ApproximateReceiveCount" in data:
            data["ApproximateReceiveCount"] = int(data["ApproximateReceiveCount"])
        if "SequenceNumber" in data:
            try:
                data["SequenceNumber"] = int(data["SequenceNumber"])
            except ValueError:
                pass  # fallback to str if conversion fails
        return data

class SQSMessageAttribute(BaseModel):
    stringValue: str|SkipJsonSchema[None] = None
    binaryValue: str | SkipJsonSchema[None] = None
    stringListValues: List[str] = Field(default_factory=list)
    binaryListValues: List[str] = Field(default_factory=list)
    dataType: str


class SQSRecord(BaseModel):
    eventSource: str| SkipJsonSchema[None] = None
    eventSourceARN: str| SkipJsonSchema[None] = None
    awsRegion: str| SkipJsonSchema[None] = None
    md5OfMessageAttributes: str | SkipJsonSchema[None] = None
    messageId: str
    receiptHandle: str
    body: str
    attributes: SQSAttributes | SkipJsonSchema[None] = None
    messageAttributes: Dict[str, SQSMessageAttribute]
    md5OfBody: str | SkipJsonSchema[None] = None

    def _safe_json_parse(self) -> Any:
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return self.body.strip()

    @computed_field
    @property
    def flat_message_attributes(self) -> Dict[str, str]:
        result = {}
        for key, attr in self.messageAttributes.items():
            val = attr.stringValue or attr.binaryValue
            if val is not None:
                result[key] = val
        return result
    
    @computed_field
    @property
    def parsed_body(self) -> Any:
        value = self._safe_json_parse()
        val_str = str(value).strip().lower()
        if val_str in {"true", "false", "null"}:
            return {"true": True, "false": False, "null": None}[val_str]
        try:
            if isinstance(value, str) and "." in value:
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return value

    @computed_field
    @property
    def dictBody(self) -> Optional[Dict[str, Any]]:
        return self.parsed_body if isinstance(self.parsed_body, dict) else None

    @computed_field
    @property
    def listBody(self) -> Optional[List[Any]]:
        return self.parsed_body if isinstance(self.parsed_body, list) else None

    @computed_field
    @property
    def intBody(self) -> Optional[int]:
        return self.parsed_body if isinstance(self.parsed_body, int) else None

    @computed_field
    @property
    def floatBody(self) -> Optional[float]:
        return self.parsed_body if isinstance(self.parsed_body, float) else None

    @computed_field
    @property
    def strBody(self) -> Optional[str]:
        return self.parsed_body if isinstance(self.parsed_body, str) else None

    @computed_field
    @property
    def boolBody(self) -> Optional[bool]:
        return self.parsed_body if isinstance(self.parsed_body, bool) else None

    @computed_field
    @property
    def model(self) -> QueueMessageModelType:
        model = self.flat_message_attributes.get("model", None)
        if not model: raise ValueError("Message attribute 'model' is required to identify the message type")
        return QueueMessageModelType(model)


class SQSEvent(BaseModel):
    Records: List[SQSRecord]

    @computed_field
    @property
    def message_count(self) -> int:
        """Number of messages received"""
        return len(self.Records)
    
    @computed_field
    @property
    def has_messages(self) -> bool:
        """Whether any messages were received"""
        return len(self.Records) > 0

    # Alias for backward compatibility with your existing code
    @computed_field
    @property
    def messages(self) -> List[SQSRecord]:
        """Alias for Messages field for backward compatibility"""
        return self.Records


class ReceiveMessageRequest(BaseModel):
    QueueUrl: QueueName
    AttributeNames: list[str] = Field(default=[], description="Attributes to retrieve (e.g., 'All', 'ApproximateReceiveCount')")
    MessageAttributeNames: list[str] = Field(default=[], description="Message attributes to retrieve (e.g., 'All', 'MyAttribute.*')")
    MaxNumberOfMessages: int= Field(default=10, description="Max messages to receive (1-10)")
    VisibilityTimeoutSeconds: int | SkipJsonSchema[None] = Field(default=None, description="Visibility timeout in seconds (0-43200)")
    WaitTimeSeconds: int = Field(default=0, description="Long polling wait time in seconds (0-20)")
    ReceiveRequestAttemptId: str | SkipJsonSchema[None] = Field(default=None, description="FIFO queue deduplication token")

    @model_validator(mode="after")
    def validate_fifo_requirements(self) -> "ReceiveMessageRequest":
        # If it's a FIFO queue, ReceiveRequestAttemptId should be provided for exactly-once processing
        if self.QueueUrl.value.endswith('.fifo') and self.ReceiveRequestAttemptId is None:
            # This is optional but recommended for FIFO queues
            pass
        return self


# ================================
# 📤 SENDING TO SQS
# ================================

class MessageAttributeDataType(str, Enum):
    STRING = "String"
    NUMBER = "Number"
    BINARY = "Binary"


class SendMessageAttribute(BaseModel):
    DataType: MessageAttributeDataType
    StringValue: str | SkipJsonSchema[None] = None
    BinaryValue: bytes | SkipJsonSchema[None] = None

    @model_validator(mode="after")
    def validate_content_by_datatype(self) -> "SendMessageAttribute":
        if self.DataType in [MessageAttributeDataType.STRING, MessageAttributeDataType.NUMBER]:
            if self.StringValue is None:
                raise ValueError(f"{self.DataType} requires 'StringValue'")
        elif self.DataType == MessageAttributeDataType.BINARY:
            if self.BinaryValue is None:
                raise ValueError("Binary requires 'BinaryValue'")
        return self
class SendMessageRequest(BaseModel):
    Queue: QueueName
    DelaySeconds: int = Field( default=0, ge=0, le=900)
    MessageAttributes: Dict[str, SendMessageAttribute] = {}

class BatchMessageRequest(BaseModel):
    DelaySeconds: int = Field( default=0, ge=0, le=900)
    MessageAttributes: Dict[str, SendMessageAttribute] | SkipJsonSchema[None] = None
    Body: BaseModel
    Id: str

class SQSSendMessageResponse(BaseModel):
    success: bool = Field(..., description="Whether the message was sent successfully")
    message_id: str = ''
    sequence_number: str|SkipJsonSchema[None] = None
    error: Optional[str] = None

class SQSBatchFailedMessage(BaseModel):
    Id: str
    Code: str
    Message: str|SkipJsonSchema[None]=None

class SQSBatchSuccessMessage(BaseModel):
    Id: str
    MessageID: str

class SQSBatchSendResponse(BaseModel):
    Success: List[SQSBatchSuccessMessage]
    Failed: List[SQSBatchFailedMessage]

class SendMessageBatchEntry(BaseModel):
    Id: str
    MessageBody: str
    DelaySeconds: int | SkipJsonSchema[None] = None
    MessageAttributes: Dict[str, SendMessageAttribute] | SkipJsonSchema[None] = None

class SendMessageBatchRequest(BaseModel):
    QueueUrl: QueueName
    Entries: List[SendMessageBatchEntry]

class DeleteMessageBatchEntry(BaseModel):
    Id: str
    ReceiptHandle: str

class DeleteMessageBatchRequest(BaseModel):
    QueueUrl: QueueName
    Entries: List[DeleteMessageBatchEntry]

class DeleteMessageBatchResultEntry(BaseModel):
    Id: str

class BatchResultErrorEntry(BaseModel):
    Id: str
    SenderFault: bool
    Code: str
    Message: Optional[str] = None

class DeleteMessageBatchResponse(BaseModel):
    Successful: List[DeleteMessageBatchResultEntry]
    Failed: List[BatchResultErrorEntry]


import botocore.exceptions
from functools import wraps

def catch_sqs_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except botocore.exceptions.ClientError as e:
            error = ErrorDetail(code=e.response['Error']['Code'])
            if error.code == "ReceiptHandleIsInvalid":
                error.message = "Invalid receipt handle"
            elif error.code == "QueueDoesNotExist":
                error.message = "Queue does not exist"
            elif error.code == "RequestThrottled":
                error.message = "Request throttled"
            elif error.code == "InvalidIdFormat":
                error.message = "Invalid ID format"
            elif error.code == "UnsupportedOperation":
                error.message = "Unsupported operation"
            elif error.code == "InvalidSecurity":
                error.message = "Invalid security token"
            elif error.code == "InvalidAddress":
                error.message = "Invalid address"
            elif error.code == "TooManyEntriesInBatchRequest":
                error.message = "Too many entries in batch request"
            elif error.code == "EmptyBatchRequest":
                error.message = "Empty batch request"
            elif error.code == "BatchEntryIdsNotDistinct":
                error.message = "Batch entry IDs must be distinct"
            elif error.code == "InvalidBatchEntryId":
                error.message = "Invalid batch entry ID"
            elif error.code == "InvalidMessageContents":
                error.message = "Invalid message contents"
            elif error.code == "OverLimit":
                error.message = "Over limit"
            elif error.code == "InvalidBatchEntryId":
                error.message = "Invalid batch entry ID"
            elif error.code == "InvalidBatchEntryId":
                error.message = "Invalid batch entry ID"
            elif error.code == "InvalidBatchEntryId":
                error.message = "Invalid batch entry ID"
            else:
                error.message = f"Unhandled SQS error: {error.code} - {e.response['Error']['Message']}"
            return DzgroError(errors=ErrorList(errors=[error]))
        except Exception as e:
            return DzgroError(errors=ErrorList(errors=[ErrorDetail(code=400, message=str(e))]))
    return wrapper


