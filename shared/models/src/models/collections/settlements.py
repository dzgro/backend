from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from typing import Literal

AmountType = Literal['ItemTCS',"Cost of Advertising","Other Transactions","Amazon Fees","Promotion","ItemFees","ItemPrice","other-transaction","ItemTDS","Other"]
TransactionType = Literal["Refund","SAFE-T Reimbursement","Other","other-transaction","ServiceFee","Cancellation","Order"]


class Settlement(BaseModel):
    settlementid: str
    amounttype: str
    transactiontype: str
    startdate:datetime|SkipJsonSchema[None]=None
    enddate:datetime|SkipJsonSchema[None]=None
    depositdate:datetime|SkipJsonSchema[None]=None
    totalamount:float|SkipJsonSchema[None]=None
    orderid: str|SkipJsonSchema[None]=None
    orderitemid: str|SkipJsonSchema[None]=None
    sku: str|SkipJsonSchema[None]=None
    date: datetime|SkipJsonSchema[None]=None
    amountdescription: str|SkipJsonSchema[None]=None
    amount:float

    # @model_validator(mode='after')
    # def setTax(self):
    #     self.isTax = any(taxIdentifier in self.amountdescription.lower() for taxIdentifier in ['tds', 'gst', 'tcs', 'tax']) if self.amountdescription else None
    #     return self
    