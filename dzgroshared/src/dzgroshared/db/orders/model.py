from pydantic import BaseModel, Field
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

class PaymentStatus(str, Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    PENDING_SETTLEMENT = "PENDING_SETTLEMENT"
    OVERDUE = "OVERDUE"

class ShippingStatus(str, Enum):
    DELIVERED = "DELIVERED"
    RETURNED = "RETURNED"
    PARTIAL_RETURNED = "PARTIAL_RETURNED"

class SettlementAmountType(BaseModel):
    amountdescription: str
    orderAmount: float|SkipJsonSchema[None] = None
    refundAmount: float|SkipJsonSchema[None] = None

class OrderItemSettlement(BaseModel):
    sku: str
    asin: str|SkipJsonSchema[None] = None
    image: str|SkipJsonSchema[None] = None
    amountTypes: list[SettlementAmountType]

class NonSkuSettlement(BaseModel):
    amountTypes: list[SettlementAmountType]

class OrderPaymentDetail(ObjectIdStr):
    orderid: str
    orderdate: datetime
    orderstatus: str
    paymentStatus: PaymentStatus|SkipJsonSchema[None] = None
    shippingStatus: ShippingStatus|SkipJsonSchema[None] = None
    orderTotal: float
    settlementTotal: float
    payoutPercentage: float
    items: list[OrderItemSettlement]
    nonSkuSettlements: NonSkuSettlement|SkipJsonSchema[None] = None

class OrderPaymentList(BaseModel):
    count: int|SkipJsonSchema[None] = None
    data: list[OrderPaymentDetail]

class PaymentStatusFacet(BaseModel):
    status: PaymentStatus
    count: int

class OrderPaymentFacets(BaseModel):
    total: int
    byStatus: list[PaymentStatusFacet]

class OrderPaymentRequest(BaseModel):
    dates: StartEndDate|SkipJsonSchema[None] = None
    paginator: Paginator

