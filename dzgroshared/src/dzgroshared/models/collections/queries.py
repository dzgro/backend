from pydantic import BaseModel,model_validator
from dzgroshared.models.model import ItemId
from dzgroshared.models.enums import CollateTypeTag
from datetime import datetime

class QueryPeriod(BaseModel):
    start: datetime
    end: datetime
    label: str = ''

    @model_validator(mode="after")
    def setLabel(self):
        self.label = f'{self.start.strftime("%b %d, %Y")} - {self.end.strftime("%b %d, %Y")}'
        return self
class Query(ItemId):
    tag: CollateTypeTag
    curr: QueryPeriod
    pre: QueryPeriod
