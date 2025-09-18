
from motor.motor_asyncio import AsyncIOMotorDatabase
from dzgroshared.client import DzgroSharedClient


class DbClient:
    client: DzgroSharedClient
    database: AsyncIOMotorDatabase

    def __init__(self, client: DzgroSharedClient):
        self.client = client
        if not self.client.mongoClient: 
            raise ValueError("MongoDB client is not initialized.")
        
        # Debug: Check if mongoClient is a coroutine
        import inspect
        if inspect.iscoroutine(self.client.mongoClient):
            raise ValueError(f"MongoDB client is a coroutine, not a client instance: {type(self.client.mongoClient)}")
            
        self.database = self.client.mongoClient[client.DB_NAME]

    def __getattr__(self, item):
        return None
    
    @property
    def country_details(self):
        from dzgroshared.db.country_details.controller import CountryDetailsHelper
        if self.countryDetailsHelper:
            return self.countryDetailsHelper
        self.countryDetailsHelper = CountryDetailsHelper(self.client)
        return self.countryDetailsHelper
    

    @property
    def invoice_number(self):
        from dzgroshared.db.invoice_number.controller import InvoiceNumberHelper
        if self.invoiceNumberHelper:
            return self.invoiceNumberHelper
        self.invoiceNumberHelper = InvoiceNumberHelper(self.client)
        return self.invoiceNumberHelper


    @property
    def daily_report_failures(self):
        from dzgroshared.db.report_failures.controller import DailyReportFailuresHelper
        if self.dailyReportFailuresHelper:
            return self.dailyReportFailuresHelper
        self.dailyReportFailuresHelper = DailyReportFailuresHelper(self.client)
        return self.dailyReportFailuresHelper

    @property
    def sqs_messages(self):
        from dzgroshared.db.queue_messages.controller import QueueMessagesHelper
        if self.queueMessagesHelper:
            return self.queueMessagesHelper
        self.queueMessagesHelper = QueueMessagesHelper(self.client)
        return self.queueMessagesHelper
    
    
    @property
    def pricing(self):
        from dzgroshared.db.pricing.controller import PricingHelper
        if self.pricingHelper:
            return self.pricingHelper
        self.pricingHelper = PricingHelper(self.client)
        return self.pricingHelper
    
    @property
    def users(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access user.")
        from dzgroshared.db.users.controller import UserHelper
        if self.userHelper:
            return self.userHelper
        self.userHelper = UserHelper(self.client)
        return self.userHelper

    @property
    def marketplaces(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access marketplaces.")
        from dzgroshared.db.marketplaces.controller import MarketplaceHelper
        if self.marketplaceHelper:
            return self.marketplaceHelper
        self.marketplaceHelper = MarketplaceHelper(self.client)
        return self.marketplaceHelper

    @property
    def payments(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access payments.")
        from dzgroshared.db.payments.controller import PaymentHelper
        if self.paymentHelper:
            return self.paymentHelper
        self.paymentHelper = PaymentHelper(self.client)
        return self.paymentHelper

    @property
    def gstin(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access gstin.")
        from dzgroshared.db.gstin.controller import GSTHelper
        if self.gstinHelper:
            return self.gstinHelper
        self.gstinHelper = GSTHelper(self.client)
        return self.gstinHelper

    @property
    def razorpay_orders(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access Razorpay Orders.")
        from dzgroshared.db.razorpay_orders.controller import RazorPayDbOrderHelper
        if self.razorpayDbOrderHelper:
            return self.razorpayDbOrderHelper
        self.razorpayDbOrderHelper = RazorPayDbOrderHelper(self.client)
        return self.razorpayDbOrderHelper

    @property
    def health(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access health.")
        from dzgroshared.db.health.controller import HealthHelper
        if self.healthHelper:
            return self.healthHelper
        self.healthHelper = HealthHelper(self.client)
        return self.healthHelper

    @property
    def advertising_accounts(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access advertising_accounts.")
        from dzgroshared.db.advertising_accounts.controller import AdvertisingAccountsHelper
        if self.advertisingAccountsHelper:
            return self.advertisingAccountsHelper
        self.advertisingAccountsHelper = AdvertisingAccountsHelper(self.client)
        return self.advertisingAccountsHelper

    @property
    def spapi_accounts(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access spapi_accounts.")
        from dzgroshared.db.spapi_accounts.controller import SPAPIAccountsHelper
        if self.spapiAccountsHelper:
            return self.spapiAccountsHelper
        self.spapiAccountsHelper = SPAPIAccountsHelper(self.client)
        return self.spapiAccountsHelper

    @property
    def daily_report_group(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access amazon_daily_reports.")
        from dzgroshared.db.daily_report_group.controller import DailyReportGroupHelper
        if self.dailyReportGroupHelper:
            return self.dailyReportGroupHelper
        self.dailyReportGroupHelper = DailyReportGroupHelper(self.client)
        return self.dailyReportGroupHelper

    @property
    def daily_report_item(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access amazon_item_reports.")
        from dzgroshared.db.daily_report_item.controller import DailyReportItemHelper
        if self.dailyReportItemHelper:
            return self.dailyReportItemHelper
        self.dailyReportItemHelper = DailyReportItemHelper(self.client)
        return self.dailyReportItemHelper

    @property
    def performance_periods(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access performance periods.")
        from dzgroshared.db.performance_periods.controller import PerformancePeriodHelper
        if self.performancePeriodHelper:
            return self.performancePeriodHelper
        self.performancePeriodHelper = PerformancePeriodHelper(self.client)
        return self.performancePeriodHelper

    @property
    def performance_period_results(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access performance periods results.")
        from dzgroshared.db.performance_period_results.controller import PerformancePeriodResultsHelper
        if self.performancePeriodResultsHelper:
            return self.performancePeriodResultsHelper
        self.performancePeriodResultsHelper = PerformancePeriodResultsHelper(self.client)
        return self.performancePeriodResultsHelper

    @property
    def dzgro_report_types(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access dzgro_reports.")
        from dzgroshared.db.dzgro_report_types.controller import DzgroReportTypesHelper
        if self.dzgroReportTypesHelper:
            return self.dzgroReportTypesHelper
        self.dzgroReportTypesHelper = DzgroReportTypesHelper(self.client)
        return self.dzgroReportTypesHelper

    @property
    def dzgro_reports(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access dzgro_reports.")
        from dzgroshared.db.dzgro_reports.controller import DzgroReportHelper
        if self.dzgroReportHelper:
            return self.dzgroReportHelper
        self.dzgroReportHelper = DzgroReportHelper(self.client)
        return self.dzgroReportHelper

    @property
    def dzgro_reports_data(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access dzgro_reports.")
        from dzgroshared.db.dzgro_report_data.controller import DzgroReportDataHelper
        if self.dzgroReportDataHelper:
            return self.dzgroReportDataHelper
        self.dzgroReportDataHelper = DzgroReportDataHelper(self.client)
        return self.dzgroReportDataHelper

    @property
    def products(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access products.")
        from dzgroshared.db.products.controller import ProductHelper
        if self.productHelper:
            return self.productHelper
        self.productHelper = ProductHelper(self.client)
        return self.productHelper

    @property
    def order_items(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access order_items.")
        from dzgroshared.db.order_items.controller import OrderItemsHelper
        if self.orderItemsHelper:
            return self.orderItemsHelper
        self.orderItemsHelper = OrderItemsHelper(self.client)
        return self.orderItemsHelper

    @property
    def orders(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access orders.")
        from dzgroshared.db.orders.controller import OrdersHelper
        if self.ordersHelper:
            return self.ordersHelper
        self.ordersHelper = OrdersHelper(self.client)
        return self.ordersHelper

    @property
    def settlements(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access settlements.")
        from dzgroshared.db.settlements.controller import SettlementsHelper
        if self.settlementsHelper:
            return self.settlementsHelper
        self.settlementsHelper = SettlementsHelper(self.client)
        return self.settlementsHelper

    @property
    def adv_assets(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access adv_assets.")
        from dzgroshared.db.adv.adv_assets.controller import AdvAssetsHelper
        if self.advAssetsHelper:
            return self.advAssetsHelper
        self.advAssetsHelper = AdvAssetsHelper(self.client)
        return self.advAssetsHelper

    @property
    def adv_ads(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access adv_assets.")
        from dzgroshared.db.adv.adv_ads.controller import AdvAAdsHelper
        if self.advAdsHelper:
            return self.advAdsHelper
        self.advAdsHelper = AdvAAdsHelper(self.client)
        return self.advAdsHelper

    @property
    def state_analytics(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access state_analytics.")
        from dzgroshared.db.state_analytics.controller import StateAnalyticsHelper
        if self.stateAnalyticsHelper:
            return self.stateAnalyticsHelper
        self.stateAnalyticsHelper = StateAnalyticsHelper(self.client)
        return self.stateAnalyticsHelper

    @property
    def date_analytics(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access date_analytics.")
        from dzgroshared.db.date_analytics.controller import DateAnalyticsHelper
        if self.dateAnalyticsHelper:
            return self.dateAnalyticsHelper
        self.dateAnalyticsHelper = DateAnalyticsHelper(self.client)
        return self.dateAnalyticsHelper
    
    @property
    def ad_structure(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_structure.")
        from dzgroshared.db.adv.adv_structure_rules.controller import AdStructureHelper
        if self.adStructureHelper:
            return self.adStructureHelper
        self.adStructureHelper = AdStructureHelper(self.client)
        return self.adStructureHelper

    @property
    def ad_rule_utility(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_utility.")
        from dzgroshared.db.adv.adv_rules.controller import AdRuleUtility
        if self.adRuleUtility:
            return self.adRuleUtility
        self.adRuleUtility = AdRuleUtility(self.client)
        return self.adRuleUtility

    @property
    def ad_rule_run_utility(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_run_utility.")
        from dzgroshared.db.adv.adv_rule_runs.controller import AdRuleRunUtility
        if self.adRuleRunUtility:
            return self.adRuleRunUtility
        self.adRuleRunUtility = AdRuleRunUtility(self.client)
        return self.adRuleRunUtility

    @property
    def ad_rule_criteria_groups(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_criteria_groups.")
        from dzgroshared.db.adv.adv_rule_criterias.controller import AdRuleCriteriaGroupsUtility
        if self.adRuleCriteriaGroupsUtility:
            return self.adRuleCriteriaGroupsUtility
        self.adRuleCriteriaGroupsUtility = AdRuleCriteriaGroupsUtility(self.client)
        return self.adRuleCriteriaGroupsUtility
    
    @property
    def ad_rule_run_results(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_run_results.")
        from dzgroshared.db.adv.adv_rule_results.controller import AdRuleRunResultsHelper
        if self.adRuleRunResultsHelper:
            return self.adRuleRunResultsHelper
        self.adRuleRunResultsHelper = AdRuleRunResultsHelper(self.client)
        return self.adRuleRunResultsHelper
    
    @property
    def ad_ad_group_mapping(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_ad_group_mapping.")
        from dzgroshared.db.adv.adv_ad_group_mapping.controller import AdvAdGroupMappingHelper
        if self.advAdGroupMappingHelper:
            return self.advAdGroupMappingHelper
        self.advAdGroupMappingHelper = AdvAdGroupMappingHelper(self.client)
        return self.advAdGroupMappingHelper
    
