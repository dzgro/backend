from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dzgroshared.models.model import ErrorDetail

class ResearchDuration(str, Enum):
    """Duration of research for inventory quantities."""
    SHORT_TERM = "researchingQuantityInShortTerm"  # 1-10 days
    MID_TERM = "researchingQuantityInMidTerm"  # 11-20 days
    LONG_TERM = "researchingQuantityInLongTerm"  # 21+ days

class GranularityType(str, Enum):
    """Granularity type for inventory aggregation."""
    MARKETPLACE = "Marketplace"

class Granularity(BaseModel):
    """Granularity at which inventory data is aggregated."""
    granularity_type: GranularityType = Field(..., alias="granularityType")
    granularity_id: str = Field(..., alias="granularityId")

class ReservedQuantity(BaseModel):
    """Reserved inventory quantities."""
    total_reserved_quantity: Optional[int] = Field(None, alias="totalReservedQuantity")
    pending_customer_order_quantity: Optional[int] = Field(None, alias="pendingCustomerOrderQuantity")
    pending_transshipment_quantity: Optional[int] = Field(None, alias="pendingTransshipmentQuantity")
    fc_processing_quantity: Optional[int] = Field(None, alias="fcProcessingQuantity")

class ResearchingQuantityEntry(BaseModel):
    """Entry for researching quantity breakdown."""
    name: ResearchDuration
    quantity: int

class ResearchingQuantity(BaseModel):
    """Quantities being researched."""
    total_researching_quantity: Optional[int] = Field(None, alias="totalResearchingQuantity")
    researching_quantity_breakdown: Optional[List[ResearchingQuantityEntry]] = Field(None, alias="researchingQuantityBreakdown")

class UnfulfillableQuantity(BaseModel):
    """Unfulfillable inventory quantities."""
    total_unfulfillable_quantity: Optional[int] = Field(None, alias="totalUnfulfillableQuantity")
    customer_damaged_quantity: Optional[int] = Field(None, alias="customerDamagedQuantity")
    warehouse_damaged_quantity: Optional[int] = Field(None, alias="warehouseDamagedQuantity")
    distributor_damaged_quantity: Optional[int] = Field(None, alias="distributorDamagedQuantity")
    carrier_damaged_quantity: Optional[int] = Field(None, alias="carrierDamagedQuantity")
    defective_quantity: Optional[int] = Field(None, alias="defectiveQuantity")
    expired_quantity: Optional[int] = Field(None, alias="expiredQuantity")

class InventoryDetails(BaseModel):
    """Detailed inventory information."""
    fulfillable_quantity: Optional[int] = Field(None, alias="fulfillableQuantity")
    inbound_working_quantity: Optional[int] = Field(None, alias="inboundWorkingQuantity")
    inbound_shipped_quantity: Optional[int] = Field(None, alias="inboundShippedQuantity")
    inbound_receiving_quantity: Optional[int] = Field(None, alias="inboundReceivingQuantity")
    reserved_quantity: Optional[ReservedQuantity] = Field(None, alias="reservedQuantity")
    researching_quantity: Optional[ResearchingQuantity] = Field(None, alias="researchingQuantity")
    unfulfillable_quantity: Optional[UnfulfillableQuantity] = Field(None, alias="unfulfillableQuantity")

class InventorySummary(BaseModel):
    """Summary of inventory for a specific item."""
    asin: Optional[str] = None
    fn_sku: Optional[str] = Field(None, alias="fnSku")
    seller_sku: Optional[str] = Field(None, alias="sellerSku")
    condition: Optional[str] = None
    inventory_details: Optional[InventoryDetails] = Field(None, alias="inventoryDetails")
    last_updated_time: Optional[datetime] = Field(None, alias="lastUpdatedTime")
    product_name: Optional[str] = Field(None, alias="productName")
    total_quantity: Optional[int] = Field(None, alias="totalQuantity")
    stores: Optional[List[str]] = None

# Request models for sandbox operations
class CreateInventoryItemRequest(BaseModel):
    """Request to create an inventory item in sandbox."""
    seller_sku: str = Field(..., alias="sellerSku")
    marketplace_id: str = Field(..., alias="marketplaceId")
    product_name: str = Field(..., alias="productName")

class InventoryItem(BaseModel):
    """Item to be added to inventory in sandbox."""
    seller_sku: str = Field(..., alias="sellerSku")
    marketplace_id: str = Field(..., alias="marketplaceId")
    quantity: int

class AddInventoryRequest(BaseModel):
    """Request to add inventory in sandbox."""
    inventory_items: List[InventoryItem] = Field(..., alias="inventoryItems")

# Response models
class GetInventorySummariesResult(BaseModel):
    """Result containing inventory summaries."""
    granularity: Granularity
    inventory_summaries: List[InventorySummary] = Field(..., alias="inventorySummaries")

class Pagination(BaseModel):
    """Pagination information."""
    next_token: Optional[str] = Field(None, alias="nextToken")

class GetInventorySummariesResponse(BaseModel):
    """Response for get_inventory_summaries operation."""
    payload: Optional[GetInventorySummariesResult] = None
    pagination: Optional[Pagination] = None
    errors: Optional[List[ErrorDetail]] = None

class SandboxResponse(BaseModel):
    """Base response for sandbox operations."""
    errors: Optional[List[ErrorDetail]] = None

class CreateInventoryItemResponse(SandboxResponse):
    """Response for create_inventory_item operation."""
    pass

class DeleteInventoryItemResponse(SandboxResponse):
    """Response for delete_inventory_item operation."""
    pass

class AddInventoryResponse(SandboxResponse):
    """Response for add_inventory operation."""
    pass 