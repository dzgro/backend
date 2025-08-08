from bson import ObjectId
from models.model import SuccessResponse, AddMarketplace
from models.enums import CountryCode, MarketplaceId, AmazonAccountType, RazorpaySubscriptionStatus
from models.collections.spapi_accounts import SPAPIAccountRequest
from models.collections.advertising_accounts import AdvertisingAccountRequest
from models.collections.subscriptions import CreateSubscriptionRequest, UserSubscription
from amazonapi import AmazonApiClient
from models.amazonapi.model import AmazonApiObject
from razorpay.client import RazorpayClient
from api.Util import RequestHelper

class OnboardingHelper:
    req: RequestHelper
    redirect_uri: str = 'https://dzgro.com/onboarding'
    razorpay: RazorpayClient

    def __init__(self, req: RequestHelper) -> None:
        self.req = req

    def __getattr__(self, item):
        return None

    async def getAmazonApiClient(self, id: str, accountType: AmazonAccountType):
        obj: dict = {}
        if accountType == AmazonAccountType.SPAPI:
            obj = await self.req.spapi_accounts.getAccountApiObject(id, self.req.secrets.SPAPI_CLIENT_ID, self.req.secrets.SPAPI_CLIENT_SECRET)
        elif accountType == AmazonAccountType.ADVERTISING:
            obj = await self.req.advertising_accounts.getAccountApiObject(id, self.req.secrets.ADS_CLIENT_ID, self.req.secrets.ADS_CLIENT_SECRET)
        return AmazonApiClient(AmazonApiObject(**obj))

    async def getRazorpayClient(self):
        if not self.razorpay:
            secrets = self.req.secrets
            self.razorpay = RazorpayClient(secrets.RAZORPAY_CLIENT_ID, secrets.RAZORPAY_CLIENT_SECRET)
        return self.razorpay

    def getRefreshToken(self, code: str, accountType: AmazonAccountType):
        client_id = self.req.secrets.SPAPI_CLIENT_ID if accountType==AmazonAccountType.SPAPI else self.req.secrets.ADS_CLIENT_ID
        client_secret = self.req.secrets.SPAPI_CLIENT_SECRET if accountType==AmazonAccountType.SPAPI else self.req.secrets.ADS_CLIENT_SECRET
        from amazonapi.auth import Onboard
        manager = Onboard(client_id, client_secret, self.redirect_uri)
        return manager.generateRefreshToken(code)

    def getUrls(self, accountType: AmazonAccountType):
        params = f'?client_id={self.req.secrets.ADS_CLIENT_ID}&scope=advertising::campaign_management&redirect_uri={self.redirect_uri}&response_type=code'
        if accountType==AmazonAccountType.SPAPI:
            import string,random
            state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            params = f'/apps/authorize/consent?application_id={self.req.secrets.SPAPI_APPLICATION_ID}&state={state}&redirect_uri={self.redirect_uri}'
        return self.req.country_details.getCountriesByRegion(accountType, params)
    
    async def addSeller(self, data: SPAPIAccountRequest)->SuccessResponse:
        if not data.sellerid: raise ValueError('Seller ID is required')
        spapi = self.req.spapi_accounts
        try:
            await spapi.getSeller(sellerid=data.sellerid)
            return SuccessResponse(success=False, message=f"Seller already exists")
        except ValueError as e:
            data.refreshtoken = await self.getRefreshToken(data.refreshtoken, AmazonAccountType.SPAPI)
            await spapi.addSeller(data)
            return SuccessResponse(success=True)
    
    async def addAdvertisingAccount(self, data: AdvertisingAccountRequest)->SuccessResponse:
        adv = self.req.advertising_accounts
        data.refreshtoken = await self.getRefreshToken(data.refreshtoken, AmazonAccountType.ADVERTISING)
        await adv.addAccount(data)
        return SuccessResponse(success=True)
    
    async def getAdAccounts(self, id: str):
        amazonapi = await self.getAmazonApiClient(id, AmazonAccountType.ADVERTISING)
        from models.model import AdAccount
        response = await amazonapi.ad.common.adsAccountsClient.listAccounts()
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
        amazonapi = await self.getAmazonApiClient(id, AmazonAccountType.SPAPI)
        sellerMarketplaces = await amazonapi.spapi.sellers.get_marketplace_participations()
        if not sellerMarketplaces.payload: raise ValueError('No marketplaces found')
        return list(filter(lambda x: x.marketplace.id in MarketplaceId.values(), sellerMarketplaces.payload))
        
    
    async def testLinkage(self, req: AddMarketplace):
        spClient = await self.getAmazonApiClient(req.seller, AmazonAccountType.SPAPI)
        spClient.object.marketplaceid = req.marketplaceid.value
        adClient = await self.getAmazonApiClient(req.ad, AmazonAccountType.ADVERTISING)
        adClient.object.profile = req.profileid
        listings = await spClient.spapi.listings.search_listings_items(
            seller_id=req.sellerid, 
            included_data=['summaries']
        )
        if not listings.items: raise ValueError("No listings found for the seller")
        listing = listings.items[0]
        asin = next((summary.asin for summary in listing.summaries if summary.marketplace_id==req.marketplaceid.value), None) if listing.summaries else None
        if not asin: return SuccessResponse(success=False, message="Selected Marketplace has no active products")
        from amazonapi.adapi.common.products import ProductMetadataRequest
        metadata = await adClient.ad.common.productsMetadataClient.listProducts(
            ProductMetadataRequest(skus=[listing.sku], pageIndex=0, pageSize=1)
        )
        if metadata.ProductMetadataList and metadata.ProductMetadataList[0].asin == asin: return SuccessResponse(success=True)
        return SuccessResponse(success=False, message="Selected Ad Account and Marketplace do not belong to same seller account")

    async def addMarketplace(self, req: AddMarketplace):
        marketplaces = await self.getMarketplaceParticipations(req.seller)
        if not any(marketplace.marketplace.id==req.marketplaceid.value for marketplace in marketplaces):
            raise ValueError("Marketplace not found for the given seller")
        await self.req.marketplaces.addMarketplace(req)
        return SuccessResponse(success=True)
    
    async def getPlanDetails(self, marketplaceid:str, planid:str):
        apiObject = await self.req.marketplaces.getMarketplaceApiObject(
            marketplaceid, self.req.secrets.SPAPI_CLIENT_ID, self.req.secrets.SPAPI_CLIENT_SECRET, AmazonAccountType.SPAPI
        )
        client = AmazonApiClient(AmazonApiObject(**apiObject))
        res = await client.spapi.sales.getLast30DaysSales()
        sales = float(res.payload[0].total_sales.amount) if res.payload else 0
        return await self.req.pricing.getPlanDetailItemsById(planid, sales)
    
    async def __createRazorpayCustomer(self, name: str, email:str, phone:str|None=None):
        from razorpay.customer import CreateCustomer
        rzrpay = await self.getRazorpayClient()
        customer = await rzrpay.customer.create_customer( CreateCustomer( email=email, name=name, contact=phone, notes={"uid": self.req.uid} ) )
        return customer
    
    async def __createSubscription(self, customerid:str, body: CreateSubscriptionRequest, name: str, email:str, phone:str|None=None):
        razorpay = await self.getRazorpayClient()
        from razorpay.subscription import CreateSubscription
        plan = await razorpay.plan.fetch_plan(body.planId)
        subscription = await razorpay.subscription.create_subscription(
            CreateSubscription(plan_id=body.planId, total_count=120 if plan.period=='monthly' else 10, quantity=1)
        )
        await self.req.subscriptions.addSubscription(
            subscription_id=subscription.id, 
            plan_id=body.planId, 
            group_id=body.groupId, 
            customer_id=customerid, 
            status=subscription.status
        )
        return razorpay.createRazorpaySubscriptionObject(subscription.id, name, email, phone)

    async def getSubscription(self, body: CreateSubscriptionRequest): 
        from cognito.client import CognitoManager
        username, details = await CognitoManager(self.req.secrets.COGNITO_APP_CLIENT_ID, self.req.secrets.COGNITO_USER_POOL_ID).get_user(self.req.uid)           
        name, email, phone = details.get('name', ''), details.get('email', ''), details.get('phone_number', None)
        if not name or not email: raise ValueError("Name and Email are required to create a subscription")
        try:
            subscription = UserSubscription(**await self.req.subscriptions.getUserSubscription())
            customerid = subscription.customerid
        except: customerid = (await self.__createRazorpayCustomer(name, email, phone)).id
        return await self.__createSubscription(customerid, body, name, email, phone)

    async def verifySubscription(self, query: dict):
        razorpay = await self.getRazorpayClient()
        subscription = UserSubscription(**await self.req.subscriptions.getUserSubscription())
        success  = razorpay.verify_razorpay_subscription_signature(
            subscription.subscriptionid,
            query['razorpay_payment_id'],
            query['razorpay_signature']
        )
        if not success: raise ValueError("Invalid subscription verification")
        subscription = await razorpay.subscription.fetch_subscription(subscription.subscriptionid)
        if subscription.status != RazorpaySubscriptionStatus.ACTIVE.value: raise ValueError("Subscription is not active")
        await self.req.subscriptions.updateSubscriptionStatus(subscription.id, RazorpaySubscriptionStatus.ACTIVE.value)
        return SuccessResponse(success=True)

        





            
