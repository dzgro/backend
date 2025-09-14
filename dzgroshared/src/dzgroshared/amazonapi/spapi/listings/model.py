from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Enums
class ConditionType(str, Enum):
    NEW_NEW = "new_new"
    NEW_OPEN_BOX = "new_open_box"
    NEW_OEM = "new_oem"
    REFURBISHED_REFURBISHED = "refurbished_refurbished"
    USED_LIKE_NEW = "used_like_new"
    USED_VERY_GOOD = "used_very_good"
    USED_GOOD = "used_good"
    USED_ACCEPTABLE = "used_acceptable"
    COLLECTIBLE_LIKE_NEW = "collectible_like_new"
    COLLECTIBLE_VERY_GOOD = "collectible_very_good"
    COLLECTIBLE_GOOD = "collectible_good"
    COLLECTIBLE_ACCEPTABLE = "collectible_acceptable"
    CLUB_CLUB = "club_club"

class ListingStatus(str, Enum):
    BUYABLE = "BUYABLE"
    DISCOVERABLE = "DISCOVERABLE"

class IssueSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class OfferType(str, Enum):
    B2C = "B2C"
    B2B = "B2B"

class RequirementsType(str, Enum):
    LISTING = "LISTING"
    LISTING_PRODUCT_ONLY = "LISTING_PRODUCT_ONLY"
    LISTING_OFFER_ONLY = "LISTING_OFFER_ONLY"

class SubmissionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    INVALID = "INVALID"
    VALID = "VALID"

# Models
class ItemImage(BaseModel):
    link: str
    height: int
    width: int

class ItemSummaryByMarketplace(BaseModel):
    marketplace_id: str = Field(..., alias="marketplaceId")
    asin: Optional[str] = None
    product_type: Optional[str] = Field(None, alias="productType")
    condition_type: Optional[ConditionType] = Field(None, alias="conditionType")
    status: List[ListingStatus]
    item_name: Optional[str] = Field(None, alias="itemName")
    created_date: datetime = Field(..., alias="createdDate")
    last_updated_date: datetime = Field(..., alias="lastUpdatedDate")
    main_image: Optional[ItemImage] = Field(None, alias="mainImage")
    fn_sku: Optional[str] = Field(None, alias="fnSku")

class Money(BaseModel):
    currency_code: str = Field(..., alias="currencyCode")
    amount: str

class Audience(BaseModel):
    value: str
    display_name: Optional[str] = Field(None, alias="displayName")

class ItemOfferByMarketplace(BaseModel):
    marketplace_id: str = Field(..., alias="marketplaceId")
    offer_type: OfferType = Field(..., alias="offerType")
    price: Money
    audience: Optional[Audience] = None

class FulfillmentAvailability(BaseModel):
    fulfillment_channel_code: str = Field(..., alias="fulfillmentChannelCode")
    quantity: Optional[int] = None

class Issue(BaseModel):
    code: str
    message: str
    severity: IssueSeverity
    attribute_names: Optional[List[str]] = Field(None, alias="attributeNames")

class ItemRelationshipsByMarketplace(BaseModel):
    marketplace_id: str = Field(..., alias="marketplaceId")
    relationships: List[Dict[str, Any]]

class ItemProductTypeByMarketplace(BaseModel):
    marketplace_id: str = Field(..., alias="marketplaceId")
    product_type: str = Field(..., alias="productType")

class Item(BaseModel):
    sku: str
    summaries: Optional[List[ItemSummaryByMarketplace]] = None
    attributes: Optional[Dict[str, Any]] = None
    issues: Optional[List[Issue]] = None
    offers: Optional[List[ItemOfferByMarketplace]] = None
    fulfillment_availability: Optional[List[FulfillmentAvailability]] = Field(None, alias="fulfillmentAvailability")
    procurement: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[ItemRelationshipsByMarketplace]] = None
    product_types: Optional[List[ItemProductTypeByMarketplace]] = Field(None, alias="productTypes")

class Pagination(BaseModel):
    next_token: Optional[str] = Field(None, alias="nextToken")
    previous_token: Optional[str] = Field(None, alias="previousToken")

class ItemSearchResults(BaseModel):
    number_of_results: int = Field(..., alias="numberOfResults")
    pagination: Optional[Pagination] = None
    items: List[Item]

# Request models
class ListingsItemPutRequest(BaseModel):
    product_type: str = Field(..., alias="productType")
    requirements: Optional[RequirementsType] = None
    attributes: Dict[str, Any]

class PatchOperation(BaseModel):
    op: str
    path: str
    value: Any

class ListingsItemPatchRequest(BaseModel):
    product_type: str = Field(..., alias="productType")
    patches: List[PatchOperation]

# Response models
class ListingsItemSubmissionResponse(BaseModel):
    sku: str
    status: SubmissionStatus
    submission_id: str = Field(..., alias="submissionId")
    issues: Optional[List[Issue]] = None
    identifiers: Optional[List[Dict[str, Any]]] = None

class GetListingsItemResponse(BaseModel):
    sku: str
    summaries: Optional[List[ItemSummaryByMarketplace]] = None
    attributes: Optional[Dict[str, Any]] = None
    issues: Optional[List[Issue]] = None
    offers: Optional[List[ItemOfferByMarketplace]] = None
    fulfillment_availability: Optional[List[FulfillmentAvailability]] = Field(None, alias="fulfillmentAvailability")
    procurement: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[ItemRelationshipsByMarketplace]] = None
    product_types: Optional[List[str]] = Field(None, alias="productTypes")
    errors: Optional[List[dict]] = None

class SearchListingsItemsResponse(BaseModel):
    items: Optional[ItemSearchResults] = None
    errors: Optional[List[dict]] = None 