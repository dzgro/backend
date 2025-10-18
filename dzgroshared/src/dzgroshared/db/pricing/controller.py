from dzgroshared.db.model import MarketplacePlan, MarketplacePlanOrderObject, PyObjectId
from dzgroshared.db.pricing.model import MarketplacePricing, Pricing
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import AmazonAccountType, CollectionType, CountryCode
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.pricing.pipelines import GetPricing, GetMarketplacePricing
from dzgroshared.db.pricing.utils import getFeatures
from dzgroshared.db.razorpay_orders.model import RazorPayDbOrderCategory
from dzgroshared.razorpay.common import CustomerKeys, RazorpayOrderObject
from dzgroshared.razorpay.order.model import RazorPayOrderNotes, RazorpayCreateOrder

class PricingHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PRICING.value))
    
    async def getPricing(self):
        result: dict = {"data": await self.client.db.country_details.db.aggregate(GetPricing.pipeline())}
        result['features'] = getFeatures()
        return Pricing.model_validate(result)
    
    async def getMarketplacePricing(self, marketplace: PyObjectId):
        obj = await self.client.db.marketplaces.getMarketplaceApiObject(marketplace, AmazonAccountType.SPAPI)
        from dzgroshared.amazonapi.spapi import SpApiClient
        client = SpApiClient(obj)
        revenueMonth, orderMonth, revenueYear, orderYear = 0, 0, 0, 0
        monthMetrics = await client.sales.getLast30DaysSales()
        yearMetrics = await client.sales.getLastYearSales()
        revenueMonth = float(monthMetrics.payload[0].total_sales.amount) if monthMetrics.payload else 0
        orderMonth = monthMetrics.payload[0].order_count if monthMetrics.payload else 0
        revenueYear = float(yearMetrics.payload[0].total_sales.amount) if yearMetrics.payload else 0
        orderYear = yearMetrics.payload[0].order_count if yearMetrics.payload else 0
        result = await self.client.db.marketplaces.db.aggregate(GetMarketplacePricing.pipeline(marketplace, revenueMonth, orderMonth, revenueYear, orderYear))
        if len(result)==0: raise ValueError("Marketplace not found")
        result = result[0]
        result['features'] = getFeatures()
        return MarketplacePricing.model_validate(result)
    
    def _createRazorpayOrderObject(self, orderId: str, name: str, email:str, phonenumber: str|None=None)->RazorpayOrderObject:
        readonlyKeys:dict[CustomerKeys,bool] = {'name': True, 'email': True, 'contact': False}
        prefill:dict[CustomerKeys,str] = {'name': name, 'email': email}
        if phonenumber: 
            prefill['contact'] = phonenumber
            readonlyKeys['contact'] = True
        return RazorpayOrderObject(order_id=orderId, prefill=prefill, key=self.client.secrets.RAZORPAY_CLIENT_ID, readonly=readonlyKeys)
    
    async def generateOrderForMarketplace(self, req: MarketplacePlanOrderObject):
        plans = (await self.getMarketplacePricing(req.marketplace))
        plan = next((plan for plan in plans.details if plan.name==req.plan.plan and plan.duration==req.plan.duration), None)
        if not plan: raise ValueError("Plan not found")
        if req.gstin and not plans.gstin==req.gstin: await self.client.db.marketplace_gstin.linkGst(req.gstin, req.marketplace)
        notes = RazorPayOrderNotes(
            uid=self.client.uid,
            marketplace=req.marketplace,
            gstin=req.gstin,
            plan=req.plan
        )
        orderReq = RazorpayCreateOrder( 
            currency=plans.currencyCode,
            amount=int(plan.total*100),
            receipt=str(req.marketplace),
            notes=notes
        )
        order = await self.client.razorpay.order.create_order(orderReq)
        await self.client.db.razorpay_orders.addOrder(order, notes, category=RazorPayDbOrderCategory.MARKETPLACE_ONBOARDING)
        return self._createRazorpayOrderObject(order.id, self.client.user.name, self.client.user.email, self.client.user.phone_number)
        
    
    async def getActivePlan(self, countrycode: CountryCode):
        result = await self.db.findOne({"countryCode": countrycode.value, "active": True})
        return Pricing.model_validate(result)
    
    async def getActivePlanId(self, countrycode: CountryCode):
        result = await self.db.findOne({"countryCode": countrycode.value, "active": True}, projectionInc=["_id"])
        return result['_id']
    
    async def getPlan(self, id: PyObjectId):
        result = await self.db.findOne({"_id": id})
        return Pricing.model_validate(result)
                