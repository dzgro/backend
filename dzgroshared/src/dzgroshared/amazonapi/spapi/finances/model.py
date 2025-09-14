from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from dzgroshared.db.model import ErrorDetail

class Currency(BaseModel):
    """Currency type and amount."""
    currency_code: str = Field(..., alias="currencyCode", description="Three-digit currency code")
    currency_amount: float = Field(..., alias="currencyAmount", description="Monetary value")

class SellingPartnerMetadata(BaseModel):
    """Metadata describing the seller."""
    selling_partner_id: str = Field(..., alias="sellingPartnerId")
    account_type: str = Field(..., alias="accountType")
    marketplace_id: str = Field(..., alias="marketplaceId")

class RelatedIdentifier(BaseModel):
    """Related business identifier."""
    related_identifier_name: str = Field(..., alias="relatedIdentifierName")
    related_identifier_value: str = Field(..., alias="relatedIdentifierValue")

class MarketplaceDetails(BaseModel):
    """Information about the marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    marketplace_name: str = Field(..., alias="marketplaceName")

class Breakdown(BaseModel):
    """Breakdown of transaction amounts."""
    breakdown_type: str = Field(..., alias="breakdownType")
    breakdown_amount: Currency = Field(..., alias="breakdownAmount")
    breakdowns: Optional[List['Breakdown']] = None

class ProductContext(BaseModel):
    """Product-related context."""
    context_type: str = Field("ProductContext", alias="contextType")
    asin: Optional[str] = None
    sku: Optional[str] = None
    quantity_shipped: Optional[int] = Field(None, alias="quantityShipped")
    fulfillment_network: Optional[str] = Field(None, alias="fulfillmentNetwork")

class AmazonPayContext(BaseModel):
    """Amazon Pay-related context."""
    context_type: str = Field("AmazonPayContext", alias="contextType")
    store_name: Optional[str] = Field(None, alias="storeName")
    order_type: Optional[str] = Field(None, alias="orderType")
    channel: Optional[str] = None

class PaymentsContext(BaseModel):
    """Payments-related context."""
    context_type: str = Field("PaymentsContext", alias="contextType")
    payment_type: Optional[str] = Field(None, alias="paymentType")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    payment_reference: Optional[str] = Field(None, alias="paymentReference")
    payment_date: Optional[datetime] = Field(None, alias="paymentDate")

class Context(BaseModel):
    """Additional transaction information."""
    context_type: str = Field(..., alias="contextType")
    asin: Optional[str] = None
    sku: Optional[str] = None
    quantity_shipped: Optional[int] = Field(None, alias="quantityShipped")
    fulfillment_network: Optional[str] = Field(None, alias="fulfillmentNetwork")
    store_name: Optional[str] = Field(None, alias="storeName")
    order_type: Optional[str] = Field(None, alias="orderType")
    channel: Optional[str] = None
    payment_type: Optional[str] = Field(None, alias="paymentType")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    payment_reference: Optional[str] = Field(None, alias="paymentReference")
    payment_date: Optional[datetime] = Field(None, alias="paymentDate")

class Item(BaseModel):
    """Item in a transaction."""
    description: Optional[str] = None
    related_identifiers: Optional[List[RelatedIdentifier]] = Field(None, alias="relatedIdentifiers")
    total_amount: Optional[Currency] = Field(None, alias="totalAmount")
    breakdowns: Optional[List[Breakdown]] = None
    contexts: Optional[List[Context]] = None

class Transaction(BaseModel):
    """Financial transaction information."""
    selling_partner_metadata: SellingPartnerMetadata = Field(..., alias="sellingPartnerMetadata")
    related_identifiers: Optional[List[RelatedIdentifier]] = Field(None, alias="relatedIdentifiers")
    transaction_type: str = Field(..., alias="transactionType")
    transaction_id: str = Field(..., alias="transactionId")
    transaction_status: str = Field(..., alias="transactionStatus")
    description: Optional[str] = None
    posted_date: datetime = Field(..., alias="postedDate")
    total_amount: Currency = Field(..., alias="totalAmount")
    marketplace_details: MarketplaceDetails = Field(..., alias="marketplaceDetails")
    items: Optional[List[Item]] = None
    contexts: Optional[List[Context]] = None
    breakdowns: Optional[List[Breakdown]] = None

# Response models
class TransactionsPayload(BaseModel):
    """Payload containing transactions."""
    next_token: Optional[str] = Field(None, alias="nextToken")
    transactions: List[Transaction]

class ListTransactionsResponse(BaseModel):
    """Response for list_transactions operation."""
    payload: TransactionsPayload

class ErrorList(BaseModel):
    """List of errors."""
    errors: List[ErrorDetail] 