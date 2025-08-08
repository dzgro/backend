from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.model import ErrorDetail

class Condition(str, Enum):
    """Item condition types."""
    NEW = "New"
    USED = "Used"
    COLLECTIBLE = "Collectible"
    REFURBISHED = "Refurbished"
    CLUB = "Club"

class SubCondition(str, Enum):
    """Item subcondition types."""
    NEW = "New"
    MINT = "Mint"
    VERY_GOOD = "VeryGood"
    GOOD = "Good"
    ACCEPTABLE = "Acceptable"
    POOR = "Poor"
    CLUB = "Club"
    OEM = "OEM"
    WARRANTY = "Warranty"
    REFURBISHED_WARRANTY = "RefurbishedWarranty"
    REFURBISHED = "Refurbished"
    OPEN_BOX = "OpenBox"
    OTHER = "Other"

class FulfillmentType(str, Enum):
    """Fulfillment channel types."""
    AFN = "AFN"  # Fulfilled by Amazon
    MFN = "MFN"  # Fulfilled by Merchant

class MoneyType(BaseModel):
    """Currency type and amount."""
    currency_code: str = Field(..., alias="currencyCode")
    amount: float = Field(..., alias="amount")

class Points(BaseModel):
    """Amazon Points information."""
    points_number: Optional[int] = Field(None, alias="pointsNumber")
    points_monetary_value: Optional[MoneyType] = Field(None, alias="pointsMonetaryValue")

class Price(BaseModel):
    """Price information."""
    listing_price: MoneyType = Field(..., alias="listingPrice")
    shipping_price: Optional[MoneyType] = Field(None, alias="shippingPrice")
    points: Optional[Points] = None

class PostalCode(BaseModel):
    """Postal code information."""
    country_code: Optional[str] = Field(None, alias="countryCode")
    value: Optional[str] = None

class SampleLocation(BaseModel):
    """Location information."""
    postal_code: Optional[PostalCode] = Field(None, alias="postalCode")

class SegmentDetails(BaseModel):
    """Segment details."""
    glance_view_weight_percentage: Optional[float] = Field(None, alias="glanceViewWeightPercentage")
    sample_location: Optional[SampleLocation] = Field(None, alias="sampleLocation")

class Segment(BaseModel):
    """Segment information."""
    segment_details: Optional[SegmentDetails] = Field(None, alias="segmentDetails")

class Offer(BaseModel):
    """Offer information."""
    seller_id: str = Field(..., alias="sellerId")
    condition: Condition
    fulfillment_type: FulfillmentType = Field(..., alias="fulfillmentType")
    listing_price: MoneyType = Field(..., alias="listingPrice")
    shipping_price: Optional[MoneyType] = Field(None, alias="shippingPrice")
    points: Optional[Points] = None
    sub_condition: Optional[SubCondition] = Field(None, alias="subCondition")

class FeaturedOfferSegment(BaseModel):
    """Featured offer segment information."""
    segment_id: str = Field(..., alias="segmentId")
    segment_details: Optional[SegmentDetails] = Field(None, alias="segmentDetails")

class SegmentedFeaturedOffer(Offer):
    """Segmented featured offer information."""
    featured_offer_segments: List[FeaturedOfferSegment] = Field(..., alias="featuredOfferSegments")

class FeaturedBuyingOption(BaseModel):
    """Featured buying option information."""
    buying_option_type: str = Field(..., alias="buyingOptionType")
    segmented_featured_offers: List[SegmentedFeaturedOffer] = Field(..., alias="segmentedFeaturedOffers")

class ReferencePrice(BaseModel):
    """Reference price information."""
    name: str
    price: MoneyType

# Request models
class GetPricingRequest(BaseModel):
    """Request parameters for get_pricing operation."""
    marketplace_id: str = Field(..., alias="MarketplaceId")
    item_type: str = Field(..., alias="ItemType")  # Asin or Sku
    asins: Optional[List[str]] = Field(None, alias="Asins")
    skus: Optional[List[str]] = Field(None, alias="Skus")

class GetFeaturedOfferExpectedPriceBatchRequest(BaseModel):
    """Request parameters for get_featured_offer_expected_price_batch operation."""
    requests: List[Dict[str, Any]]

# Response models
class PriceResponse(BaseModel):
    """Response for a single item in get_pricing operation."""
    status: str
    seller_sku: Optional[str] = Field(None, alias="SellerSKU")
    asin: Optional[str] = Field(None, alias="ASIN")
    product: Optional[Dict[str, Any]] = Field(None, alias="Product")

class GetPricingResponse(BaseModel):
    """Response for get_pricing operation."""
    payload: Optional[List[PriceResponse]] = None
    errors: Optional[List[ErrorDetail]] = None

class FeaturedOfferExpectedPriceResponse(BaseModel):
    """Response for a single item in get_featured_offer_expected_price operation."""
    status: str
    body: Optional[Dict[str, Any]] = None
    errors: Optional[List[ErrorDetail]] = None

class GetFeaturedOfferExpectedPriceBatchResponse(BaseModel):
    """Response for get_featured_offer_expected_price_batch operation."""
    responses: List[FeaturedOfferExpectedPriceResponse] 