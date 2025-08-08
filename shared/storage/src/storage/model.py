from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from typing import Union, Dict
from datetime import datetime
from enum import Enum

class S3Bucket(str, Enum):
    DZGRO = "dzgro"



class S3PutObjectModel(BaseModel):
    Bucket: S3Bucket = S3Bucket.DZGRO
    Key: str
    Body: Union[str, bytes]  # Required field
    ACL: str | SkipJsonSchema[None] = None
    CacheControl: str | SkipJsonSchema[None] = None
    ContentDisposition: str | SkipJsonSchema[None] = None
    ContentEncoding: str | SkipJsonSchema[None] = None
    ContentLanguage: str | SkipJsonSchema[None] = None
    ContentLength: int | SkipJsonSchema[None] = None
    ContentMD5: str | SkipJsonSchema[None] = None
    ContentType: str | SkipJsonSchema[None] = None
    Expires: datetime | SkipJsonSchema[None] = None
    GrantFullControl: str | SkipJsonSchema[None] = None
    GrantRead: str | SkipJsonSchema[None] = None
    GrantReadACP: str | SkipJsonSchema[None] = None
    GrantWriteACP: str | SkipJsonSchema[None] = None
    Metadata: Dict[str, str] | SkipJsonSchema[None] = None
    ServerSideEncryption: str | SkipJsonSchema[None] = None
    WebsiteRedirectLocation: str | SkipJsonSchema[None] = None
    SSECustomerAlgorithm: str | SkipJsonSchema[None] = None
    SSECustomerKey: str | SkipJsonSchema[None] = None
    SSECustomerKeyMD5: str | SkipJsonSchema[None] = None
    SSEKMSKeyId: str | SkipJsonSchema[None] = None
    SSEKMSEncryptionContext: str | SkipJsonSchema[None] = None
    BucketKeyEnabled: bool | SkipJsonSchema[None] = None
    RequestPayer: str | SkipJsonSchema[None] = None
    Tagging: str | SkipJsonSchema[None] = None
    ObjectLockMode: str | SkipJsonSchema[None] = None
    ObjectLockRetainUntilDate: datetime | SkipJsonSchema[None] = None
    ObjectLockLegalHoldStatus: str | SkipJsonSchema[None] = None

    class Config:
        arbitrary_types_allowed = True


class S3GetObjectModel(BaseModel):
    Bucket: S3Bucket = S3Bucket.DZGRO
    Key: str
    IfMatch: str | SkipJsonSchema[None] = None
    IfModifiedSince: datetime | SkipJsonSchema[None] = None
    IfNoneMatch: str | SkipJsonSchema[None] = None
    IfUnmodifiedSince: datetime | SkipJsonSchema[None] = None
    Range: str | SkipJsonSchema[None] = None
    ResponseCacheControl: str | SkipJsonSchema[None] = None
    ResponseContentDisposition: str | SkipJsonSchema[None] = None
    ResponseContentEncoding: str | SkipJsonSchema[None] = None
    ResponseContentLanguage: str | SkipJsonSchema[None] = None
    ResponseContentType: str | SkipJsonSchema[None] = None
    ResponseExpires: datetime | SkipJsonSchema[None] = None
    VersionId: str | SkipJsonSchema[None] = None
    SSECustomerAlgorithm: str | SkipJsonSchema[None] = None
    SSECustomerKey: str | SkipJsonSchema[None] = None
    SSECustomerKeyMD5: str | SkipJsonSchema[None] = None
    RequestPayer: str | SkipJsonSchema[None] = None
    PartNumber: int | SkipJsonSchema[None] = None
    ExpectedBucketOwner: str | SkipJsonSchema[None] = None
    ChecksumMode: str | SkipJsonSchema[None] = None

    class Config:
        arbitrary_types_allowed = True