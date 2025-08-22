from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import SuccessResponse, AddMarketplace
from dzgroshared.models.enums import CountryCode, MarketplaceId, AmazonAccountType, RazorpaySubscriptionStatus
from dzgroshared.models.collections.spapi_accounts import SPAPIAccountRequest
from dzgroshared.models.collections.advertising_accounts import AdvertisingAccountRequest
from dzgroshared.models.collections.subscriptions import CreateSubscriptionRequest, UserSubscription
from dzgroshared.amazonapi.spapi import SpApiClient
from dzgroshared.amazonapi.adapi import AdApiClient
from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.models.razorpay.customer import CreateCustomer
from dzgroshared.models.razorpay.subscription import CreateSubscription
from dzgroshared.razorpay.client import RazorpayClient
from api.Util import RequestHelper

class OnboardingHelper:
    client: DzgroSharedClient
    redirect_uri: str = 'https://dzgro.com/onboarding'
    uid:str
    marketplace: ObjectId

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        if not self.client.uid or not self.client.marketplace:
            raise ValueError("Client must have uid and marketplace set")
        self.uid = self.client.uid
        self.marketplace = self.client.marketplace

    def __getattr__(self, item):
        return None
    
    async def spapi(self, id: str):
        return await self.client.db.spapi_accounts.getAccountApiClient(id, self.client.secrets.SPAPI_CLIENT_ID, self.client.secrets.SPAPI_CLIENT_SECRET)
    
    async def adapi(self, id: str):
        return await self.client.db.advertising_accounts.getAccountApiClient(id, self.client.secrets.ADS_CLIENT_ID, self.client.secrets.ADS_CLIENT_SECRET)

    def getRefreshToken(self, code: str, accountType: AmazonAccountType):
        client_id = self.client.secrets.SPAPI_CLIENT_ID if accountType==AmazonAccountType.SPAPI else self.client.secrets.ADS_CLIENT_ID
        client_secret = self.client.secrets.SPAPI_CLIENT_SECRET if accountType==AmazonAccountType.SPAPI else self.client.secrets.ADS_CLIENT_SECRET
        from dzgroshared.amazonapi.auth import Onboard
        manager = Onboard(client_id, client_secret, self.redirect_uri)
        return manager.generateRefreshToken(code)

    def getUrls(self, accountType: AmazonAccountType):
        params = f'?client_id={self.client.secrets.ADS_CLIENT_ID}&scope=advertising::campaign_management&redirect_uri={self.redirect_uri}&response_type=code'
        if accountType==AmazonAccountType.SPAPI:
            import string,random
            state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            params = f'/apps/authorize/consent?application_id={self.client.secrets.SPAPI_APPLICATION_ID}&state={state}&redirect_uri={self.redirect_uri}'
        return self.client.db.country_details.getCountriesByRegion(accountType, params)
    
    async def addSeller(self, data: SPAPIAccountRequest)->SuccessResponse:
        if not data.sellerid: raise ValueError('Seller ID is required')
        spapi = self.client.db.spapi_accounts
        try:
            await spapi.getSeller(sellerid=data.sellerid)
            return SuccessResponse(success=False, message=f"Seller already exists")
        except ValueError as e:
            data.refreshtoken = await self.getRefreshToken(data.refreshtoken, AmazonAccountType.SPAPI)
            await spapi.addSeller(data)
            return SuccessResponse(success=True)
    
    async def addAdvertisingAccount(self, data: AdvertisingAccountRequest)->SuccessResponse:
        adv = self.client.db.advertising_accounts
        data.refreshtoken = await self.getRefreshToken(data.refreshtoken, AmazonAccountType.ADVERTISING)
        await adv.addAccount(data)
        return SuccessResponse(success=True)
    
    async def getAdAccounts(self, id: str):
        from dzgroshared.models.model import AdAccount
        client = await self.adapi(id)
        response = await client.common.adsAccountsClient.listAccounts()
        accounts: list[AdAccount] = []
        for acc in list(filter(lambda x: x.status in ["CREATED", "ACTIVE"], response.adsAccounts)):
            for code in list(filter(lambda x: x in CountryCode.values(), acc.countryCodes)):
                profileId = next((x.profileId for x in acc.alternateIds if x.countryCode==code and x.entityId is None), None)
                entityId = next((x.entityId for x in acc.alternateIds if x.countryCode==code and x.profileId is None), None)
                if profileId and entityId:
                    adAccount = AdAccount(adsaccountid=acc.adsAccountId, accountname=acc.accountName, countryCode=CountryCode(code), profileid=profileId, entityid=entityId)
                    accounts.append(adAccount)
        return accounts
    
    async def getMarketplaceParticipations(self, id: str):
        client = await self.spapi(id)
        sellerMarketplaces = await client.sellers.get_marketplace_participations()
        if not sellerMarketplaces.payload: raise ValueError('No marketplaces found')
        return list(filter(lambda x: x.marketplace.id in MarketplaceId.values(), sellerMarketplaces.payload))
        
    
    async def testLinkage(self, req: AddMarketplace):
        spClient = await self.spapi(req.seller)
        adClient = await self.adapi(req.ad)
        listings = await spClient.listings.search_listings_items(
            seller_id=req.sellerid, 
            included_data=['summaries']
        )
        if not listings.items: raise ValueError("No listings found for the seller")
        listing = listings.items[0]
        asin = next((summary.asin for summary in listing.summaries if summary.marketplace_id==req.marketplaceid.value), None) if listing.summaries else None
        if not asin: return SuccessResponse(success=False, message="Selected Marketplace has no active products")
        from dzgroshared.amazonapi.adapi.common.products import ProductMetadataRequest
        metadata = await adClient.common.productsMetadataClient.listProducts(
            ProductMetadataRequest(skus=[listing.sku], pageIndex=0, pageSize=1)
        )
        if metadata.ProductMetadataList and metadata.ProductMetadataList[0].asin == asin: return SuccessResponse(success=True)
        return SuccessResponse(success=False, message="Selected Ad Account and Marketplace do not belong to same seller account")

    async def addMarketplace(self, req: AddMarketplace):
        marketplaces = await self.getMarketplaceParticipations(req.seller)
        if not any(marketplace.marketplace.id==req.marketplaceid.value for marketplace in marketplaces):
            raise ValueError("Marketplace not found for the given seller")
        await self.client.db.marketplaces.addMarketplace(req)
        return SuccessResponse(success=True)
    
    async def getPlanDetails(self, marketplaceid:str, planid:str):
        client = await self.spapi(marketplaceid)
        res = await client.sales.getLast30DaysSales()
        sales = float(res.payload[0].total_sales.amount) if res.payload else 0
        return await self.client.db.pricing.getPlanDetailItemsById(planid, sales)
    
    async def __createRazorpayCustomer(self, name: str, email:str, phone:str|None=None):
        customer = await self.client.razorpay.customer.create_customer( CreateCustomer( email=email, name=name, contact=phone, notes={"uid": self.uid} ) )
        return customer
    
    async def __createSubscription(self, customerid:str, body: CreateSubscriptionRequest, name: str, email:str, phone:str|None=None):
        plan = await self.client.razorpay.plan.fetch_plan(body.planId)
        subscription = await self.client.razorpay.subscription.create_subscription(
            CreateSubscription(plan_id=body.planId, total_count=120 if plan.period=='monthly' else 10, quantity=1)
        )
        await self.client.db.subscriptions.addSubscription(
            subscription_id=subscription.id, 
            plan_id=body.planId, 
            group_id=body.groupId, 
            customer_id=customerid, 
            status=subscription.status
        )
        return self.client.razorpay.createRazorpaySubscriptionObject(subscription.id, name, email, phone)

    async def getSubscription(self, body: CreateSubscriptionRequest): 
        from dzgroshared.cognito.client import CognitoManager
        username, details = await CognitoManager(self.client.secrets.COGNITO_APP_CLIENT_ID, self.client.secrets.COGNITO_USER_POOL_ID).get_user(self.uid)
        name, email, phone = details.get('name', ''), details.get('email', ''), details.get('phone_number', None)
        if not name or not email: raise ValueError("Name and Email are required to create a subscription")
        try:
            subscription = UserSubscription(**await self.client.db.subscriptions.getUserSubscription())
            customerid = subscription.customerid
        except: customerid = (await self.__createRazorpayCustomer(name, email, phone)).id
        return await self.__createSubscription(customerid, body, name, email, phone)

    async def verifySubscription(self, query: dict):
        subscription = UserSubscription(**await self.client.db.subscriptions.getUserSubscription())
        success  = self.client.razorpay.verify_razorpay_subscription_signature(
            subscription.subscriptionid,
            query['razorpay_payment_id'],
            query['razorpay_signature']
        )
        if not success: raise ValueError("Invalid subscription verification")
        subscription = await self.client.razorpay.subscription.fetch_subscription(subscription.subscriptionid)
        if subscription.status != RazorpaySubscriptionStatus.ACTIVE.value: raise ValueError("Subscription is not active")
        await self.client.db.subscriptions.updateSubscriptionStatus(subscription.id, RazorpaySubscriptionStatus.ACTIVE.value)
        return SuccessResponse(success=True)

        





            
