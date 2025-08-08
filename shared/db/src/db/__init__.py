from db.collections.order_items import OrderItemsHelper
from db.collections.orders import OrdersHelper
from db.collections.products import ProductHelper
from db.collections.queries import QueryHelper
from db.collections.query_results import QueryResultsHelper
from db.collections.settlements import SettlementsHelper
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from db.collections.user import UserHelper
from db.collections.marketplaces import MarketplaceHelper
from db.collections.payments import PaymentHelper
from db.collections.health import HealthHelper
from db.collections.analytics import DashboardHelper
from db.collections.subscriptions  import SubscriptionsHelper
from db.collections.country_details  import CountryDetailsHelper
from db.collections.pricing  import PricingHelper
from db.collections.spapi_accounts  import SPAPIAccountsHelper
from db.collections.advertising_accounts  import AdvertisingAccountsHelper
from db.collections.queue_messages import QueueMessagesHelper
from db.collections.amazon_daily_reports import AmazonDailyReportHelper
from db.collections.analytics_calculation import CalculationKeysHelper
from db.collections.adv_assets import AdvAssetsHelper
from db.collections.state_analytics import StateAnalyticsHelper
from db.collections.date_analytics import DateAnalyticsHelper
from db.collections.dzgro_reports import DzgroReportHelper
from db.collections.adv_rules import AdRuleUtility
from db.collections.adv_rule_runs import AdRuleRunUtility
from db.collections.adv_rule_criterias import AdRuleCriteriaGroupsUtility
from db.collections.adv_rule_run_results import AdRuleRunResultsHelper
from db.collections.adv_ad_group_mapping import AdvAdGroupMappingHelper

from db.extras.ad_structure import AdStructureHelper
from bson import ObjectId

class DbClient:

    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase

    def __init__(self, MONGO_DB_CONNECT_URI: str):
        self.client = AsyncIOMotorClient(MONGO_DB_CONNECT_URI)
        self.db = self.client['dzgro-dev']

    def country_details(self):
        return CountryDetailsHelper(self.db)

    def pricing(self):
        return PricingHelper(self.db)
    
    def sqs_messages(self):
        return QueueMessagesHelper(self.db)

    def user(self, uid:str):
        return UserHelper(self.db, uid)

    def marketplaces(self, uid:str):
        return MarketplaceHelper(self.db, uid)

    def payments(self, uid:str):
        return PaymentHelper(self.db, uid)

    def health(self, uid:str, marketplace: ObjectId):
        return HealthHelper(self.db, uid, marketplace)

    def analytics(self, uid:str, marketplace: ObjectId):
        return DashboardHelper(self.db, uid, marketplace)

    def subscriptions(self, uid:str):
        return SubscriptionsHelper(self.db, uid)

    def advertising_accounts(self, uid:str):
        return AdvertisingAccountsHelper(self.db, uid)
    
    def spapi_accounts(self, uid:str):
        return SPAPIAccountsHelper(self.db, uid)

    def amazon_daily_reports(self, uid:str, marketplace: ObjectId):
        return AmazonDailyReportHelper(self.db, uid, marketplace)

    def calculation_keys(self):
        return CalculationKeysHelper(self.db)

    def queries(self, uid:str, marketplace: ObjectId):
        return QueryHelper(self.db, uid, marketplace)

    def reports(self, uid:str, marketplace: ObjectId):
        return DzgroReportHelper(self.db, uid, marketplace)

    def query_results(self, uid:str, marketplace: ObjectId):
        return QueryResultsHelper(self.db, uid, marketplace)
    
    def products(self, uid:str, marketplace: ObjectId):
        return ProductHelper(self.db, uid, marketplace)
    
    def order_items(self, uid:str, marketplace: ObjectId):
        return OrderItemsHelper(self.db, uid, marketplace)
    
    def orders(self, uid:str, marketplace: ObjectId):
        return OrdersHelper(self.db, uid, marketplace)
    
    def settlements(self, uid:str, marketplace: ObjectId):
        return SettlementsHelper(self.db, uid, marketplace)
    
    def adv_assets(self, uid:str, marketplace: ObjectId):
        return AdvAssetsHelper(self.db, uid, marketplace)
    
    def state_analytics(self, uid:str, marketplace: ObjectId):
        return StateAnalyticsHelper(self.db, uid, marketplace)
    
    def date_analytics(self, uid:str, marketplace: ObjectId):
        return DateAnalyticsHelper(self.db, uid, marketplace)
    
    def ad_structure(self, uid:str, marketplace: ObjectId):
        return AdStructureHelper(self.db, uid, marketplace)
    
    def ad_rule_utility(self, uid:str, marketplace: ObjectId):
        return AdRuleUtility(self.db, uid, marketplace)
    
    def ad_rule_run_utility(self, uid:str, marketplace: ObjectId):
        return AdRuleRunUtility(self.db, uid, marketplace)
    
    def ad_rule_criteria_groups(self, uid:str, marketplace: ObjectId):
        return AdRuleCriteriaGroupsUtility(self.db, uid, marketplace)
    
    def ad_rule_run_results(self, uid:str, marketplace: ObjectId):
        return AdRuleRunResultsHelper(self.db, uid, marketplace)
    
    def ad_ad_group_mapping(self, uid:str, marketplace: ObjectId):
        return AdvAdGroupMappingHelper(self.db, uid, marketplace)
    
