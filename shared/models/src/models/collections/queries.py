from pydantic import BaseModel,model_validator
from models.model import ItemId
from models.enums import CollateTypeTag
from datetime import datetime

class QueryPeriod(BaseModel):
    start: datetime
    end: datetime
    label: str

    @model_validator(mode="before")
    def setLabel(cls, data):
        data['label'] = f'{data['start'].strftime("%b %d, %Y")} - {data['end'].strftime("%b %d, %Y")}'
        return data
class Query(ItemId):
    tag: CollateTypeTag
    curr: QueryPeriod
    pre: QueryPeriod
