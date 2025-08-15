from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dzgroshared.models.model import ErrorDetail

class Requirements(str, Enum):
    LISTING = "LISTING"
    LISTING_PRODUCT_ONLY = "LISTING_PRODUCT_ONLY"
    LISTING_OFFER_ONLY = "LISTING_OFFER_ONLY"

class RequirementsEnforced(str, Enum):
    ENFORCED = "ENFORCED"
    NOT_ENFORCED = "NOT_ENFORCED"

class ProductType(BaseModel):
    name: str
    display_name: str = Field(..., alias="displayName")
    marketplace_ids: List[str] = Field(..., alias="marketplaceIds")

class ProductTypeList(BaseModel):
    product_types: List[ProductType] = Field(..., alias="productTypes")
    product_type_version: str = Field(..., alias="productTypeVersion")

class SchemaLink(BaseModel):
    link: Dict[str, Any]
    checksum: str

class ProductTypeVersion(BaseModel):
    version: str
    latest: bool
    release_candidate: Optional[bool] = Field(None, alias="releaseCandidate")

class PropertyGroup(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_names: Optional[List[str]] = Field(None, alias="propertyNames")

class ProductTypeDefinition(BaseModel):
    meta_schema: Optional[SchemaLink] = Field(None, alias="metaSchema")
    schemalink: SchemaLink = Field(..., alias="schema")
    requirements: Requirements
    requirements_enforced: RequirementsEnforced = Field(..., alias="requirementsEnforced")
    property_groups: Dict[str, PropertyGroup] = Field(..., alias="propertyGroups")
    locale: str
    marketplace_ids: List[str] = Field(..., alias="marketplaceIds")
    product_type: str = Field(..., alias="productType")
    display_name: str = Field(..., alias="displayName")
    product_type_version: ProductTypeVersion = Field(..., alias="productTypeVersion")

class GetDefinitionsProductTypeResponse(ProductTypeDefinition):
    errors: Optional[List[ErrorDetail]] = None 