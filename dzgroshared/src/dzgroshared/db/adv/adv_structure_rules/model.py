from pydantic import BaseModel, Field, validator, model_validator
from enum import Enum
from typing import List, Optional

from dzgroshared.db.adv.adv_assets.model import SPTargetDetails
from dzgroshared.db.products.model import Product
from dzgroshared.db.enums import AdAssetType

class ScoreComment(str, Enum):
    VERY_POOR = "Very Poor"
    POOR = "Poor"
    AVERAGE = "Average"
    GOOD = "Good"
    EXCELLENT = "Excellent"
    PERFECT = "Perfect"


class ScoreItem(BaseModel):
    ruleid: str
    label: str
    value: str  # Example: "85%"
    weight: int
    remaining: int
    color: str  # Example: "#C8E6C9"
    comment: ScoreComment
    benefits: list[str]
    description: str
    assettype: AdAssetType


class StructureScoreResponse(BaseModel):
    score: str  # Final score as string with %, e.g. "92%"
    rawScore: int  # Final score as int, e.g. 92
    color: str  # Overall color based on score
    comment: ScoreComment
    items: list[ScoreItem]

class AutoSegmentData(BaseModel):
    impressions: int
    clicks: int
    spend: float
    sales: float
    acos: str
    zero_impressions: bool = Field(..., alias="zeroImpressions")
    zero_clicks: bool = Field(..., alias="zeroClicks")
    zero_sales: bool = Field(..., alias="zeroSales")
    should_pause: bool = Field(..., alias="shouldPause")
    should_renew: bool = Field(..., alias="shouldRenew")
    retain: bool

class ViolatingAdGroupAd(AutoSegmentData):
    ad: str
    product: Product

class ViolatingAdGroupTarget(AutoSegmentData):
    id: str
    targettype: str
    targetdetails: SPTargetDetails
class ViolatingAdGroupMatchType(AutoSegmentData):
    matchtype: str
    count: int

class ViolatingAdGroupMatchTypeWithTargets(ViolatingAdGroupMatchType):
    targetsToRetain: List[ViolatingAdGroupTarget] = Field(default_factory=list, description="Targets to retain for this match type")
    targetsToCreateNew: List[ViolatingAdGroupTarget] = Field(default_factory=list, description="Targets to create new for this match type")
    targetsToPause: List[ViolatingAdGroupTarget] = Field(default_factory=list, description="Targets to pause for this match type")

class AdGroupCompliance(BaseModel):
    adgroupid: str = Field(..., description="Unique identifier of the ad group")
    name: str = Field(..., description="Ad group name")
    campaignid: str = Field(..., description="Campaign ID this ad group belongs to")
    campaignName: str = Field(..., description="Name of the campaign")
    violatesMultipleProducts: bool
    violatesMultipleMatchTypes: bool
    violatesKeywordStuffing: bool

# Form data models for ad group optimization
class RemoveMultipleAdsForm(BaseModel):
    retain: List[ViolatingAdGroupAd] = Field(default_factory=list, description="Ads to retain")
    pause: List[ViolatingAdGroupAd] = Field(default_factory=list, description="Ads to pause")
    createNew: List[ViolatingAdGroupAd] = Field(default_factory=list, description="Ads to create new")

class RemoveMatchTypesForm(BaseModel):
    retain: List[ViolatingAdGroupMatchTypeWithTargets] = Field(default_factory=list, description="Match types to retain")
    pause: List[ViolatingAdGroupMatchTypeWithTargets] = Field(default_factory=list, description="Match types to pause")
    createNew: List[ViolatingAdGroupMatchTypeWithTargets] = Field(default_factory=list, description="Match types to create new")

class RemoveKeywordStuffingForm(BaseModel):
    retain: List[ViolatingAdGroupTarget] = Field(default_factory=list, description="Targets to retain")
    pause: List[ViolatingAdGroupTarget] = Field(default_factory=list, description="Targets to pause")
    createNew: List[ViolatingAdGroupTarget] = Field(default_factory=list, description="Targets to create new")

class AdGroupOptimizationRequest(BaseModel):
    adgroupid: str = Field(..., description="Ad group ID to optimize")
    ads: Optional[RemoveMultipleAdsForm] = Field(default=None, description="Multiple ads removal configuration")
    matchtypes: Optional[RemoveMatchTypesForm] = Field(default=None, description="Match types removal configuration")
    targets: Optional[RemoveKeywordStuffingForm] = Field(default=None, description="Keyword stuffing removal configuration")

    @model_validator(mode='after')
    def validate_optimization_request(self):
        # Check if at least one remove item is present
        if self.ads is None and self.matchtypes is None and self.targets is None:
            raise ValueError("At least one remove item (ads, matchtypes, or targets) must be present.")
        
        # Validate ads if present
        if self.ads is not None:
            if not self.ads.retain and not self.ads.pause and not self.ads.createNew:
                raise ValueError("At least one ad must be retained, paused, or created new.")
            if not self.ads.retain:
                raise ValueError("At least one ad must be retained.")
        
        # Validate matchtypes if present
        if self.matchtypes is not None:
            if not self.matchtypes.retain and not self.matchtypes.pause and not self.matchtypes.createNew:
                raise ValueError("At least one match type must be retained, paused, or created new.")
            if not self.matchtypes.retain:
                raise ValueError("At least one match type must be retained.")
        
        # Validate targets if present
        if self.targets is not None:
            if not self.targets.retain and not self.targets.pause and not self.targets.createNew:
                raise ValueError("At least one target must be retained, paused, or created new.")
            if not self.targets.retain:
                raise ValueError("At least one target must be retained.")
        
        return self

class AdGroupOptimizationResponse(BaseModel):
    success: bool = Field(..., description="Whether the optimization was successful")
    message: str = Field(..., description="Response message")
    adgroupid: str = Field(..., description="Ad group ID that was optimized")
    changes_applied: dict = Field(default_factory=dict, description="Summary of changes applied")
