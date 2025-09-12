
from motor.motor_asyncio import AsyncIOMotorDatabase
from dzgroshared.client import DzgroSharedClient


class DbClient:
    client: DzgroSharedClient
    database: AsyncIOMotorDatabase

    def __init__(self, client: DzgroSharedClient):
        self.client = client
        if not self.client.mongoClient: raise ValueError("MongoDB client is not initialized.")
        self.database = self.client.mongoClient[client.DB_NAME]

    def __getattr__(self, item):
        return None
    
    @property
    def country_details(self):
        from dzgroshared.db.collections.country_details import CountryDetailsHelper
        if self.countryDetailsHelper:
            return self.countryDetailsHelper
        self.countryDetailsHelper = CountryDetailsHelper(self.client)
        return self.countryDetailsHelper
    
    @property
    def pricing(self):
        from dzgroshared.db.collections.pricing import PricingHelper
        if self.pricingHelper:
            return self.pricingHelper
        self.pricingHelper = PricingHelper(self.client)
        return self.pricingHelper

    @property
    def defaults(self):
        from dzgroshared.db.collections.defaults import DefaultsHelper
        if self.defaultsHelper:
            return self.defaultsHelper
        self.defaultsHelper = DefaultsHelper(self.client)
        return self.defaultsHelper
    
    @property
    def daily_report_failures(self):
        from dzgroshared.db.collections.report_failures import DailyReportFailuresHelper
        if self.dailyReportFailuresHelper:
            return self.dailyReportFailuresHelper
        self.dailyReportFailuresHelper = DailyReportFailuresHelper(self.client)
        return self.dailyReportFailuresHelper

    @property
    def sqs_messages(self):
        from dzgroshared.db.collections.queue_messages import QueueMessagesHelper
        if self.queueMessagesHelper:
            return self.queueMessagesHelper
        self.queueMessagesHelper = QueueMessagesHelper(self.client)
        return self.queueMessagesHelper
    
    @property
    def user(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access user.")
        from dzgroshared.db.collections.user import UserHelper
        if self.userHelper:
            return self.userHelper
        self.userHelper = UserHelper(self.client)
        return self.userHelper

    @property
    def marketplaces(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access marketplaces.")
        from dzgroshared.db.collections.marketplaces import MarketplaceHelper
        if self.marketplaceHelper:
            return self.marketplaceHelper
        self.marketplaceHelper = MarketplaceHelper(self.client)
        return self.marketplaceHelper

    @property
    def payments(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access payments.")
        from dzgroshared.db.collections.payments import PaymentHelper
        if self.paymentHelper:
            return self.paymentHelper
        self.paymentHelper = PaymentHelper(self.client)
        return self.paymentHelper

    @property
    def gstin(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access gstin.")
        from dzgroshared.db.collections.gstin import GSTHelper
        if self.gstinHelper:
            return self.gstinHelper
        self.gstinHelper = GSTHelper(self.client)
        return self.gstinHelper

    @property
    def pg_orders(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access PG Orders.")
        from dzgroshared.db.collections.pg_orders import PGOrderHelper
        if self.pgOrderHelper:
            return self.pgOrderHelper
        self.pgOrderHelper = PGOrderHelper(self.client)
        return self.pgOrderHelper

    @property
    def health(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access health.")
        from dzgroshared.db.collections.health import HealthHelper
        if self.healthHelper:
            return self.healthHelper
        self.healthHelper = HealthHelper(self.client)
        return self.healthHelper

    @property
    def analytics(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access analytics.")
        from dzgroshared.db.collections.analytics import DashboardHelper
        if self.dashboardHelper:
            return self.dashboardHelper
        self.dashboardHelper = DashboardHelper(self.client)
        return self.dashboardHelper

    @property
    def subscriptions(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access subscriptions.")
        from dzgroshared.db.collections.subscriptions import SubscriptionsHelper
        if self.subscriptionsHelper:
            return self.subscriptionsHelper
        self.subscriptionsHelper = SubscriptionsHelper(self.client)
        return self.subscriptionsHelper

    @property
    def advertising_accounts(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access advertising_accounts.")
        from dzgroshared.db.collections.advertising_accounts import AdvertisingAccountsHelper
        if self.advertisingAccountsHelper:
            return self.advertisingAccountsHelper
        self.advertisingAccountsHelper = AdvertisingAccountsHelper(self.client)
        return self.advertisingAccountsHelper

    @property
    def spapi_accounts(self):
        if not self.client.uid:
            raise ValueError("UID must be set to access spapi_accounts.")
        from dzgroshared.db.collections.spapi_accounts import SPAPIAccountsHelper
        if self.spapiAccountsHelper:
            return self.spapiAccountsHelper
        self.spapiAccountsHelper = SPAPIAccountsHelper(self.client)
        return self.spapiAccountsHelper

    @property
    def amazon_daily_reports(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access amazon_daily_reports.")
        from dzgroshared.db.collections.amazon_daily_reports import AmazonDailyReportHelper
        if self.amazonDailyReportHelper:
            return self.amazonDailyReportHelper
        self.amazonDailyReportHelper = AmazonDailyReportHelper(self.client)
        return self.amazonDailyReportHelper

    @property
    def queries(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access queries.")
        from dzgroshared.db.collections.queries import QueryHelper
        if self.queryHelper:
            return self.queryHelper
        self.queryHelper = QueryHelper(self.client)
        return self.queryHelper

    @property
    def dzgro_report_types(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access dzgro_reports.")
        from dzgroshared.db.collections.dzgro_report_types import DzgroReportTypesHelper
        if self.dzgroReportTypesHelper:
            return self.dzgroReportTypesHelper
        self.dzgroReportTypesHelper = DzgroReportTypesHelper(self.client)
        return self.dzgroReportTypesHelper

    @property
    def dzgro_reports(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access dzgro_reports.")
        from dzgroshared.db.collections.dzgro_reports import DzgroReportHelper
        if self.dzgroReportHelper:
            return self.dzgroReportHelper
        self.dzgroReportHelper = DzgroReportHelper(self.client)
        return self.dzgroReportHelper

    @property
    def dzgro_reports_data(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access dzgro_reports.")
        from dzgroshared.db.collections.dzgro_reports_data import DzgroReportDataHelper
        if self.dzgroReportDataHelper:
            return self.dzgroReportDataHelper
        self.dzgroReportDataHelper = DzgroReportDataHelper(self.client)
        return self.dzgroReportDataHelper

    @property
    def query_results(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access query_results.")
        from dzgroshared.db.collections.query_results import QueryResultsHelper
        if self.queryResultsHelper:
            return self.queryResultsHelper
        self.queryResultsHelper = QueryResultsHelper(self.client)
        return self.queryResultsHelper

    @property
    def products(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access products.")
        from dzgroshared.db.collections.products import ProductHelper
        if self.productHelper:
            return self.productHelper
        self.productHelper = ProductHelper(self.client)
        return self.productHelper

    @property
    def order_items(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access order_items.")
        from dzgroshared.db.collections.order_items import OrderItemsHelper
        if self.orderItemsHelper:
            return self.orderItemsHelper
        self.orderItemsHelper = OrderItemsHelper(self.client)
        return self.orderItemsHelper

    @property
    def orders(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access orders.")
        from dzgroshared.db.collections.orders import OrdersHelper
        if self.ordersHelper:
            return self.ordersHelper
        self.ordersHelper = OrdersHelper(self.client)
        return self.ordersHelper

    @property
    def settlements(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access settlements.")
        from dzgroshared.db.collections.settlements import SettlementsHelper
        if self.settlementsHelper:
            return self.settlementsHelper
        self.settlementsHelper = SettlementsHelper(self.client)
        return self.settlementsHelper

    @property
    def adv_assets(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access adv_assets.")
        from dzgroshared.db.collections.adv_assets import AdvAssetsHelper
        if self.advAssetsHelper:
            return self.advAssetsHelper
        self.advAssetsHelper = AdvAssetsHelper(self.client)
        return self.advAssetsHelper

    @property
    def adv_ads(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access adv_assets.")
        from dzgroshared.db.collections.adv_ads import AdvAAdsHelper
        if self.advAdsHelper:
            return self.advAdsHelper
        self.advAdsHelper = AdvAAdsHelper(self.client)
        return self.advAdsHelper

    @property
    def state_analytics(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access state_analytics.")
        from dzgroshared.db.collections.state_analytics import StateAnalyticsHelper
        if self.stateAnalyticsHelper:
            return self.stateAnalyticsHelper
        self.stateAnalyticsHelper = StateAnalyticsHelper(self.client)
        return self.stateAnalyticsHelper

    @property
    def date_analytics(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access date_analytics.")
        from dzgroshared.db.collections.date_analytics import DateAnalyticsHelper
        if self.dateAnalyticsHelper:
            return self.dateAnalyticsHelper
        self.dateAnalyticsHelper = DateAnalyticsHelper(self.client)
        return self.dateAnalyticsHelper
    
    @property
    def ad_structure(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_structure.")
        from dzgroshared.db.extras.ad_structure import AdStructureHelper
        if self.adStructureHelper:
            return self.adStructureHelper
        self.adStructureHelper = AdStructureHelper(self.client)
        return self.adStructureHelper

    @property
    def ad_rule_utility(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_utility.")
        from dzgroshared.db.collections.adv_rules import AdRuleUtility
        if self.adRuleUtility:
            return self.adRuleUtility
        self.adRuleUtility = AdRuleUtility(self.client)
        return self.adRuleUtility

    @property
    def ad_rule_run_utility(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_run_utility.")
        from dzgroshared.db.collections.adv_rule_runs import AdRuleRunUtility
        if self.adRuleRunUtility:
            return self.adRuleRunUtility
        self.adRuleRunUtility = AdRuleRunUtility(self.client)
        return self.adRuleRunUtility

    @property
    def ad_rule_criteria_groups(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_criteria_groups.")
        from dzgroshared.db.collections.adv_rule_criterias import AdRuleCriteriaGroupsUtility
        if self.adRuleCriteriaGroupsUtility:
            return self.adRuleCriteriaGroupsUtility
        self.adRuleCriteriaGroupsUtility = AdRuleCriteriaGroupsUtility(self.client)
        return self.adRuleCriteriaGroupsUtility
    
    @property
    def ad_rule_run_results(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_rule_run_results.")
        from dzgroshared.db.collections.adv_rule_run_results import AdRuleRunResultsHelper
        if self.adRuleRunResultsHelper:
            return self.adRuleRunResultsHelper
        self.adRuleRunResultsHelper = AdRuleRunResultsHelper(self.client)
        return self.adRuleRunResultsHelper
    
    @property
    def ad_ad_group_mapping(self):
        if not self.client.uid or not self.client.marketplaceId:
            raise ValueError("Marketplace and UID must be set to access ad_ad_group_mapping.")
        from dzgroshared.db.collections.adv_ad_group_mapping import AdvAdGroupMappingHelper
        if self.advAdGroupMappingHelper:
            return self.advAdGroupMappingHelper
        self.advAdGroupMappingHelper = AdvAdGroupMappingHelper(self.client)
        return self.advAdGroupMappingHelper
    
