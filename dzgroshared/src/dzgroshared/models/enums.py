from enum import Enum


class ENVIRONMENT(str, Enum):
    PROD = "Prod"
    TEST = "Test"
    DEV = "Dev"
    LOCAL = "Local"

    
    @staticmethod
    def all():
        return list(ENVIRONMENT)

class CollateTypeTag(str, Enum):
    DAYS_7 = "Last 7 Days"
    DAYS_30 = "Last 30 Days"
    MONTH_ON_NONTH = "This Month vs Last Month (Till Date)"
    MONTH_OVER_MONTH = "This Month vs Last Month (Complete)"
    CUSTOM = "Custom"

class FilterOperator(str, Enum):
    eq = 'Equals'
    gt = 'Greater Than'
    gte = 'Greater Than or Equal To'
    lt = 'Less Than'
    lte = 'Less Than or Equal To'
    ne = 'Not Equal To'

class RazorpaySubscriptionStatus(str, Enum):
    CREATED = "created"
    AUTHENTICATED = "authenticated"
    PENDING = "pending"
    ACTIVE = "active"
    HALTED = "halted"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"

    def is_active(self) -> bool:
        return self in {
            RazorpaySubscriptionStatus.ACTIVE,
            RazorpaySubscriptionStatus.AUTHENTICATED,
            RazorpaySubscriptionStatus.PENDING,
        }

    def is_final_status(self) -> bool:
        return self in {
            RazorpaySubscriptionStatus.CANCELLED,
            RazorpaySubscriptionStatus.COMPLETED,
            RazorpaySubscriptionStatus.EXPIRED,
        }

    def is_failed_or_halted(self) -> bool:
        return self == RazorpaySubscriptionStatus.HALTED

    def is_created(self) -> bool:
        return self == RazorpaySubscriptionStatus.CREATED
    
class CollateType(str, Enum):
    SKU="sku"
    ASIN="asin"
    PARENT="parentsku"
    CATEGORY="producttype"
    MARKETPLACE="marketplace"

    @staticmethod
    def values():
        return list(CollateType)
    
class OperatorSign(str, Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "In"
    NOTIN = "Not In"

    @staticmethod
    def values():
        return list(OperatorSign)
class Operator(str, Enum):
    EQ = "Equals"
    NE = "Not Equals"
    GT = "Greater Than"
    GTE = "Greater Than or Equal to"
    LT = "Less Than"
    LTE = "Less Than or Equal to"
    IN = "In Values"
    NOTIN = "Not In Value"

    @staticmethod
    def values():
        return list(Operator)
    
    @staticmethod
    def withSigns():
        return list(map(lambda c: {"label": c.value, "value": getOperator(c)}, Operator))
    


class GSTStateCode(Enum):
    JAMMU_AND_KASHMIR = "01"
    HIMACHAL_PRADESH = "02"
    PUNJAB = "03"
    CHANDIGARH = "04"
    UTTARAKHAND = "05"
    HARYANA = "06"
    DELHI = "07"
    RAJASTHAN = "08"
    UTTAR_PRADESH = "09"
    BIHAR = "10"
    SIKKIM = "11"
    ARUNACHAL_PRADESH = "12"
    NAGALAND = "13"
    MANIPUR = "14"
    MIZORAM = "15"
    TRIPURA = "16"
    MEGHALAYA = "17"
    ASSAM = "18"
    WEST_BENGAL = "19"
    JHARKHAND = "20"
    ODISHA = "21"
    CHHATTISGARH = "22"
    MADHYA_PRADESH = "23"
    GUJARAT = "24"
    DAMAN_AND_DIU = "25"
    DADRA_AND_NAGAR_HAVELI = "26"
    MAHARASHTRA = "27"
    ANDHRA_PRADESH_OLD = "28"
    KARNATAKA = "29"
    GOA = "30"
    LAKSHADWEEP = "31"
    KERALA = "32"
    TAMIL_NADU = "33"
    PUDUCHERRY = "34"
    ANDAMAN_AND_NICOBAR_ISLANDS = "35"
    TELANGANA = "36"
    ANDHRA_PRADESH = "37"

class OnboardStep(str, Enum):
    ADD_SPAPI_ACCOUNT = 'Add Seller Central Account'
    ADD_AD_ACCOUNT = 'Add Advertising Account'
    ADD_MARKETPLACE = 'Select Marketplace'
    ADD_GST_DETAILS = 'Add Business Details'
    SUBSCRIBE = 'Start Subscription'

    @staticmethod
    def values():
        return list(OnboardStep)

def getOperator(op: Operator)->OperatorSign:
    return OperatorSign[op.name]

class AmazonDailyReportAggregationStep(str,Enum):
    ADD_PRODUCTS = "ADD_PRODUCTS"
    ADD_PORTFOLIOS="ADD_PORTFOLIOS"
    CREATE_REPORTS = "CREATE_REPORTS"
    PROCESS_REPORTS = "PROCESS_REPORTS"
    CREATE_STATE_DATE_ANALYTICS = "CREATE_STATE_DATE_ANALYTICS"
    ADD_QUERIES = "ADD_QUERIES"
    CREATE_AD_GROUP_AD_DATA = "CREATE_AD_GROUP_AD_DATA"
    CREATE_ADS = "CREATE_ADS"
    MARK_COMPLETION = "MARK_COMPLETION"

    @staticmethod
    def values():
        return list(map(lambda c: c, AmazonDailyReportAggregationStep))
    
class AmazonParentReportTaskStatus(str, Enum):
    PENDING="PENDING"
    PROCESSING="PROCESSING"
    COMPLETED="COMPLETED"

class MarketplaceStatus(str, Enum):
    NEW = "New"
    ACTIVE="Active"
    INACTIVE="Inactive"
    BUFFERING="Buffering"
    ARCHIVED="Archived"
    
class AmazonAccountType(str, Enum):
    ADVERTISING = "ADVERTISING"
    SPAPI= "SPAPI"

class SPAPIReportType(str, Enum):
    GET_MERCHANT_LISTINGS_ALL_DATA = "GET_MERCHANT_LISTINGS_ALL_DATA"
    GET_V2_SELLER_PERFORMANCE_REPORT = "GET_V2_SELLER_PERFORMANCE_REPORT"
    GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
    GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2 = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2"


class ProcessingStatus(str, Enum):
    """Report processing status values."""
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    FATAL = "FATAL"
    IN_PROGRESS = "IN_PROGRESS"
    IN_QUEUE = "IN_QUEUE"
    ADDED_TO_S3 = "ADDED_TO_S3"

class DataKioskType(str, Enum):
    SALES_TRAFFIC_ASIN = "SALES_TRAFFIC_ASIN"


class AdState(str, Enum):
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, AdState))
    
    @staticmethod
    def values():
        return list(AdState)

class AdProduct(str, Enum):
    SP = "SPONSORED_PRODUCTS"
    SB = "SPONSORED_BRANDS"
    SD = "SPONSORED_DISPLAY"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, AdProduct))

    @staticmethod
    def values():
        return list(AdProduct)

class AdAssetType(str, Enum):
    PORTFOLIO = 'Portfolio'
    CAMPAIGN = 'Campaign'
    AD_GROUP = 'Ad Group'
    TARGET = 'Target'
    NEGATIVE_ADGROUP = 'Ad Group Negative Target'
    NEGATIVE_CAMPAIGN = 'Campaign Negative Target'
    AD = 'Ad'
    SEARCH_TERM = 'Search Term'

class SearchTermType(str, Enum):
    BROAD="BROAD"
    PHRASE="PHRASE"
    EXACT="EXACT"
    TARGETING_EXPRESSION="TARGETING_EXPRESSION"
    TARGETING_EXPRESSION_PREDEFINED="TARGETING_EXPRESSION_PREDEFINED"

class AmazonReportAction(str, Enum):
    CREATE="CREATE"
    GET="GET"
    GET_DOCUMENT="GET_DOCUMENT"
    SAVE="SAVE"

    @staticmethod
    def list():
        return list(map(lambda c: c, AmazonReportAction))
    
class CountryCode(Enum):
    CANADA = 'CA'
    UNITED_STATES = 'US'
    MEXICO = 'MX'
    BRAZIL = 'BR'
    SPAIN = 'ES'
    UNITED_KINGDOM = 'UK'
    FRANCE = 'FR'
    BELGIUM = 'BE'
    NETHERLANDS = 'NL'
    GERMANY = 'DE'
    ITALY = 'IT'
    SWEDEN = 'SE'
    SOUTH_AFRICA = 'ZA'
    POLAND = 'PL'
    EGYPT = 'EG'
    TURKIYE = 'TR'
    SAUDI_ARABIA = 'SA'
    UNITED_ARAB_EMIRATES = 'AE'
    INDIA = 'IN'
    SINGAPORE = 'SG'
    AUSTRALIA = 'AU'
    JAPAN = 'JP'

    @staticmethod
    def values():
        return [x.value for x in CountryCode]

class MarketplaceId(Enum):
    CA = 'A2EUQ1WTGCTBG2'
    US = 'ATVPDKIKX0DER'
    MX = 'A1AM78C64UM0Y8'
    BR = 'A2Q3Y263D00KWC'
    ES = 'A1RKKUPIHCS9HS'
    UK = 'A1F83G8C2ARO7P'
    FR = 'A13V1IB3VIYZZH'
    BE = 'AMEN7PMS3EDWL'
    NL = 'A1805IZSGTT6HS'
    DE = 'A1PA6795UKMFR9'
    IT = 'APJ6JRA9NG5V4'
    SE = 'A2NODRKZP88ZB9'
    ZA = 'AE08WJ6YKNBMC'
    PL = 'A1C3SOZRARQ6R3'
    EG = 'ARBP9OOSHTCHU'
    TR = 'A33AVAJ2PDY3EV'
    SA = 'A17E79C6D8DWNP'
    AE = 'A2VIGQ35RCS4UG'
    IN = 'A21TJRUUN4KGV'
    SG = 'A19VAU5U5O7RUS'
    AU = 'A39IBJ37TRP1C6'
    JP = 'A1VC38T7YXB528'

    
    @staticmethod
    def values():
        return [x.value for x in MarketplaceId]


class CurrencyCode(Enum):
    CA = 'CAD'   # Canada Dollar
    US = 'USD'   # US Dollar
    MX = 'MXN'   # Mexican Peso
    BR = 'BRL'   # Brazilian Real
    ES = 'EUR'   # Euro (Spain)
    UK = 'GBP'   # British Pound
    FR = 'EUR'   # Euro (France)
    BE = 'EUR'   # Euro (Belgium)
    NL = 'EUR'   # Euro (Netherlands)
    DE = 'EUR'   # Euro (Germany)
    IT = 'EUR'   # Euro (Italy)
    SE = 'SEK'   # Swedish Krona
    ZA = 'ZAR'   # South African Rand
    PL = 'PLN'   # Polish Złoty
    EG = 'EGP'   # Egyptian Pound
    TR = 'TRY'   # Turkish Lira
    SA = 'SAR'   # Saudi Riyal
    AE = 'AED'   # UAE Dirham
    IN = 'INR'   # Indian Rupee
    SG = 'SGD'   # Singapore Dollar
    AU = 'AUD'   # Australian Dollar
    JP = 'JPY'   # Japanese Yen

    @staticmethod
    def values():
        return [x.value for x in CurrencyCode]
    

class CurrencySymbol(Enum):
    CA = 'CA$'   # Canadian Dollar
    US = '$'     # US Dollar
    MX = 'MX$'   # Mexican Peso
    BR = 'R$'    # Brazilian Real
    ES = '€'     # Euro (Spain)
    UK = '£'     # British Pound
    FR = '€'     # Euro (France)
    BE = '€'     # Euro (Belgium)
    NL = '€'     # Euro (Netherlands)
    DE = '€'     # Euro (Germany)
    IT = '€'     # Euro (Italy)
    SE = 'kr'    # Swedish Krona
    ZA = 'R'     # South African Rand
    PL = 'zł'    # Polish Złoty
    EG = 'E£'    # Egyptian Pound
    TR = '₺'     # Turkish Lira
    SA = '﷼'     # Saudi Riyal
    AE = 'د.إ'   # UAE Dirham
    IN = '₹'     # Indian Rupee
    SG = 'S$'    # Singapore Dollar
    AU = 'A$'    # Australian Dollar
    JP = '¥'     # Japanese Yen

    @staticmethod
    def values():
        return [x.value for x in CurrencySymbol]
    

class CollectionType(str,Enum):
    USERS = 'users'
    PRICING = 'pricing'
    SPAPI_ACCOUNTS = 'spapi_accounts'
    SPAPI_SUBSCRIPTIONS = 'spapi_subscriptions'
    ADVERTISING_ACCOUNTS = 'advertising_accounts'
    AD_ACCOUNTS = 'ad_accounts'
    MARKETPLACES = 'marketplaces'
    AMAZON_CHILD_REPORT_GROUP = 'amazon_child_reports_group'
    QUEUE_MESSAGES = "queue_messages"
    AMAZON_CHILD_REPORT = 'amazon_child_reports'
    COUNTRY_DETAILS = 'country_details'
    PAYMENTS = 'payments'
    SUBSCRIPTIONS = 'subscriptions'
    EVENTS = 'events'
    DEFAULTS = 'defaults'
    CREDITS = 'credits'
    PRODUCTS = 'products'
    ORDERS = 'orders'
    ORDER_ITEMS = 'order_items'
    RETURNS = 'returns'
    SETTLEMENTS = 'settlements'
    HEALTH = 'health'
    REPORT_DATA = 'report_data'
    TRAFFIC = 'traffic'
    DZGRO_REPORT_TYPES = 'dzgro_report_types'
    DZGRO_REPORTS = 'dzgro_reports'
    DZGRO_REPORT_DATA = 'dzgro_report_data'
    ADV = 'adv'
    ADV_ASSETS = 'adv_assets'
    ADV_RULE_RUN_RESULTS = 'adv_rule_run_results'
    ADV_RULE_RUNS = 'adv_rule_runs'
    ADV_RULES = 'adv_rules'
    ADV_AD_GROUP_MAPPING = 'adv_ad_group_mapping'
    ADV_ADS = 'adv_ads'
    ADV_RULE_CRITERIA_GROUPS = 'adv_rule_criteria_groups'
    STATE_ANALYTICS = 'state_analytics'
    STATE_NAMES = 'state_names'
    DATE_ANALYTICS = 'date_analytics'
    QUERIES = 'queries'
    QUERY_RESULTS = 'query_results'
    ANALYTICS_CALCULATION = 'analytics_calculation'
    SPAPI_REPORTS = 'spapi_reports'
    DATA_KIOSK_REPORTS = 'data_kiosk_reports'
    ADV_PERFORMANCE_REPORTS = 'adv_performance_reports'
    ADV_EXPORT_REPORTS = 'adv_export_reports'

    @staticmethod
    def values():
        return [x for x in CollectionType]


class FederationCollectionType(str,Enum):
    DZGRO_REPORT_DATA = 'dzgro_report_data'
    

class SQSMessageStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
class QueueName(str, Enum):
    AMAZON_REPORTS = "AmazonReports"
    RAZORPAY_WEBHOOK = "RazorpayWebhook"
    DZGRO_REPORTS = "DzgroReports"
    AMS_CHANGE = "AmsChange"
    AMS_PERFORMANCE = "AmsPerformance"
    PAYMENT_PROCESSOR = "PaymentProcessor"

class S3Bucket(str, Enum):
    DZGRO_REPORTS = "dzgro-report-data"
    AMAZON_REPORTS = "dzgro-amz-report-data"
    INVOICES = "dzgro-invoice"


class PlanDuration(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class BusinessType(str, Enum):
    PERSONAL = 'Personal'
    BUSINESS = 'Business'

class PlanType(str, Enum):
    REPORTS = 'Reports'
    ANALYTICS = 'Analytics'
    ADVERTISING = 'Advertising'
    ADVERTISING_SERVICE = 'Advertising Service'



class AmazonReportType(str, Enum):
    SPAPI = "SPAPI"
    AD = "AD"
    KIOSK = "KIOSK"
    AD_EXPORT = "AD_EXPORT"

class AdExportType(str, Enum):
    CAMPAIGN = "CAMPAIGN"
    AD_GROUP = "AD_GROUP"
    AD = "AD"
    TARGET = "TARGET"


class AdReportType(str, Enum):
    SPCAMPAIGNS = "spCampaigns"
    SBCAMPAIGNS = "sbCampaigns"
    SDCAMPAIGNS = "sdCampaigns"
    SBADGROUPS = "sbAdGroup"
    SDADGROUPS = "sdAdGroup"
    SBCAMPAIGNPLACEMENT = "sbCampaignPlacement"
    SPTARGETING = "spTargeting"
    SBTARGETING = "sbTargeting"
    SDTARGETING = "sdTargeting"
    SPSEARCHTERM = "spSearchTerm"
    SBSEARCHTERM = "sbSearchTerm"
    SPADVERTISEDPRODUCT = "spAdvertisedProduct"
    SDADVERTISEDPRODUCT = "sdAdvertisedProduct"
    SBADS = "sbAds"
    SPPURCHASEDPRODUCT = "spPurchasedProduct"
    SBPURCHASEDPRODUCT = "sbPurchasedProduct"
    SDPURCHASEDPRODUCT = "sdPurchasedProduct"
    SPGROSSANDINVALIDS = "spGrossAndInvalids"
    SBGROSSANDINVALIDS = "sbGrossAndInvalids"
    SDGROSSANDINVALIDS = "sdGrossAndInvalids"

class Region(str, Enum):
    NA = "NA"
    EU = "EU"
    FE = "FE"

class AMSDataSet(Enum):
    CAMPAIGNS = "campaigns"
    AD_GROUPS = "ad-groups"
    TARGETS = "targets"
    ADS = "ads"
    SP_TRAFFIC = "sp-traffic"
    SP_CONVERSIONS = "sp-conversion"
    SB_TRAFFIC = "sb-traffic"
    SB_CLICKSTREAM = "sb-clickstream"
    SD_TRAFFIC = "sd-traffic"
    SD_CONVERSIONS = "sd-conversion"
    SB_CONVERSIONS = "sb-conversion"
    SB_RICH_MEDIA = "sb-rich-media"
    BUDGET_USAGE = "budget-usage"
    CAMPAIGN_DIAGNOSTICS = "campaign-diagnostics"
    SP_BUDGET_RECOMMENDATIONS = "sp-budget-recommendations"


class DzgroReportType(str, Enum):
    ORDER_PAYMENT_RECON = "Order Payment Reconciliation"
    PRODUCT_PAYMENT_RECON = "Product Payment Reconciliation"
    PROFITABILITY = "Profitability"
    INVENTORY_PLANNING = "Inventory Planning"
    OUT_OF_STOCK = "Stock Out Skus"

class DzroReportPaymentReconSettlementRangeType(str, Enum):
    NO_END_DATE = 'NO_END_DATE'
    SAME_END_DATE = 'SAME_END_DATE'
    DIFFERENT_END_DATE = 'DIFFERENT_END_DATE'