from pydantic import BaseModel,model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import ItemId, StartEndDate
from dzgroshared.db.enums import QueryTag
from typing import List, Union, Optional


class PerformancePeriod(ItemId):
    tag: QueryTag
    curr: StartEndDate
    pre: StartEndDate
    disabled: bool
    label: str = ''

    @model_validator(mode="after")
    def addLabel(self):
        self.label = f"{self.curr.label} vs {self.pre.label}"
        return self

class PerformancePeriodList(BaseModel):
    data: List[PerformancePeriod]