from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.model import ErrorDetail

class SolicitationType(str, Enum):
    PRODUCT_REVIEW_AND_SELLER_FEEDBACK = "productReviewAndSellerFeedback"

class LinkObject(BaseModel):
    href: str
    name: Optional[str] = None

class SolicitationsAction(BaseModel):
    name: str

class GetSolicitationActionResponse(BaseModel):
    _links: Dict[str, LinkObject]
    _embedded: Optional[Dict[str, Any]] = None
    payload: Optional[SolicitationsAction] = None
    errors: Optional[List[ErrorDetail]] = None

class GetSolicitationActionsForOrderResponse(BaseModel):
    _links: Dict[str, Any]
    _embedded: Optional[Dict[str, Any]] = None
    errors: Optional[List[ErrorDetail]] = None

class CreateProductReviewAndSellerFeedbackSolicitationResponse(BaseModel):
    errors: Optional[List[ErrorDetail]] = None 