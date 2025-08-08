from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.model import ErrorDetail

class ContentType(str, Enum):
    EBC = "EBC"
    EMC = "EMC"

class ContentStatus(str, Enum):
    APPROVED = "APPROVED"
    DRAFT = "DRAFT"
    REJECTED = "REJECTED"
    SUBMITTED = "SUBMITTED"

class ContentBadge(str, Enum):
    BULK = "BULK"
    GENERATED = "GENERATED"
    LAUNCHPAD = "LAUNCHPAD"
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"

class IncludedDataSet(str, Enum):
    CONTENTS = "CONTENTS"
    METADATA = "METADATA"

class LanguageTag(str, Enum):
    EN_US = "en-US"
    EN_GB = "en-GB"
    DE_DE = "de-DE"
    FR_FR = "fr-FR"
    IT_IT = "it-IT"
    ES_ES = "es-ES"
    # Add more as needed

class ContentMetadata(BaseModel):
    name: str
    marketplace_id: str = Field(..., alias="marketplaceId")
    status: ContentStatus
    badge_set: List[ContentBadge] = Field(..., alias="badgeSet")
    update_time: str = Field(..., alias="updateTime")

class ContentMetadataRecord(BaseModel):
    content_reference_key: str = Field(..., alias="contentReferenceKey")
    content_metadata: ContentMetadata = Field(..., alias="contentMetadata")

class GetContentDocumentResponse(BaseModel):
    content_record: Dict[str, Any] = Field(..., alias="contentRecord")
    warnings: Optional[List[ErrorDetail]] = None
    errors: Optional[List[ErrorDetail]] = None

class PostContentDocumentRequest(BaseModel):
    content_document: Dict[str, Any] = Field(..., alias="contentDocument")

class PostContentDocumentResponse(BaseModel):
    content_reference_key: str = Field(..., alias="contentReferenceKey")
    warnings: Optional[List[ErrorDetail]] = None
    errors: Optional[List[ErrorDetail]] = None

class SearchContentDocumentsResponse(BaseModel):
    content_metadata_records: List[ContentMetadataRecord] = Field(..., alias="contentMetadataRecords")
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    errors: Optional[List[ErrorDetail]] = None 