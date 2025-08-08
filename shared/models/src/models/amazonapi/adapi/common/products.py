from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ProductMetadata(BaseModel):
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: Optional[str] = Field(None, description="Product title")
    brand: Optional[str] = Field(None, description="Brand name")
    category: Optional[str] = Field(None, description="Product category")
    imageUrl: Optional[str] = Field(None, description="URL of the product image")
    price: Optional[float] = Field(None, description="Product price")
    currency: Optional[str] = Field(None, description="Currency code")
    availability: Optional[str] = Field(None, description="Availability status")
    rating: Optional[float] = Field(None, description="Product rating")
    reviewCount: Optional[int] = Field(None, description="Number of reviews")

class ProductMetadataListResponse(BaseModel):
    ProductMetadataList: List[ProductMetadata] = Field(..., description="List of product metadata")
    nextToken: Optional[str] = Field(None, description="Token for the next page of results, if available")

class ProductMetadataRequest(BaseModel):
    checkItemDetails: Optional[bool] = Field(default=False, description="Whether item details such as name, image, and price is required.")
    skus: Optional[List[str]] = Field(default=None, description="Specific SKUs to search for in the advertiser's inventory. Cannot use together with asins or searchStr input types.")
    checkEligibility: Optional[bool] = Field(default=False, description="Whether advertising eligibility info is required")
    isGlobalStoreSelection: Optional[bool] = Field(default=False, description="Return only GlobalStore listings")
    pageSize: int = Field(..., description="Number of items to be returned on this page index.", ge=1, le=300)
    locale: Optional[str] = Field(default=None, description="Optional locale for detail and eligibility response strings. Default to the marketplace locale.")
    asins: Optional[List[str]] = Field(default=None, description="Specific asins to search for in the advertiser's inventory. Cannot use together with skus or searchStr input types.")
    cursorToken: Optional[str] = Field(default=None, description="Pagination token used for the suggested sort type or for author merchant")
    adType: Optional[Literal["SP", "SB", "SD"]] = Field(default=None, description="Program type. Required if checks advertising eligibility.")
    searchStr: Optional[str] = Field(default=None, description="Specific string in the item title to search for in the advertiser's inventory. Case insensitive. Cannot use together with asins or skus input types.", max_length=200)
    pageIndex: int = Field(..., description="Index of the page to be returned; For author, this value will be ignored, should use cursorToken instead.", ge=0)
    sortOrder: Optional[Literal["ASC", "DESC"]] = Field(default="DESC", description="Sort order (has to be DESC for the suggested sort type).")
    sortBy: Optional[Literal["SUGGESTED", "CREATED_DATE"]] = Field(default=None, description="Sort option for the result. Only supports SP program type for sellers.")
