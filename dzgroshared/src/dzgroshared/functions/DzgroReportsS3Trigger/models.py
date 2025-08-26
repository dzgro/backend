from enum import Enum
from dzgroshared.models.enums import S3Bucket
from pydantic import BaseModel, model_validator

class S3FileType(str, Enum):
    PARQUET = "PARQUET"
    XLSX = "XLSX"
    CSV = "CSV"

class S3TriggerType(str, Enum):
    PUT = "ObjectCreated:Put"
    DELETE = ""


class Bucket(BaseModel):
    name: str
    arn: str

class S3Object(BaseModel):
    key: str
    size: int
    filetype: S3FileType

    @model_validator(mode="before")
    def setFileType(cls, data: dict):
        if data['key'].endswith('.parquet'): data['filetype'] = S3FileType.PARQUET
        elif data['key'].endswith('.xlsx'): data['filetype'] = S3FileType.XLSX
        elif data['key'].endswith('.csv'): data['filetype'] = S3FileType.CSV
        else: raise ValueError("Invalid File Type")
        return data


class S3TriggerDetails(BaseModel):
    bucket: Bucket
    object: S3Object

class S3TriggerObject(BaseModel):
    uid: str
    marketplace: str
    reporttype: str
    reportid: str
    eventName: str
    s3: S3TriggerDetails
    triggerType: S3TriggerType

    @model_validator(mode="before")
    def setDetails(cls, data: dict):
        data['triggerType'] = S3TriggerType.PUT if data['eventName']=='ObjectCreated:Put' else S3TriggerType.DELETE
        splitted = tuple(data['s3']['object']['key'].split('/'))
        if len(splitted)!=5: raise ValueError("Invalid File Name")
        data['uid'],data['marketplace'],data['reporttype'],data['reportid'],filename = splitted
        return data