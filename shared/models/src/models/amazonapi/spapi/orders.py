from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.model import ErrorDetail

class OrderStatus(str, Enum):
    """Order status values."""
    PENDING = "Pending"
    UNSHIPPED = "Unshipped"
    PARTIALLY_SHIPPED = "PartiallyShipped"
    SHIPPED = "Shipped"
    CANCELED = "Canceled"
    UNFULFILLABLE = "Unfulfillable"
    INVOICE_UNCONFIRMED = "InvoiceUnconfirmed"
    PENDING_AVAILABILITY = "PendingAvailability"

class FulfillmentChannel(str, Enum):
    """Fulfillment channel types."""
    MFN = "MFN"  # Merchant Fulfilled Network
    AFN = "AFN"  # Amazon Fulfilled Network

class PaymentMethod(str, Enum):
    """Payment method types."""
    COD = "COD"  # Cash on Delivery
    CVS = "CVS"  # Convenience Store
    OTHER = "Other"

class OrderType(str, Enum):
    """Order type values."""
    STANDARD_ORDER = "StandardOrder"
    LONG_LEAD_TIME_ORDER = "LongLeadTimeOrder"
    PREORDER = "Preorder"
    BACK_ORDER = "BackOrder"
    SOURCING_ON_DEMAND_ORDER = "SourcingOnDemandOrder"

class Money(BaseModel):
    """Currency type and amount."""
    currency_code: str = Field(..., alias="CurrencyCode")
    amount: str = Field(..., alias="Amount")

class Address(BaseModel):
    """Shipping address information."""
    name: str = Field(..., alias="Name")
    company_name: Optional[str] = Field(None, alias="CompanyName")
    address_line1: Optional[str] = Field(None, alias="AddressLine1")
    address_line2: Optional[str] = Field(None, alias="AddressLine2")
    address_line3: Optional[str] = Field(None, alias="AddressLine3")
    city: Optional[str] = Field(None, alias="City")
    county: Optional[str] = Field(None, alias="County")
    district: Optional[str] = Field(None, alias="District")
    state_or_region: Optional[str] = Field(None, alias="StateOrRegion")
    municipality: Optional[str] = Field(None, alias="Municipality")
    postal_code: Optional[str] = Field(None, alias="PostalCode")
    country_code: Optional[str] = Field(None, alias="CountryCode")
    phone: Optional[str] = Field(None, alias="Phone")
    address_type: Optional[str] = Field(None, alias="AddressType")

class BuyerTaxInfo(BaseModel):
    """Tax information about the buyer."""
    company_legal_name: Optional[str] = Field(None, alias="CompanyLegalName")
    taxing_region: Optional[str] = Field(None, alias="TaxingRegion")
    tax_classifications: Optional[List[Dict[str, str]]] = Field(None, alias="TaxClassifications")

class BuyerInfo(BaseModel):
    """Buyer information."""
    buyer_email: Optional[str] = Field(None, alias="BuyerEmail")
    buyer_name: Optional[str] = Field(None, alias="BuyerName")
    buyer_county: Optional[str] = Field(None, alias="BuyerCounty")
    buyer_tax_info: Optional[BuyerTaxInfo] = Field(None, alias="BuyerTaxInfo")
    purchase_order_number: Optional[str] = Field(None, alias="PurchaseOrderNumber")

class PaymentExecutionDetailItem(BaseModel):
    """Payment execution detail item."""
    payment: Money
    payment_method: str = Field(..., alias="PaymentMethod")

class Order(BaseModel):
    """Order information."""
    amazon_order_id: str = Field(..., alias="AmazonOrderId")
    seller_order_id: Optional[str] = Field(None, alias="SellerOrderId")
    purchase_date: datetime = Field(..., alias="PurchaseDate")
    last_update_date: datetime = Field(..., alias="LastUpdateDate")
    order_status: OrderStatus = Field(..., alias="OrderStatus")
    fulfillment_channel: Optional[FulfillmentChannel] = Field(None, alias="FulfillmentChannel")
    sales_channel: Optional[str] = Field(None, alias="SalesChannel")
    order_channel: Optional[str] = Field(None, alias="OrderChannel")
    ship_service_level: Optional[str] = Field(None, alias="ShipServiceLevel")
    order_total: Optional[Money] = Field(None, alias="OrderTotal")
    number_of_items_shipped: Optional[int] = Field(None, alias="NumberOfItemsShipped")
    number_of_items_unshipped: Optional[int] = Field(None, alias="NumberOfItemsUnshipped")
    payment_execution_detail: Optional[List[PaymentExecutionDetailItem]] = Field(None, alias="PaymentExecutionDetail")
    payment_method: Optional[PaymentMethod] = Field(None, alias="PaymentMethod")
    payment_method_details: Optional[List[str]] = Field(None, alias="PaymentMethodDetails")
    marketplace_id: Optional[str] = Field(None, alias="MarketplaceId")
    shipment_service_level_category: Optional[str] = Field(None, alias="ShipmentServiceLevelCategory")
    order_type: Optional[OrderType] = Field(None, alias="OrderType")
    earliest_ship_date: Optional[datetime] = Field(None, alias="EarliestShipDate")
    latest_ship_date: Optional[datetime] = Field(None, alias="LatestShipDate")
    earliest_delivery_date: Optional[datetime] = Field(None, alias="EarliestDeliveryDate")
    latest_delivery_date: Optional[datetime] = Field(None, alias="LatestDeliveryDate")
    is_business_order: Optional[bool] = Field(None, alias="IsBusinessOrder")
    is_prime: Optional[bool] = Field(None, alias="IsPrime")
    is_premium_order: Optional[bool] = Field(None, alias="IsPremiumOrder")
    is_global_express_enabled: Optional[bool] = Field(None, alias="IsGlobalExpressEnabled")
    shipping_address: Optional[Address] = Field(None, alias="ShippingAddress")
    buyer_info: Optional[BuyerInfo] = Field(None, alias="BuyerInfo")

class OrderItem(BaseModel):
    """Order item information."""
    asin: str = Field(..., alias="ASIN")
    seller_sku: Optional[str] = Field(None, alias="SellerSKU")
    order_item_id: str = Field(..., alias="OrderItemId")
    title: Optional[str] = Field(None, alias="Title")
    quantity_ordered: int = Field(..., alias="QuantityOrdered")
    quantity_shipped: Optional[int] = Field(None, alias="QuantityShipped")
    item_price: Optional[Money] = Field(None, alias="ItemPrice")
    shipping_price: Optional[Money] = Field(None, alias="ShippingPrice")
    item_tax: Optional[Money] = Field(None, alias="ItemTax")
    shipping_tax: Optional[Money] = Field(None, alias="ShippingTax")
    shipping_discount: Optional[Money] = Field(None, alias="ShippingDiscount")
    shipping_discount_tax: Optional[Money] = Field(None, alias="ShippingDiscountTax")
    promotion_discount: Optional[Money] = Field(None, alias="PromotionDiscount")
    promotion_discount_tax: Optional[Money] = Field(None, alias="PromotionDiscountTax")
    promotion_ids: Optional[List[str]] = Field(None, alias="PromotionIds")
    cod_fee: Optional[Money] = Field(None, alias="CODFee")
    cod_fee_discount: Optional[Money] = Field(None, alias="CODFeeDiscount")
    is_gift: Optional[str] = Field(None, alias="IsGift")
    condition_note: Optional[str] = Field(None, alias="ConditionNote")
    condition_id: Optional[str] = Field(None, alias="ConditionId")
    condition_subtype_id: Optional[str] = Field(None, alias="ConditionSubtypeId")
    scheduled_delivery_start_date: Optional[datetime] = Field(None, alias="ScheduledDeliveryStartDate")
    scheduled_delivery_end_date: Optional[datetime] = Field(None, alias="ScheduledDeliveryEndDate")

# Response models
class OrdersList(BaseModel):
    """List of orders with pagination information."""
    orders: List[Order] = Field(..., alias="Orders")
    next_token: Optional[str] = Field(None, alias="NextToken")
    last_updated_before: Optional[str] = Field(None, alias="LastUpdatedBefore")
    created_before: Optional[str] = Field(None, alias="CreatedBefore")

class OrderItemsList(BaseModel):
    """List of order items with pagination information."""
    order_items: List[OrderItem] = Field(..., alias="OrderItems")
    next_token: Optional[str] = Field(None, alias="NextToken")
    amazon_order_id: str = Field(..., alias="AmazonOrderId")

class GetOrdersResponse(BaseModel):
    """Response for get_orders operation."""
    payload: Optional[OrdersList] = None
    errors: Optional[List[ErrorDetail]] = None

class GetOrderResponse(BaseModel):
    """Response for get_order operation."""
    payload: Optional[Order] = None
    errors: Optional[List[ErrorDetail]] = None

class GetOrderItemsResponse(BaseModel):
    """Response for get_order_items operation."""
    payload: Optional[OrderItemsList] = None
    errors: Optional[List[ErrorDetail]] = None 