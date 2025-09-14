
from dzgroshared.db.enums import DzgroReportType
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class DzgroReportSpecification(BaseModel):
    id: DzgroReportType = Field(alias="_id")
    description: list[str]
    maxdays: int|SkipJsonSchema[None]=None
    comingsoon: bool = False

class DzgroReportSpecificationWithProjection(DzgroReportSpecification):
    projection: dict[str, str]