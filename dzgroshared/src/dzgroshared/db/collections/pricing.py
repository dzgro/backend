from dzgroshared.models.collections.pricing import Pricing, PricingDetail, PricingDetailItem
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.enums import CollectionType 
from dzgroshared.db.DbUtils import DbManager

class PricingHelper:
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.PRICING.value))

    async def getPricing(self, sales: float):
        pipeline = [ { '$set': { 'plans': { '$map': { 'input': '$plans', 'as': 'p', 'in': { '$mergeObjects': [ '$$p', { 'eligible': { '$expr': { '$and': [ { '$ne': [ { '$ifNull': [ '$$p.gmv.max', None ] }, None ] }, { '$gte': [ '$$p.gmv.min', sales ] } ] } } } ] } } } } } ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Pricing found")
        return data[0]
    
    async def getPlans(self):
        return await self.db.findOne({})
    
    async def getPlanDetailItemsById(self, planid: str, revenue: float):
        items: list[PricingDetailItem] = []
        pricing = Pricing(**await self.getPlans())
        for plan in pricing.plans:
            if plan.planid == planid:
                items.append(PricingDetailItem(label="A. Base Price", value=plan.baseprice))
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
                return PricingDetail(planid=plan.planid, name=plan.name, groupId=str(pricing.id), items=items, total=total, currency=pricing.currency, currencyCode=pricing.currencyCode)
        raise ValueError("Plan not found")

                