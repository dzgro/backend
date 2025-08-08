
from pydantic import BaseModel
from models.enums import RazorpaySubscriptionStatus
from models.model import ObjectIdStr


class UserSubscription(ObjectIdStr):
    subscriptionid: str
    planid: str
    customerid: str
    groupid: str
    status: RazorpaySubscriptionStatus

    def is_usable(self) -> bool:
        return self.status.is_active()

class CreateSubscriptionRequest(BaseModel):
    planId: str
    groupId: str