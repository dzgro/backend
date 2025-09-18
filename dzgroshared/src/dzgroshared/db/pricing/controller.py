from dzgroshared.db.model import PyObjectId
from dzgroshared.db.pricing.model import PlanWithPricingDetail, Pricing, PricingDetail, PricingDetailItem
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import CollectionType, CountryCode, PlanType 
from dzgroshared.db.DbUtils import DbManager

class PricingHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PRICING.value))
    
    async def getActivePlan(self, countrycode: CountryCode):
        result = await self.db.findOne({"countryCode": countrycode.value, "active": True})
        return Pricing.model_validate(result)
    
    async def getActivePlanId(self, countrycode: CountryCode):
        result = await self.db.findOne({"countryCode": countrycode.value, "active": True}, projectionInc=["_id"])
        return result['_id']
    
    async def getPlan(self, id: PyObjectId):
        result = await self.db.findOne({"_id": id})
        return Pricing.model_validate(result)

    async def getPlanDetailItemsById(self, pricingid: PyObjectId, revenue: float):
        pricing = await self.getPlan(pricingid)
        plans: list[PlanWithPricingDetail]=[]
        for plan in pricing.plans:
            items: list[PricingDetailItem] = [PricingDetailItem(label="A. Base Price", value=plan.baseprice)]
            total = 0
            gst = 0
            if plan.variable:
                items.append(PricingDetailItem(label="B. Revenue", sublabel="Last 30 Days", value=revenue))
                items.append(PricingDetailItem(label="C. Variable Price", sublabel=f'@{plan.variable}% of Revenue', value=round(revenue*plan.variable/100,1)))
                base = plan.baseprice + round(revenue * plan.variable / 100, 1)
                items.append(PricingDetailItem(label="D. Total Price", sublabel="Base + Variable Price", value=base))
                gst = round(base * 0.18,1)
                items.append(PricingDetailItem(label="E. GST @18%", value=gst))
                total = round(base +gst,1)
                items.append(PricingDetailItem(label="F. Net Payable", sublabel="Total Price + GST", value=total))
            else:
                gst = round(plan.baseprice * 0.18,1)
                items.append(PricingDetailItem(label="E. GST @18%", value=gst))
                total = round(plan.baseprice + gst,1)
                items.append(PricingDetailItem(label="F. Net Payable", sublabel="Total Price + GST", value=total))
            plans.append(PlanWithPricingDetail(plantype=plan.plantype, items=items, total=total))
        return PricingDetail(groupId=str(pricing.id), plans=plans, currency=pricing.currency, currencyCode=pricing.currencyCode)
                