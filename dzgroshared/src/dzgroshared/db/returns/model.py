from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime

class ReturnMetadata(BaseModel):
    accountId: str
    marketplace: str

class FileReturn(BaseModel):
    orderId:str =  Field(validation_alias='Order ID')
    orderDate:str =  Field(validation_alias='Order date')
    returnRequestDate:str =  Field(validation_alias='Return request date')
    returnRequestStatus:str =  Field(validation_alias='Return request status')
    amazonRmaId:str =  Field(validation_alias='Amazon RMA ID')
    merchantRmaId:str =  Field(validation_alias='Merchant RMA ID')
    labelType:str =  Field(validation_alias='Label type')
    labelCost:str =  Field(validation_alias='Label cost')
    currency:str =  Field(validation_alias='Currency code')
    carrier:str =  Field(validation_alias='Return carrier')
    trackingId:str =  Field(validation_alias='Tracking ID')
    labelToBePaidBy:str =  Field(validation_alias='Label to be paid by')
    azClaim:str =  Field(validation_alias='A-to-Z Claim')
    isPrime:str =  Field(validation_alias='Is prime')
    asin:str =  Field(validation_alias='ASIN')
    sku:str =  Field(validation_alias='Merchant SKU')
    itemName:str =  Field(validation_alias='Item Name')
    quantity:str =  Field(validation_alias='Return quantity')
    reason:str =  Field(validation_alias='Return Reason')
    inPolicy:str =  Field(validation_alias='In policy')
    returnType:str =  Field(validation_alias='Return type')
    resolution:str =  Field(validation_alias='Resolution')
    invoiceNumber:str =  Field(validation_alias='Invoice number')
    returnDeliveryDate:str =  Field(validation_alias='Return delivery date')
    orderAmount:str =  Field(validation_alias='Order Amount')
    orderQuantity:str =  Field(validation_alias='Order quantity')
    safeTActionReason:str =  Field(validation_alias='SafeT Action reason')
    safeTClaimId:str =  Field(validation_alias='SafeT claim id')
    safeTClaimState:str =  Field(validation_alias='SafeT claim state')
    safeTCreationDate:str =  Field(validation_alias='SafeT claim creation time')
    safeTRefundAmount:str =  Field(validation_alias='SafeT claim reimbursement amount')
    refundedAmount:str =  Field(validation_alias='Refunded Amount')
    category:str =  Field(validation_alias='Category')

class SafeT(BaseModel):
    reason: str
    state: str
    createdOn: datetime
    amount: float|SkipJsonSchema[None]=None

class ReturnItem(BaseModel):
    orderId: str
    sku: str
    returnDate: datetime
    atoZClaim: bool|SkipJsonSchema[None]=None
    returnQuantity: int
    reason: str
    returnType: str
    resolution: str
    returnDeliveryDate: datetime|SkipJsonSchema[None]=None
    orderQuantity: int
    safeT: SafeT|SkipJsonSchema[None]=None





