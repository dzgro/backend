from typing import List, Optional, Dict, Any
from models.amazonapi.spapi.reports import ProcessingStatus
from pydantic import BaseModel, Field
from models.model import ErrorDetail

# --- Query Models ---

class CreateQueryRequest(BaseModel):
    query: str


class CreateQueryResponse(BaseModel):
    query_id: str = Field(..., alias="queryId")
    status: str
    errors: Optional[List[ErrorDetail]] = None

class GetQueryResponse(BaseModel):
    query_id: str = Field(..., alias="queryId")
    query: str
    status: str
    created_time: str = Field(..., alias="createdTime")
    updated_time: str = Field(..., alias="updatedTime")
    errors: Optional[List[ErrorDetail]] = None

class ListQueriesResponse(BaseModel):
    queries: List[GetQueryResponse]
    next_token: Optional[str] = Field(None, alias="nextToken")
    errors: Optional[List[ErrorDetail]] = None

class CancelQueryResponse(BaseModel):
    query_id: str = Field(..., alias="queryId")
    status: str
    errors: Optional[List[ErrorDetail]] = None

# --- Query Result Models ---

class GetQueryResultResponse(BaseModel):
    query_id: str = Field(..., alias="queryId")
    status: ProcessingStatus
    result_document_id: Optional[str] = Field(None, alias="resultDocumentId")
    errors: Optional[List[ErrorDetail]] = None

class GetQueryResultDocumentResponse(BaseModel):
    result_document_id: str = Field(..., alias="resultDocumentId")
    url: str
    expires_at: str = Field(..., alias="expiresAt")
    errors: Optional[List[ErrorDetail]] = None

# --- Schema Models ---

class SchemaField(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: Optional[bool] = None
    enum_values: Optional[List[str]] = Field(None, alias="enumValues")

class GetSchemaResponse(BaseModel):
    schema_name: str = Field(..., alias="schemaName")
    fields: List[SchemaField]
    description: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None

class ListSchemasResponse(BaseModel):
    schemas: List[str]
    next_token: Optional[str] = Field(None, alias="nextToken")
    errors: Optional[List[ErrorDetail]] = None 