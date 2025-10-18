import httpx, base64
from .order.controller import RazorpayOrderHelper
from .customer.controller import RazorpayCustomerHelper
from .plan.controller import RazorpayPlanHelper
from .subscription.controller import RazorpaySubscriptionHelper

class RazorpayClient:
    base_url = "https://api.razorpay.com/v1"
    
    def __init__(self, key:str, secret:str):
        credentials = f"{key}:{secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        self.headers = {"Authorization": f"Basic {encoded_credentials}"}
        self.client = httpx.AsyncClient(headers=self.headers)

    @property
    def subscription(self):
        return RazorpaySubscriptionHelper(self.base_url, self.client)

    @property
    def plan(self):
        return RazorpayPlanHelper(self.base_url, self.client)

    @property
    def customer(self):
        return RazorpayCustomerHelper(self.base_url, self.client)

    @property
    def order(self):
        return RazorpayOrderHelper(self.base_url, self.client)

    def verify_razorpay_signature(self, id: str, payment_id: str, signature: str, secret: str) -> bool:
        import hmac
        import hashlib
        try:
            message = f"{id}|{payment_id}"
            generated_signature = hmac.new( key=secret.encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256 ).hexdigest()
            return hmac.compare_digest(generated_signature, signature)
        except Exception as e:
            print(f"Frontend signature verification failed: {e}")
            return False
    
    
    # def createRazorpaySubscriptionObject(self, subscriptionId: str, name: str, email:str, phonenumber: str|None=None)->RazorpaySubscriptionObject:
    #     readonlyKeys:dict[CustomerKeys,bool] = {'name': True, 'email': True, 'contact': False}
    #     prefill:dict[CustomerKeys,str] = {'name': name, 'email': email}
    #     if phonenumber: 
    #         prefill['contact'] = phonenumber
    #         readonlyKeys['contact'] = True
    #     return RazorpaySubscriptionObject(subscription_id=subscriptionId, prefill=prefill, key=self.key, readonly=readonlyKeys)
    
    

    async def close(self):
        await self.client.aclose()