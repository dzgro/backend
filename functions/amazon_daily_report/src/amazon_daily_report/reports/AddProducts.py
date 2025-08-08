import asyncio
from datetime import datetime
from amazon_daily_report.reports.ReportUtils import ReportUtil
from amazonapi.spapi import SpApiClient
from bson import ObjectId
from db import DbClient
from db.collections.products import ProductHelper
from models.amazonapi.spapi.listings import Item
from models.collections.products import Product
from db.DbUtils import DbManager, PyObjectId
from models.enums import CollectionType
from models.extras.amazon_daily_report import MarketplaceObjectForReport
from models.model import LambdaContext, MockLambdaContext
from models.amazonapi.errors import APIError

class ListingsBuilder:
    marketplace: MarketplaceObjectForReport
    spapi: SpApiClient
    reportUtil: ReportUtil
    dbClient: DbClient
    reportId: PyObjectId
    productHelper: ProductHelper
    context: LambdaContext|MockLambdaContext
    dateFormat = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, marketplace: MarketplaceObjectForReport, context: LambdaContext|MockLambdaContext, spapi: SpApiClient, dbClient: DbClient, reportUtil: ReportUtil, reportId: PyObjectId ) -> None:
        self.marketplace = marketplace
        self.context = context
        self.spapi = spapi
        self.dbClient = dbClient
        self.productHelper = self.dbClient.products(self.marketplace.uid, ObjectId(self.marketplace.id))
        self.reportUtil = reportUtil
        self.reportId = reportId

    async def execute(self, date: datetime|None):
        exitBefore = 1000*120
        token:str|None = None
        items: list[dict] = []
        while self.context.get_remaining_time_in_millis()>exitBefore and (token is not None or len(items)==0):
            try:
                res = await self.getProducts(date, token)
                for item in res.items:
                    product = self.convertItemToDict(item)
                    if product: items.append(product)
                    print(f'Items : {len(items)}, Remaining: {res.number_of_results-20}')
                token = res.pagination.next_token if res.pagination and res.pagination.next_token else None
                date = datetime.strptime(items[-1]['lastUpdatedDate'], self.dateFormat)
            except APIError as e:
                if e.status_code==429:
                    await asyncio.sleep(1)
                    continue
                else: raise e
        return await self.complete(items, date, token is not None)

    async def complete(self, items: list[dict], date: datetime|None, hasMore: bool):
        if len(items)>0:
            await self.reportUtil.update(self.dbClient, CollectionType.PRODUCTS, items, self.reportId, False)
        if hasMore: return date
        await self.addParents()
        await self.addParentsWhereAbsent()


    async def getProducts(self, date: datetime|None, token: str|None=None):
        try:
            return (await self.spapi.listings.search_listings_items(
                seller_id=self.marketplace.sellerid,
                included_data=[
                    'summaries', 'attributes', 'relationships', 'images', 'productTypes', 'fulfillmentAvailability', 'offers'
                ],
                lastUpdatedAfter=date, pageToken=token
            ))
        except APIError as e:
            if e.status_code==429:
                await asyncio.sleep(1)
                return await self.getProducts(date, token)
            raise e
    
    async def addParents(self):
        pp = self.productHelper.db.pp
        matchStage = pp.matchMarketplace({ 'childskus': { '$exists': True } })
        unset = pp.unset([ 'parentsku', 'parentasin' ])
        unwind = pp.unwind("childskus")
        replaceRoot = pp.replaceRoot({ '_id': { '$concat': [ { '$toString': '$marketplace' }, '_', '$childskus' ] }, 'parentsku': '$sku', 'parentasin': '$asin' })
        merge = pp.merge(CollectionType.PRODUCTS)
        pipeline = [matchStage, unset, unwind, replaceRoot, merge]
        await self.productHelper.db.aggregate(pipeline)

    async def addParentsWhereAbsent(self):
        pp = self.productHelper.db.pp
        matchStage = pp.matchMarketplace({ 'parentsku': None })
        replaceRoot = pp.replaceRoot({ '_id': "$_id", 'parentsku': '$sku', 'parentasin': '$asin' })
        merge = pp.merge(CollectionType.PRODUCTS)
        pipeline = [matchStage, replaceRoot, merge]
        await self.productHelper.db.aggregate(pipeline)
    
    def convertItemToDict(self, item: Item)->dict|None:
        marketplaceId = self.marketplace.marketplaceid.value
        product: dict|None=None
        if not item.summaries or not item.attributes: raise ValueError("Product Summary not available")
        summary = next((summary for summary in item.summaries if summary.marketplace_id==marketplaceId), None)
        if not summary: raise ValueError("Product Summary not available for marketplace")
        product = {"_id": f'{str(self.marketplace.id)}_{item.sku}', "sku": item.sku, "asin": summary.asin, 'producttype': summary.product_type, 'title': summary.item_name, 'lastUpdatedDate': summary.last_updated_date}
        images = [item.attributes.get('main_product_image_locator', [{'media_location': None}])]
        i = 0
        while i<15:
            images.append(item.attributes.get(f'other_product_image_locator_{i}', [{'media_location': None}]))
            i=i+1
        product['images'] = [image[0]['media_location'] for image in images]
        product['images'] = list(filter(lambda x: x is not None, product['images']))
        if item.relationships:
            relationship = next((relationship.relationships[0] for relationship in item.relationships if relationship.marketplace_id==marketplaceId), None)
            if relationship:
                itemDict = {}
                if 'childSkus' in relationship and relationship['childSkus']: itemDict['childskus'] = relationship['childSkus']
                elif 'parentSkus' in relationship and relationship['parentSkus'] and len(relationship['parentSkus'])>0: itemDict['parentsku'] = relationship['parentSkus'][0]
                if 'variationTheme' in relationship and relationship['variationTheme'] and 'attributes' in relationship['variationTheme'] and relationship['variationTheme']['attributes']: 
                    itemDict['variationtheme'] = relationship['variationTheme']['theme']
                    attributes = relationship['variationTheme']['attributes']
                    if isinstance(attributes, list) and len(attributes)>0:
                        for attr in attributes:
                            x = item.attributes.get(attr, [{"value": None}])
                            if len(x)>0 and 'value' in x[0]:
                                obj = x[0]['value'] if 'value' in x[0] else None
                                if obj is None and 'standardized_values' in x:
                                    if isinstance(x['standardized_values'], list) and len(x['standardized_values'])>0:
                                        obj = x['standardized_values'][0]
                                if not obj: obj = '-'
                                if 'variationdetails' not in itemDict: itemDict['variationdetails'] = [{attr:obj }]
                                else: itemDict['variationdetails'].append({attr:obj })
                product.update(itemDict)
        return product