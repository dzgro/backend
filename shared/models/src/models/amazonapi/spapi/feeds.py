from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, RootModel

from models.model import ErrorDetail

class ProcessingStatus(str, Enum):
    """Feed processing status."""
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    FATAL = "FATAL"
    IN_PROGRESS = "IN_PROGRESS"
    IN_QUEUE = "IN_QUEUE"

class CompressionAlgorithm(str, Enum):
    """Feed document compression algorithm."""
    GZIP = "GZIP"

class Feed(BaseModel):
    """Feed information."""
    feed_id: str = Field(..., alias="feedId")
    feed_type: str = Field(..., alias="feedType")
    marketplace_ids: Optional[List[str]] = Field(None, alias="marketplaceIds")
    created_time: datetime = Field(..., alias="createdTime")
    processing_status: ProcessingStatus = Field(..., alias="processingStatus")
    processing_start_time: Optional[datetime] = Field(None, alias="processingStartTime")
    processing_end_time: Optional[datetime] = Field(None, alias="processingEndTime")
    result_feed_document_id: Optional[str] = Field(None, alias="resultFeedDocumentId")

class FeedDocument(BaseModel):
    """Feed document information."""
    feed_document_id: str = Field(..., alias="feedDocumentId")
    url: str = Field(..., description="Presigned URL for the feed document")
    compression_algorithm: Optional[CompressionAlgorithm] = Field(None, alias="compressionAlgorithm")

class CreateFeedDocumentSpecification(BaseModel):
    """Specification for creating a feed document."""
    content_type: str = Field(..., alias="contentType")

class CreateFeedDocumentResponse(BaseModel):
    """Response for creating a feed document."""
    feed_document_id: str = Field(..., alias="feedDocumentId")
    url: str = Field(..., description="Presigned URL for uploading the feed")

class FeedOptions(RootModel[Dict[str, str]]):
    """Additional feed options."""
    pass

class CreateFeedSpecification(BaseModel):
    """Specification for creating a feed."""
    feed_type: str = Field(..., alias="feedType")
    marketplace_ids: List[str] = Field(..., alias="marketplaceIds")
    input_feed_document_id: str = Field(..., alias="inputFeedDocumentId")
    feed_options: Optional[FeedOptions] = Field(None, alias="feedOptions")

class CreateFeedResponse(BaseModel):
    """Response for creating a feed."""
    feed_id: str = Field(..., alias="feedId")

# Response models
class GetFeedsResponse(BaseModel):
    """Response for getting feeds."""
    feeds: List[Feed]
    next_token: Optional[str] = Field(None, alias="nextToken")

class ErrorList(BaseModel):
    """List of errors."""
    errors: List[ErrorDetail] 