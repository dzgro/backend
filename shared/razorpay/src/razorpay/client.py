import httpx, base64
from typing import Dict, Optional

from razorpay.customer import RazorpayCustomerHelper
from razorpay.plan import RazorpayPlanHelper
from .subscription import RazorpaySubscriptionHelper
from razorpay.models.common import RazorpaySubscriptionObject, RazorpayOrderObject, CustomerKeys

class RazorpayClient:

    subscription: RazorpaySubscriptionHelper
    plan: RazorpayPlanHelper
    customer: RazorpayCustomerHelper
    key: str
    secret: str
    
    def __init__(self, api_key: str, api_secret: str):
        self.key = api_key
        self.secret = api_secret
        credentials = f"{api_key}:{api_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}" }
        self.client = httpx.AsyncClient(headers=self.headers)
        self.subscription = RazorpaySubscriptionHelper(self.client)
        self.plan = RazorpayPlanHelper(self.client)
        self.customer = RazorpayCustomerHelper(self.client)

    def verify_razorpay_subscription_signature(self, subscription_id: str, payment_id: str, signature: str) -> bool:
        import hmac
        import hashlib
        
        try:
            # For subscription callbacks, the message format is: payment_id|subscription_id
            message = f"{payment_id}|{subscription_id}"
            
            # Generate HMAC signature using SHA256 and your secret key
            generated_signature = hmac.new(
                key=self.secret.encode('utf-8'),
                msg=message.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(generated_signature, signature)
            
        except Exception as e:
            # Log the error in production
            print(f"Frontend signature verification failed: {e}")
            return False
    
    def createRazorpaySubscriptionObject(self, subscriptionId: str, name: str, email:str, phonenumber: str|None=None)->RazorpaySubscriptionObject:
        readonlyKeys:dict[CustomerKeys,bool] = {'name': True, 'email': True, 'contact': False}
        prefill:dict[CustomerKeys,str] = {'name': name, 'email': email}
        if phonenumber: 
            prefill['contact'] = phonenumber
            readonlyKeys['contact'] = True
        return RazorpaySubscriptionObject(subscription_id=subscriptionId, prefill=prefill, key=self.key, readonly=readonlyKeys)
    
    def createRazorpayOrderObject(self, orderId: str, name: str, email:str, phonenumber: str|None=None)->RazorpayOrderObject:
        readonlyKeys:dict[CustomerKeys,bool] = {'name': True, 'email': True, 'contact': False}
        prefill:dict[CustomerKeys,str] = {'name': name, 'email': email}
        if phonenumber: 
            prefill['contact'] = phonenumber
            readonlyKeys['contact'] = True
        return RazorpayOrderObject(order_id=orderId, prefill=prefill, key=self.key, readonly=readonlyKeys)
    

    async def close(self):
        await self.client.aclose()