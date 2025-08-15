from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dzgroshared.models.model import ErrorDetail


class IdentifierType(str, Enum):
    ASIN = "ASIN"
    EAN = "EAN"
    FNSKU = "FNSKU"
    GTIN = "GTIN"
    ISBN = "ISBN"
    JAN = "JAN"
    MINSAN = "MINSAN"
    SKU = "SKU"
    UPC = "UPC"


class IncludedData(str, Enum):
    summaries = "summaries"
    attributes = "attributes"
    issues = "issues"
    offers = "offers"
    fulfillmentAvailability = "fulfillmentAvailability"
    procurement = "procurement"
    relationships = "relationships"
    productTypes = "productTypes"


class StatusFilter(str, Enum):
    BUYABLE = "BUYABLE"
    DISCOVERABLE = "DISCOVERABLE"


class SortBy(str, Enum):
    sku = "sku"
    createdDate = "createdDate"
    lastUpdatedDate = "lastUpdatedDate"


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ImageVariant(str, Enum):
    """Image variant types."""
    MAIN = "MAIN"
    PT01 = "PT01"
    PT02 = "PT02"
    PT03 = "PT03"
    PT04 = "PT04"
    PT05 = "PT05"
    PT06 = "PT06"
    PT07 = "PT07"
    PT08 = "PT08"
    SWCH = "SWCH"

class ItemClassification(str, Enum):
    """Item classification types."""
    BASE_PRODUCT = "BASE_PRODUCT"
    OTHER = "OTHER"
    PRODUCT_BUNDLE = "PRODUCT_BUNDLE"
    VARIATION_PARENT = "VARIATION_PARENT"

class ItemImage(BaseModel):
    """Item image information."""
    variant: ImageVariant
    link: str
    height: int
    width: int

class ItemImagesByMarketplace(BaseModel):
    """Item images grouped by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    images: List[ItemImage]

class ItemIdentifier(BaseModel):
    """Item identifier information."""
    identifier_type: str = Field(..., alias="identifierType")
    identifier: str

class ItemIdentifiersByMarketplace(BaseModel):
    """Item identifiers grouped by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    identifiers: List[ItemIdentifier]

class ItemSalesRank(BaseModel):
    """Item sales rank information."""
    title: str
    rank: int
    link: Optional[str] = None

class ItemSalesRanksByMarketplace(BaseModel):
    """Item sales ranks grouped by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    ranks: List[ItemSalesRank]

class ItemProductTypeByMarketplace(BaseModel):
    """Item product type information by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    product_type: str = Field(..., alias="productType")

class ItemSummaryByMarketplace(BaseModel):
    """Item summary information by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    brand_name: Optional[str] = Field(None, alias="brandName")
    color_name: Optional[str] = Field(None, alias="colorName")
    item_name: Optional[str] = Field(None, alias="itemName")
    manufacturer: Optional[str] = None
    model_number: Optional[str] = Field(None, alias="modelNumber")
    size_name: Optional[str] = Field(None, alias="sizeName")
    style_name: Optional[str] = Field(None, alias="styleName")

class ItemBrowseClassification(BaseModel):
    """Item browse classification information."""
    display_name: str = Field(..., alias="displayName")
    classification_id: str = Field(..., alias="classificationId")

class ItemBrowseClassificationsByMarketplace(BaseModel):
    """Item browse classifications grouped by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    classifications: List[ItemBrowseClassification]

class ItemRelationship(BaseModel):
    """Item relationship information."""
    type: str
    variant: Optional[str] = None
    children: Optional[List[str]] = None
    parent: Optional[str] = None

class ItemRelationshipsByMarketplace(BaseModel):
    """Item relationships grouped by marketplace."""
    marketplace_id: str = Field(..., alias="marketplaceId")
    relationships: List[ItemRelationship]

class Item(BaseModel):
    """Item information."""
    asin: str
    attributes: Optional[Dict[str, Any]] = None
    dimensions: Optional[Dict[str, Any]] = None
    identifiers: Optional[List[ItemIdentifiersByMarketplace]] = None
    images: Optional[List[ItemImagesByMarketplace]] = None
    product_types: Optional[List[ItemProductTypeByMarketplace]] = Field(None, alias="productTypes")
    relationships: Optional[List[ItemRelationshipsByMarketplace]] = None
    sales_ranks: Optional[List[ItemSalesRanksByMarketplace]] = Field(None, alias="salesRanks")
    summaries: Optional[List[ItemSummaryByMarketplace]] = None
    classifications: Optional[List[ItemBrowseClassificationsByMarketplace]] = None

class BrandRefinement(BaseModel):
    """Brand refinement information."""
    number_of_results: int = Field(..., alias="numberOfResults")
    brand_name: str = Field(..., alias="brandName")

class ClassificationRefinement(BaseModel):
    """Classification refinement information."""
    number_of_results: int = Field(..., alias="numberOfResults")
    display_name: str = Field(..., alias="displayName")
    classification_id: str = Field(..., alias="classificationId")

class Refinements(BaseModel):
    """Search refinements."""
    brands: List[BrandRefinement]
    classifications: List[ClassificationRefinement]

class Pagination(BaseModel):
    """Pagination information."""
    next_token: Optional[str] = Field(None, alias="nextToken")
    previous_token: Optional[str] = Field(None, alias="previousToken")

# Response models
class ItemSearchResults(BaseModel):
    """Search results information."""
    number_of_results: int = Field(..., alias="numberOfResults")
    pagination: Pagination
    refinements: Refinements
    items: List[Item]

class GetCatalogItemResponse(BaseModel):
    """Response for get_catalog_item operation."""
    payload: Optional[Item] = None
    errors: Optional[List[ErrorDetail]] = None

class SearchCatalogItemsResponse(BaseModel):
    """Response for search_catalog_items operation."""
    payload: Optional[ItemSearchResults] = None
    errors: Optional[List[ErrorDetail]] = None
