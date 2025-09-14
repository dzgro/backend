from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from enum import Enum
from datetime import datetime
from typing import List
from dzgroshared.db.model import ErrorDetail
from dzgroshared.models.amazonapi.spapi.reports import ProcessingStatus

class ErrorList(BaseModel):
    """A list of error responses returned when a request is unsuccessful."""
    errors: List[ErrorDetail] = Field(description="Error response returned when the request is unsuccessful.")


class Pagination(BaseModel):
    """Pagination information for query results."""
    nextToken: str | SkipJsonSchema[None] = None


class DataKioskQueryResponse(BaseModel):
    """Detailed information about the query."""
    queryId: str = Field(description="The query identifier. This identifier is unique only in combination with a selling partner account ID.")
    query: str = Field(description="The submitted query.")
    createdTime: datetime = Field(description="The date and time when the query was created, in ISO 8601 date time format.")
    processingStatus: ProcessingStatus = Field(description="The processing status of the query.")
    processingStartTime: datetime | SkipJsonSchema[None] = None
    processingEndTime: datetime | SkipJsonSchema[None] = None
    dataDocumentId: str | SkipJsonSchema[None] = None
    errorDocumentId: str | SkipJsonSchema[None] = None
    pagination: Pagination | SkipJsonSchema[None] = None


class DataKioskCreateQuerySpecification(BaseModel):
    """Information required to create the query."""
    query: str = Field(description="The GraphQL query to submit. A query must be at most 8000 characters after unnecessary whitespace is removed.")
    paginationToken: str | SkipJsonSchema[None] = None


class DataKioskCreateQueryResponse(BaseModel):
    """The response for the createQuery operation."""
    queryId: str = Field(description="The identifier for the query. This identifier is unique only in combination with a selling partner account ID.")


class GetQueriesResponse(BaseModel):
    """The response for the getQueries operation."""
    queries: List[DataKioskQueryResponse] = Field(description="The Data Kiosk queries.")
    pagination: Pagination | SkipJsonSchema[None] = None


class DataKioskDocumentResponse(BaseModel):
    """The response for the getDocument operation."""
    documentId: str = Field(description="The identifier for the Data Kiosk document. This identifier is unique only in combination with a selling partner account ID.")
    documentUrl: str = Field(description="A presigned URL that can be used to retrieve the Data Kiosk document. This URL expires after 5 minutes.")


# Request/Response Models for API purposes
class GetQueriesRequest(BaseModel):
    """Request model for getQueries operation."""
    processingStatuses: List[ProcessingStatus] | SkipJsonSchema[None] = None
    pageSize: int | SkipJsonSchema[None] = Field(default=10, ge=1, le=100)
    createdSince: datetime | SkipJsonSchema[None] = None
    createdUntil: datetime | SkipJsonSchema[None] = None
    paginationToken: str | SkipJsonSchema[None] = None


class DataKioskCreateQueryRequest(BaseModel):
    """Request model for createQuery operation."""
    body: DataKioskCreateQuerySpecification


# Response wrapper for error handling
class DataKioskApiResponse(BaseModel):
    """Generic response wrapper for Data Kiosk API operations."""
    success: bool = True
    data: dict | SkipJsonSchema[None] = None
    errors: List[ErrorDetail] | SkipJsonSchema[None] = None
    statusCode: int | SkipJsonSchema[None] = None


class DataKioskErrorResponse(BaseModel):
    """Error response wrapper."""
    success: bool = False
    errors: List[ErrorDetail]
    statusCode: int 