from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from typing import Literal
from enum import Enum
from dzgroshared.db.model import ObjectIdStr, Paginator, StartEndDate

class SettlementOrderRefund(BaseModel):
    order: float|SkipJsonSchema[None] = None
    refund: float|SkipJsonSchema[None] = None

class SettlementDetailItem(SettlementOrderRefund):
    title: str

class SettlementDetail(BaseModel):
    title: Literal['Principal & Tax', 'Fees','Other Charges']
    items: list[SettlementDetailItem]

class OrderItem(BaseModel):
    sku: str
    asin: str
    imageUrl: str|SkipJsonSchema[None] = None
    quantity: int
    settlement: list[SettlementDetail]

class BasicOrderDetails(BaseModel):
    orderId: str
    status: str
    date: datetime

class Order(BasicOrderDetails):
    fulfillment: str
    revenue: float
    expenses: float
    netProceeds: float
    netProceedsPercent: float

class FacetFilter(BaseModel):
    title: str = Field(alias="_id")
    count: int

class OrderQueryFilters(BaseModel):
    status: list[str]|SkipJsonSchema[None] = None
    fulfillment: list[str]|SkipJsonSchema[None] = None
    months: list[str]|SkipJsonSchema[None] = None
    orderId: str|SkipJsonSchema[None] = None
    
class OrdersQuery(OrderQueryFilters):
    paginator: Paginator
    loadfilters: bool = True


class OrderFilterValue(BaseModel):
    applied: list[str]
    values: list[FacetFilter]

class OrderFilters(BaseModel):
    status: OrderFilterValue
    fulfillment: OrderFilterValue
    months: OrderFilterValue

class OrderResult(BaseModel):
    orders: list[Order]
    filters: OrderFilters|SkipJsonSchema[None] = None
    count: int

class OrderItemPrice(BaseModel):
    productPrice: float
    productTax: float
    shippingPrice: float|SkipJsonSchema[None] = None
    shippingTax: float|SkipJsonSchema[None] = None
    giftWrapPrice: float|SkipJsonSchema[None] = None
    giftWrapTax: float|SkipJsonSchema[None] = None
    shipPromotionDiscount: float|SkipJsonSchema[None] = None
    itemPromotionDiscount: float|SkipJsonSchema[None] = None

class OrderItems(BasicOrderDetails):
    orderId: str
    items: list[OrderItem]
    settlement: dict[str,float]

class DbOrder(ObjectIdStr):
    orderid: str
    originalorderid: str|SkipJsonSchema[None]=None
    orderdate:datetime
    date: datetime
    orderstatus:str
    city:str|SkipJsonSchema[None]=None
    state:str|SkipJsonSchema[None]=None
    code:str|SkipJsonSchema[None]=None
    country:str|SkipJsonSchema[None]=None
    fulfillment:str
    isbusinessorder:bool|SkipJsonSchema[None]=None
    
class DbOrderItem(BaseModel):
    order: str
    date: datetime
    orderitemid: str|SkipJsonSchema[None]=None
    itemstatus:str|SkipJsonSchema[None]=None
    sku: str
    asin: str
    quantity:int = 0
    revenue: float = 0
    price: float = 0
    tax: float = 0
    shippingprice: float|SkipJsonSchema[None]=None
    shippingtax: float|SkipJsonSchema[None]=None
    giftwrapprice: float|SkipJsonSchema[None]=None
    giftwraptax: float|SkipJsonSchema[None]=None
    itempromotiondiscount: float|SkipJsonSchema[None]=None
    shippromotiondiscount: float|SkipJsonSchema[None]=None

# Payment Reconciliation Models

class OrderPaymentStatus(str, Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    PENDING_SETTLEMENT = "Pending Settlement"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"
    
    @staticmethod
    def list():
        return [x.value for x in OrderPaymentStatus]
    
class OrderPaymentSettlementFacet(str,Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    PENDING_SETTLEMENT = "Pending Settlement"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"
    TOTAL = "Total Orders"
    

class OrderShippingStatus(str, Enum):
    DELIVERED = "Delivered"
    RETURNED = "Returned"
    PARTIAL_RETURNED = "Partial Returned"
    CANCELLED = "Cancelled"
    
    @staticmethod
    def list():
        return [x.value for x in OrderShippingStatus]
    

class OrderShippingStatusSettlementFacet(str,Enum):
    DELIVERED = "Delivered"
    RETURNED = "Returned"
    PARTIAL_RETURNED = "Partial Returned"
    CANCELLED = "Cancelled"
    TOTAL = "Total Orders"
    
class SettlementAmountDescription(BaseModel):
    title:str
    orderAmount: float|SkipJsonSchema[None] = None
    refundAmount: float|SkipJsonSchema[None] = None

class SettlementAmountType(BaseModel):
    title: str
    rowSpan: int
    items: list[SettlementAmountDescription]
    
    @model_validator(mode="after")
    def setRowSpan(self):
        self.rowSpan = max(self.rowSpan, 1)
        return self
    
class OrderProduct(BaseModel):
    sku: str
    asin: str
    image: str|SkipJsonSchema[None] = None
    

class OrderItemSettlement(BaseModel):
    product: OrderProduct|SkipJsonSchema[None]=None
    rowSpan: int
    settlements: list[SettlementAmountType]
    
    @model_validator(mode="after")
    def setRowSpan(self):
        self.rowSpan = max(self.rowSpan, 1)
        return self
    
class OrderPaymentItemsDetail(BaseModel):
    columns: list[str]
    rows: list[OrderItemSettlement]

class OrderPaymentDetail(BaseModel):
    orderid: str
    orderdate: datetime
    fulfillment:str
    paymentStatus: OrderPaymentStatus
    shippingStatus: OrderShippingStatus
    revenue: float
    settlement: float
    payoutPercent: str
    items: OrderPaymentItemsDetail

class OrderPaymentList(BaseModel):
    data: list[OrderPaymentDetail]
    dates: StartEndDate

class PaymentStatusFacet(BaseModel):
    title: OrderPaymentSettlementFacet
    count: int
    
class OrderShippingStatusFacet(BaseModel):
    title: OrderShippingStatusSettlementFacet
    count: int
    

class OrderPaymentFacets(BaseModel):
    count: int
    paymentStatuses: list[PaymentStatusFacet]
    shippingStatuses: list[OrderShippingStatusFacet]

class OrderPaymentRequest(BaseModel):
    dates: StartEndDate|SkipJsonSchema[None]=None
    paginator: Paginator
    paymentStatus: OrderPaymentSettlementFacet|SkipJsonSchema[None]=None
    shippingStatus: OrderShippingStatusSettlementFacet|SkipJsonSchema[None]=None

class OrderPaymentFacetRequest(BaseModel):
    paymentStatus: OrderPaymentSettlementFacet|SkipJsonSchema[None]=None
    shippingStatus: OrderShippingStatusSettlementFacet|SkipJsonSchema[None]=None
    dates: StartEndDate|SkipJsonSchema[None]=None

