from dzgroshared.db.enums import CurrencyCode
from pydantic import BaseModel,Field, model_validator,ConfigDict
from pydantic.json_schema import SkipJsonSchema
from typing import Literal, Any

def snakeCaseToTitleCase():
    def camel(field_name: str):
        if field_name=="id": return "_id"
        first, *others = field_name.split('_')
        return ''.join([first.lower(), *map(str.title, others)])


    return ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: camel(field_name),
    )

CustomerKeys = Literal['name','email','contact']

class RazorpayEntity(BaseModel):
    entity: Literal['payment','subscription','order','card','invoice']

class Currency(BaseModel):
    currency: CurrencyCode

class Amount(BaseModel):
    amount: int

class RazorpayId(BaseModel):
    id: str

class Receipt(BaseModel):
    receipt: str

class Notes(BaseModel):
    notes: dict[str,str]|Any = {}

    @model_validator(mode="after")
    def setDefault(self):
        self.notes = self.notes if isinstance(self.notes, dict) and len(self.notes.keys())>0 else None
        return self

class RazorpayCountSkip(BaseModel):
    count: int = Field(default=10, lt=100)
    skip: int = Field(default=0)

class RazorpayPagination(RazorpayCountSkip):
    # model_config = ConfigDict(populate_by_name=True)
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: field_name.lower()
    )
    FROM: int
    TO: int

class ItemWithNameDescriptionCurrencyAmount(Currency, Amount):
    name: str
    description: str|SkipJsonSchema[None]=None

class ItemObject(BaseModel):
    item: ItemWithNameDescriptionCurrencyAmount


class RazorpayObject(BaseModel):
    key: str
    name: str="Dzgro"
    customer_id: str|SkipJsonSchema[None]=None
    prefill: dict[CustomerKeys,str]
    theme: dict[str,str] = {'color':'#3f51b5'}
    readonly: dict[CustomerKeys,bool]

class RazorpaySubscriptionObject(RazorpayObject):
    subscription_id: str

class RazorpayOrderObject(RazorpayObject):
    order_id: str
