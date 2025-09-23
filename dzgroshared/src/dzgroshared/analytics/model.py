from dzgroshared.db.enums import AnalyticsMetric, AnalyticsMetricOperation, AnalyticGroupMetricLabel
from dzgroshared.db.model import MetricCalculation, MetricDetail, MetricGroup, MetricItem

METRIC_CALCULATIONS: list[MetricCalculation] = [
    MetricCalculation( metric=AnalyticsMetric.REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.FBA_REVENUE]),
    MetricCalculation( metric=AnalyticsMetric.FBA_REVENUE_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_REVENUE, AnalyticsMetric.REVENUE], level=1),
    MetricCalculation( metric=AnalyticsMetric.FBM_REVENUE_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.REVENUE], level=1),
    MetricCalculation( metric=AnalyticsMetric.RETURN_VALUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_RETURN_VALUE, AnalyticsMetric.FBA_RETURN_VALUE] ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.FBM_RETURN_VALUE] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_REVENUE, AnalyticsMetric.FBA_RETURN_VALUE] ),
    MetricCalculation( metric=AnalyticsMetric.TAX, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_TAX, AnalyticsMetric.FBA_TAX] ),
    MetricCalculation( metric=AnalyticsMetric.NET_REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.REVENUE, AnalyticsMetric.RETURN_VALUE], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.ORDERS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_ORDERS, AnalyticsMetric.FBA_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.CANCELLED_ORDERS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_CANCELLED_ORDERS, AnalyticsMetric.FBA_CANCELLED_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.NET_ORDERS, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.ORDERS, AnalyticsMetric.CANCELLED_ORDERS], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_ORDERS, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.FBM_ORDERS, AnalyticsMetric.FBM_CANCELLED_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_ORDERS, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.FBA_ORDERS, AnalyticsMetric.FBA_CANCELLED_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_QUANTITY, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.FBA_QUANTITY, AnalyticsMetric.FBA_RETURN_QUANTITY] ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_QUANTITY, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.FBM_QUANTITY, AnalyticsMetric.FBM_RETURN_QUANTITY] ),
    MetricCalculation( metric=AnalyticsMetric.NET_QUANTITY, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.QUANTITY, AnalyticsMetric.RETURN_QUANTITY], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.QUANTITY, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_QUANTITY, AnalyticsMetric.FBA_QUANTITY] ),
    MetricCalculation( metric=AnalyticsMetric.NET_QUANTITY, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.QUANTITY, AnalyticsMetric.RETURN_QUANTITY], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_RETURN_QUANTITY, AnalyticsMetric.FBA_QUANTITY] ),
    MetricCalculation( metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_RETURN_QUANTITY, AnalyticsMetric.FBM_QUANTITY] ),
    MetricCalculation( metric=AnalyticsMetric.RETURN_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.RETURN_QUANTITY, AnalyticsMetric.QUANTITY], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.RETURN_QUANTITY, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_RETURN_QUANTITY, AnalyticsMetric.FBM_RETURN_QUANTITY]),
    MetricCalculation( metric=AnalyticsMetric.FEES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_FEES, AnalyticsMetric.FBA_FEES] ),
    MetricCalculation( metric=AnalyticsMetric.NON_FEES_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_NON_FEES_EXPENSES, AnalyticsMetric.FBA_NON_FEES_EXPENSES] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_FEES, AnalyticsMetric.FBA_NON_FEES_EXPENSES] ),
    MetricCalculation( metric=AnalyticsMetric.FBM_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_FEES, AnalyticsMetric.FBM_NON_FEES_EXPENSES] ),
    MetricCalculation( metric=AnalyticsMetric.GROSS_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_EXPENSES, AnalyticsMetric.FBM_EXPENSES], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.NET_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.GROSS_EXPENSES, AnalyticsMetric.MISC_EXPENSES], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.NET_EXPENSES, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.GROSS_EXPENSES, AnalyticsMetric.SPEND], level=3 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_NET_REVENUE, AnalyticsMetric.FBA_EXPENSES], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_NET_REVENUE, AnalyticsMetric.FBM_EXPENSES], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.GROSS_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.NET_REVENUE,AnalyticsMetric.GROSS_EXPENSES], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.NET_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.NET_REVENUE,AnalyticsMetric.NET_EXPENSES], level=4 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_PAYOUT_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_NET_PROCEEDS, AnalyticsMetric.FBA_REVENUE], level=4 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_PAYOUT_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_NET_PROCEEDS, AnalyticsMetric.FBM_REVENUE], level=4 ),
    MetricCalculation( metric=AnalyticsMetric.PAYOUT_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.NET_PROCEEDS, AnalyticsMetric.REVENUE], level=5 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_PAYOUT_PER_UNIT, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_NET_PROCEEDS, AnalyticsMetric.FBA_QUANTITY],avoidMultiplier=True, level=5 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_PAYOUT_PER_UNIT, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_NET_PROCEEDS, AnalyticsMetric.FBM_QUANTITY],avoidMultiplier=True, level=5 ),
    MetricCalculation( metric=AnalyticsMetric.PAYOUT_PER_UNIT, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.NET_PROCEEDS, AnalyticsMetric.QUANTITY],avoidMultiplier=True, level=5 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_REVENUE, AnalyticsMetric.FBA_QUANTITY],avoidMultiplier=True, level=1 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.FBM_QUANTITY],avoidMultiplier=True, level=1 ),
    MetricCalculation( metric=AnalyticsMetric.AVERAGE_SALE_PRICE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.REVENUE, AnalyticsMetric.QUANTITY] , avoidMultiplier=True, level=2),
    MetricCalculation( metric=AnalyticsMetric.CTR, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.CLICKS, AnalyticsMetric.IMPRESSIONS] ),
    MetricCalculation( metric=AnalyticsMetric.ACOS, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.SPEND, AnalyticsMetric.AD_SALES] ),
    MetricCalculation( metric=AnalyticsMetric.CPC, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.SPEND, AnalyticsMetric.CLICKS], avoidMultiplier=True ),
    MetricCalculation( metric=AnalyticsMetric.ROAS, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.AD_SALES, AnalyticsMetric.SPEND], avoidMultiplier=True ),
    MetricCalculation( metric=AnalyticsMetric.CVR, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.AD_ORDERS, AnalyticsMetric.CLICKS] ),
    MetricCalculation( metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.BROWSER_SESSIONS, AnalyticsMetric.SESSIONS] ),
    MetricCalculation( metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.MOBILE_APP_SESSIONS, AnalyticsMetric.SESSIONS] ),
    MetricCalculation( metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.UNIT_SESSIONS, AnalyticsMetric.SESSIONS] ),
    MetricCalculation( metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.BROWSER_PAGE_VIEWS, AnalyticsMetric.PAGE_VIEWS] ),
    MetricCalculation( metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.MOBILE_APP_PAGE_VIEWS, AnalyticsMetric.PAGE_VIEWS] ),
    MetricCalculation( metric=AnalyticsMetric.BUY_BOX_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.BUY_BOX_VIEWS, AnalyticsMetric.PAGE_VIEWS] ),
    MetricCalculation( metric=AnalyticsMetric.BUY_BOX_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.BUY_BOX_VIEWS, AnalyticsMetric.PAGE_VIEWS] ),
    MetricCalculation( metric=AnalyticsMetric.PRE_TAX_REVENUE, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.REVENUE, AnalyticsMetric.TAX], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.TACOS, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.SPEND, AnalyticsMetric.PRE_TAX_REVENUE], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.ORGANIC_SALES_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.AD_SALES, AnalyticsMetric.PRE_TAX_REVENUE], level=2 )
]


METRIC_DETAILS: list[MetricDetail] = [
    MetricDetail( metric=AnalyticsMetric.TOTAL, ispercentage=False, label="Total Revenue"),
    MetricDetail( metric=AnalyticsMetric.NET_REVENUE, ispercentage=False, label="Net Revenue", description="Total value of orders after returns including tax"),
    MetricDetail( metric=AnalyticsMetric.FBA, ispercentage=False, label="FBA/Flex++", description="Amazon Fulfillment via FBA or Flex or others similar"),
    MetricDetail( metric=AnalyticsMetric.FBM, ispercentage=False, label="Merchant Fulfilled", description="Easy Ship or Self Ship"),
    MetricDetail( metric=AnalyticsMetric.FBA_REVENUE_PERCENTAGE, ispercentage=False, label="FBA Revenue %", description="FBA Revenue as a percentage of total revenue"),
    MetricDetail( metric=AnalyticsMetric.FBM_REVENUE_PERCENTAGE, ispercentage=False, label="FBM Revenue %", description="FBM Revenue as a percentage of total revenue"),
    MetricDetail( metric=AnalyticsMetric.FBM_NET_REVENUE, ispercentage=False, label="FBM Net Revenue", description="Total value of FBM orders after returns including tax"),
    MetricDetail( metric=AnalyticsMetric.FBA_NET_REVENUE, ispercentage=False, label="FBA Net Revenue", description="Total value of FBA orders after returns including tax"),
    MetricDetail( metric=AnalyticsMetric.REVENUE, ispercentage=False, label="Gross Revenue", description="Total value of purchases including tax" ),
    MetricDetail( metric=AnalyticsMetric.FBA_REVENUE, ispercentage=False, label="FBA Revenue", description="Total value of FBA orders including tax" ),
    MetricDetail( metric=AnalyticsMetric.FBM_REVENUE, ispercentage=False, label="FBM Revenue", description="Total value of FBM orders including tax" ),
    MetricDetail( metric=AnalyticsMetric.RETURN_VALUE, ispercentage=False, label="Return Value", description="Total value of return orders including tax"),
    MetricDetail( metric=AnalyticsMetric.FBA_RETURN_VALUE, ispercentage=False, label="FBA Return Value", description="Total value of FBA return orders including tax"),
    MetricDetail( metric=AnalyticsMetric.FBM_RETURN_VALUE, ispercentage=False, label="FBM Return Value", description="Total value of FBM return orders including tax"),
    MetricDetail( metric=AnalyticsMetric.PAYOUT_PERCENTAGE, ispercentage=True, label="Net Payout %", description="Net revenue as a percentage of gross revenue"),
    MetricDetail( metric=AnalyticsMetric.NET_ORDERS, ispercentage=False, label="Net Orders", description="Total orders after cancellations"),
    MetricDetail( metric=AnalyticsMetric.FBA_ORDERS, ispercentage=False, label="FBA Orders", description="Total orders received for FBA"),
    MetricDetail( metric=AnalyticsMetric.FBM_ORDERS, ispercentage=False, label="FBM Orders", description="Total orders received for FBM"),
    MetricDetail( metric=AnalyticsMetric.ORDERS, ispercentage=False, label="Total Orders", description="Total orders received" ),
    MetricDetail( metric=AnalyticsMetric.CANCELLED_ORDERS, ispercentage=False, label="Cancelled Orders", description="Total orders cancelled" ),
    MetricDetail( metric=AnalyticsMetric.RETURN_VALUE, ispercentage=False, label="Return Value", description="Total value of return orders including tax"),
    MetricDetail( metric=AnalyticsMetric.TACOS, ispercentage=True, label="TACOS", description="Total Ad Cost as a percentage of Pre Tax Revenue", isReverseGrowth=True),
    MetricDetail( metric=AnalyticsMetric.ORGANIC_SALES_PERCENTAGE, ispercentage=True, label="Organic Sales %", description="Percentage of revenue generated from non-ad sources"),
    MetricDetail( metric=AnalyticsMetric.NET_QUANTITY, ispercentage=False, label="Net Units", description="Total items purchased after returns"),
    MetricDetail( metric=AnalyticsMetric.QUANTITY, ispercentage=False, label="Total Units", description="Total Items Ordered"),
    MetricDetail( metric=AnalyticsMetric.RETURN_QUANTITY, ispercentage=False, label="Return Units", description="Items returned by customers"),
    MetricDetail( metric=AnalyticsMetric.RETURN_PERCENTAGE, ispercentage=True, label="Return %", description="Items returned as a percentage of total items sold", isReverseGrowth=True),
    MetricDetail( metric=AnalyticsMetric.AVERAGE_SALE_PRICE, ispercentage=False, label="Average Selling Price", description="Average selling price of items sold"),
    MetricDetail( metric=AnalyticsMetric.NET_EXPENSES, ispercentage=False, label="Net Expenses", description="All Expenses including ad spend, storgae and other adjustments"),
    MetricDetail( metric=AnalyticsMetric.GROSS_EXPENSES, ispercentage=False, label="Gross Expenses", description="Fees, Shipping and other all order related expenses"),
    MetricDetail( metric=AnalyticsMetric.FEES, ispercentage=False, label="Fees++", description="Fees charged by the platform"),
    MetricDetail( metric=AnalyticsMetric.NON_FEES_EXPENSES, ispercentage=False, label="Shipping++", description="Additional adjustments or costs"),
    MetricDetail( metric=AnalyticsMetric.MISC_EXPENSES, ispercentage=False, label="Misc. Expenses", description="Total value of miscellaneous expenses"),
    MetricDetail( metric=AnalyticsMetric.PAYOUT_PER_UNIT, ispercentage=False, label="Net Payout/Unit", description="Average net revenue earned per item sold"),
    MetricDetail( metric=AnalyticsMetric.IMPRESSIONS, ispercentage=False, label="Impressions", description="Total number of impressions"),
    MetricDetail( metric=AnalyticsMetric.CLICKS, ispercentage=False, label="Clicks", description="Total number of clicks"),
    MetricDetail( metric=AnalyticsMetric.CTR, ispercentage=True, label="CTR", description="Percentage of clicks received out of total impressions"),
    MetricDetail( metric=AnalyticsMetric.SPEND, ispercentage=False, label="Ad Spend", description="Cost incurred for ads"),
    MetricDetail( metric=AnalyticsMetric.CPC, ispercentage=False, label="CPC", description="Average cost spent for each click"),
    MetricDetail( metric=AnalyticsMetric.AD_UNITS, ispercentage=False, label="Ad Units", description="Total number of items sold through ads"),
    MetricDetail( metric=AnalyticsMetric.AD_ORDERS, ispercentage=False, label="Ad Orders", description="Total number of orders received through ads"),
    MetricDetail( metric=AnalyticsMetric.CVR, ispercentage=True, label="CVR", description="Percentage of clicks that resulted in a purchase"),
    MetricDetail( metric=AnalyticsMetric.AD_SALES, ispercentage=False, label="Ad Sales", description="Revenue generated from ads"),
    MetricDetail( metric=AnalyticsMetric.ACOS, ispercentage=True, label="ACOS", description="Cost spent on advertising as a percentage of revenue generated from ads"),
    MetricDetail( metric=AnalyticsMetric.ROAS, ispercentage=False, label="ROAS", description="Revenue generated for every unit of ad cost", isReverseGrowth=True),
    MetricDetail( metric=AnalyticsMetric.SESSIONS, ispercentage=False, label="Sessions", description="Total number of user sessions"),
    MetricDetail( metric=AnalyticsMetric.BROWSER_SESSIONS, ispercentage=False, label="Browser Sessions", description="Sessions originating from web browsers"),
    MetricDetail( metric=AnalyticsMetric.MOBILE_APP_SESSIONS, ispercentage=False, label="Mobile App Sessions", description="Sessions originating from mobile applications"),
    MetricDetail( metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE, ispercentage=True, label="Browser Session %", description="Browser sessions as a percentage of total sessions"),
    MetricDetail( metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE, ispercentage=True, label="Mobile App Session %", description="Mobile app sessions as a percentage of total sessions"),
    MetricDetail( metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE, ispercentage=True, label="Unit Session %", description="Percentage of sessions that resulted in a purchase"),
    MetricDetail( metric=AnalyticsMetric.PAGE_VIEWS, ispercentage=False, label="Page Views", description="Total number of pages viewed"),
    MetricDetail( metric=AnalyticsMetric.BROWSER_PAGE_VIEWS, ispercentage=False, label="Browser Page Views", description="Pages viewed from web browsers"),
    MetricDetail( metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE, ispercentage=True, label="Browser Page View %", description="Browser page views as a percentage of total page views"),
    MetricDetail( metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS, ispercentage=False, label="Mobile App Page Views", description="Pages viewed from mobile apps"),
    MetricDetail( metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE, ispercentage=True, label="Mobile App Page View %", description="Mobile app page views as a percentage of total page views"),
    MetricDetail( metric=AnalyticsMetric.BUY_BOX_PERCENTAGE, ispercentage=True, label="Buy Box %", description="% times the featured offer was with your brand"),
    MetricDetail( metric=AnalyticsMetric.PRE_TAX_REVENUE, ispercentage=False, label="Pre-Tax Revenue", description="Revenue before tax"),
    MetricDetail( metric=AnalyticsMetric.TAX, ispercentage=False, label="Tax Collected", description="Total tax collected on sales"),
    MetricDetail( metric=AnalyticsMetric.FBA_TAX, ispercentage=False, label="FBA Tax", description="Total FBA tax collected on sales"),
    MetricDetail( metric=AnalyticsMetric.FBM_TAX, ispercentage=False, label="FBM Tax", description="Total FBM tax collected on sales"),
    MetricDetail( metric=AnalyticsMetric.FBA_CANCELLED_ORDERS, ispercentage=False, label="FBA Cancelled Orders", description="Total FBA orders that were cancelled"),
    MetricDetail( metric=AnalyticsMetric.FBM_CANCELLED_ORDERS, ispercentage=False, label="FBM Cancelled Orders", description="Total FBM orders that were cancelled"),
    MetricDetail( metric=AnalyticsMetric.FBA_NET_ORDERS, ispercentage=False, label="FBA Net Orders", description="Total FBA orders minus cancellations"),
    MetricDetail( metric=AnalyticsMetric.FBM_NET_ORDERS, ispercentage=False, label="FBM Net Orders", description="Total FBM orders minus cancellations"),
    MetricDetail( metric=AnalyticsMetric.FBA_QUANTITY, ispercentage=False, label="FBA Quantity", description="Total quantity of FBA orders"),
    MetricDetail( metric=AnalyticsMetric.FBM_QUANTITY, ispercentage=False, label="FBM Quantity", description="Total quantity of FBM orders"),
    MetricDetail( metric=AnalyticsMetric.FBA_RETURN_QUANTITY, ispercentage=False, label="FBA Return Quantity", description="Total quantity of FBA orders that were returned"),
    MetricDetail( metric=AnalyticsMetric.FBM_RETURN_QUANTITY, ispercentage=False, label="FBM Return Quantity", description="Total quantity of FBM orders that were returned"),
    MetricDetail( metric=AnalyticsMetric.FBA_RETURN_TAX, ispercentage=False, label="FBA Return Tax", description="Total tax collected on FBA returns"),
    MetricDetail( metric=AnalyticsMetric.FBM_RETURN_TAX, ispercentage=False, label="FBM Return Tax", description="Total tax collected on FBM returns"),
    MetricDetail( metric=AnalyticsMetric.RETURN_TAX, ispercentage=False, label="Return Tax", description="Total tax collected on returns"),
    MetricDetail( metric=AnalyticsMetric.FBA_FEES, ispercentage=False, label="FBA Fees", description="Total fees charged for FBA orders"),
    MetricDetail( metric=AnalyticsMetric.FBM_FEES, ispercentage=False, label="FBM Fees", description="Total fees charged for FBM orders"),
    MetricDetail( metric=AnalyticsMetric.FBA_NON_FEES_EXPENSES, ispercentage=False, label="FBA Shipping++", description="Additional shipping or adjustment costs for FBA orders"),
    MetricDetail( metric=AnalyticsMetric.FBM_NON_FEES_EXPENSES, ispercentage=False, label="FBM Shipping++", description="Additional shipping or adjustment costs for FBM orders"),
    MetricDetail( metric=AnalyticsMetric.FBA_EXPENSES, ispercentage=False, label="FBA Expenses", description="Total expenses for FBA orders including fees and shipping++"),
    MetricDetail( metric=AnalyticsMetric.FBM_EXPENSES, ispercentage=False, label="FBM Expenses", description="Total expenses for FBM orders including fees and shipping++"),
    MetricDetail( metric=AnalyticsMetric.FBA_NET_PROCEEDS, ispercentage=False, label="FBA Net Payout", description="Net revenue from FBA orders after fees, returns, and adjustments"),
    MetricDetail( metric=AnalyticsMetric.FBM_NET_PROCEEDS, ispercentage=False, label="FBM Net Payout", description="Net revenue from FBM orders after fees, returns, and adjustments"),
    MetricDetail( metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE, ispercentage=False, label="FBA Average Sale Price", description="Average sale price of FBA orders"),
    MetricDetail( metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE, ispercentage=False, label="FBM Average Sale Price", description="Average sale price of FBM orders"),
    MetricDetail( metric=AnalyticsMetric.FBA_PAYOUT_PERCENTAGE, ispercentage=True, label="FBA Net Payout %", description="Net revenue from FBA orders as a percentage of gross FBA revenue"),
    MetricDetail( metric=AnalyticsMetric.FBM_PAYOUT_PERCENTAGE, ispercentage=True, label="FBM Net Payout %", description="Net revenue from FBM orders as a percentage of gross FBM revenue"),
    MetricDetail( metric=AnalyticsMetric.FBA_PAYOUT_PER_UNIT, ispercentage=False, label="FBA Net Payout/Unit", description="Average net revenue earned per FBA item sold"),
    MetricDetail( metric=AnalyticsMetric.FBM_PAYOUT_PER_UNIT, ispercentage=False, label="FBM Net Payout/Unit", description="Average net revenue earned per FBM item sold"),
    MetricDetail( metric=AnalyticsMetric.UNIT_SESSIONS, ispercentage=False, label="Unit Sessions", description="Total sessions that resulted in a purchase"),
    MetricDetail( metric=AnalyticsMetric.BUY_BOX_VIEWS, ispercentage=False, label="Buy Box Views", description="Total views of the Buy Box"),
    MetricDetail( metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE, ispercentage=True, label="FBA Return %", description="Percentage of FBA orders that were returned", isReverseGrowth=True),
    MetricDetail( metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE, ispercentage=True, label="FBM Return %", description="Percentage of FBM orders that were returned", isReverseGrowth=True),
    MetricDetail( metric=AnalyticsMetric.FBA_NET_QUANTITY, ispercentage=False, label="FBA Net Quantity", description="Total FBA units sold minus returns"),
    MetricDetail( metric=AnalyticsMetric.FBM_NET_QUANTITY, ispercentage=False, label="FBM Net Quantity", description="Total FBM units sold minus returns"),
    MetricDetail( metric=AnalyticsMetric.GROSS_PROCEEDS, ispercentage=False, label="Gross Proceeds", description="Proceeds after fees and returns but before adjustments"),
    MetricDetail( metric=AnalyticsMetric.NET_PROCEEDS, ispercentage=False, label="Net Proceeds", description="Proceeds after fees, returns, and adjustments"),
    MetricDetail( metric=AnalyticsMetric.GROSS_EXPENSES, ispercentage=False, label="Gross Profit", description="Total revenue minus cost of goods sold"),
]


PERCENT_FIELDS = [d.metric.value for d in METRIC_DETAILS if d.ispercentage]
NON_PERCENT_FIELDS = [d.metric.value for d in METRIC_DETAILS if not d.ispercentage]

STATE_LITE_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.STATE_LITE, items = [
                    MetricItem(metric=AnalyticsMetric.NET_REVENUE),
                    MetricItem(metric=AnalyticsMetric.FBA_REVENUE_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.NET_ORDERS),
                    MetricItem(metric=AnalyticsMetric.NET_QUANTITY),
                    MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.GROSS_PROCEEDS)
        ])
    ]

STATE_DETAILED_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.SALES, items=[
            MetricItem(metric=AnalyticsMetric.REVENUE),
            MetricItem(metric=AnalyticsMetric.RETURN_VALUE),
            MetricItem(metric=AnalyticsMetric.NET_REVENUE),
            MetricItem(metric=AnalyticsMetric.FBA_NET_REVENUE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_REVENUE),
                MetricItem(metric=AnalyticsMetric.FBA_RETURN_VALUE),
            ]),
            MetricItem(metric=AnalyticsMetric.FBM_NET_REVENUE, items=[
                MetricItem(metric=AnalyticsMetric.FBM_REVENUE),
                MetricItem(metric=AnalyticsMetric.FBM_RETURN_VALUE),
            ]),
            MetricItem(metric=AnalyticsMetric.ORDERS),
            MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS),
            MetricItem(metric=AnalyticsMetric.NET_ORDERS),
            MetricItem(metric=AnalyticsMetric.FBA_NET_ORDERS, items=[
                MetricItem(metric=AnalyticsMetric.FBA_ORDERS),
                MetricItem(metric=AnalyticsMetric.FBA_CANCELLED_ORDERS),
            ]),
            MetricItem(metric=AnalyticsMetric.FBM_NET_ORDERS, items=[
                MetricItem(metric=AnalyticsMetric.FBM_ORDERS),
                MetricItem(metric=AnalyticsMetric.FBM_CANCELLED_ORDERS),
            ]),
            MetricItem(metric=AnalyticsMetric.QUANTITY),
            MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY),
            MetricItem(metric=AnalyticsMetric.NET_QUANTITY),
            MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE),
            MetricItem(metric=AnalyticsMetric.FBA_NET_QUANTITY, items=[
                MetricItem(metric=AnalyticsMetric.FBA_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBA_RETURN_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE),
            ]),
            MetricItem(metric=AnalyticsMetric.FBM_NET_QUANTITY, items=[
                MetricItem(metric=AnalyticsMetric.FBM_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBM_RETURN_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE),
            ]),
            MetricItem(metric=AnalyticsMetric.FEES),
            MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES),
            MetricItem(metric=AnalyticsMetric.GROSS_EXPENSES),
            MetricItem(metric=AnalyticsMetric.FBA_EXPENSES, items=[
                MetricItem(metric=AnalyticsMetric.FBA_FEES),
                MetricItem(metric=AnalyticsMetric.FBA_NON_FEES_EXPENSES),
            ]),
            MetricItem(metric=AnalyticsMetric.FBM_EXPENSES, items=[
                MetricItem(metric=AnalyticsMetric.FBM_FEES),
                MetricItem(metric=AnalyticsMetric.FBM_NON_FEES_EXPENSES),
            ]),
            MetricItem(metric=AnalyticsMetric.FBA_NET_PROCEEDS, items=[
                MetricItem(metric=AnalyticsMetric.FBA_PAYOUT_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.FBA_PAYOUT_PER_UNIT),
            ]),
            MetricItem(metric=AnalyticsMetric.FBM_NET_PROCEEDS, items=[
                MetricItem(metric=AnalyticsMetric.FBM_PAYOUT_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.FBM_PAYOUT_PER_UNIT),
            ]),
            MetricItem(metric=AnalyticsMetric.GROSS_PROCEEDS),
            MetricItem(metric=AnalyticsMetric.FBA_NET_PROCEEDS),
            MetricItem(metric=AnalyticsMetric.FBM_NET_PROCEEDS),
        ])
    ]

ALL_STATE_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.STATE_DETAILED, items = [
            MetricItem(metric=AnalyticsMetric.REVENUE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_REVENUE),
                MetricItem(metric=AnalyticsMetric.FBM_REVENUE),
                MetricItem(metric=AnalyticsMetric.REVENUE, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.RETURN_VALUE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_RETURN_VALUE),
                MetricItem(metric=AnalyticsMetric.FBM_RETURN_VALUE),
                MetricItem(metric=AnalyticsMetric.RETURN_VALUE, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.NET_REVENUE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_NET_REVENUE),
                MetricItem(metric=AnalyticsMetric.FBM_NET_REVENUE),
                MetricItem(metric=AnalyticsMetric.NET_REVENUE, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.ORDERS, items=[
                MetricItem(metric=AnalyticsMetric.FBA_ORDERS),
                MetricItem(metric=AnalyticsMetric.FBM_ORDERS),
                MetricItem(metric=AnalyticsMetric.ORDERS, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS, items=[
                MetricItem(metric=AnalyticsMetric.FBA_CANCELLED_ORDERS),
                MetricItem(metric=AnalyticsMetric.FBM_CANCELLED_ORDERS),
                MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.NET_ORDERS, items=[
                MetricItem(metric=AnalyticsMetric.FBA_NET_ORDERS),
                MetricItem(metric=AnalyticsMetric.FBM_NET_ORDERS),
                MetricItem(metric=AnalyticsMetric.NET_ORDERS, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.QUANTITY, items=[
                MetricItem(metric=AnalyticsMetric.FBA_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBM_QUANTITY),
                MetricItem(metric=AnalyticsMetric.QUANTITY, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY, items=[
                MetricItem(metric=AnalyticsMetric.FBA_RETURN_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBM_RETURN_QUANTITY),
                MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.NET_QUANTITY, items=[
                MetricItem(metric=AnalyticsMetric.FBA_NET_QUANTITY),
                MetricItem(metric=AnalyticsMetric.FBM_NET_QUANTITY),
                MetricItem(metric=AnalyticsMetric.NET_QUANTITY, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE),
                MetricItem(metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE),
                MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.FEES, items=[
                MetricItem(metric=AnalyticsMetric.FBA_FEES),
                MetricItem(metric=AnalyticsMetric.FBM_FEES),
                MetricItem(metric=AnalyticsMetric.FEES, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES, items=[
                MetricItem(metric=AnalyticsMetric.FBA_NON_FEES_EXPENSES),
                MetricItem(metric=AnalyticsMetric.FBM_NON_FEES_EXPENSES),
                MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.GROSS_EXPENSES, items=[
                MetricItem(metric=AnalyticsMetric.FBA_EXPENSES),
                MetricItem(metric=AnalyticsMetric.FBM_EXPENSES),
                MetricItem(metric=AnalyticsMetric.GROSS_EXPENSES, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.GROSS_PROCEEDS, items=[
                MetricItem(metric=AnalyticsMetric.FBA_NET_PROCEEDS),
                MetricItem(metric=AnalyticsMetric.FBM_NET_PROCEEDS),
                MetricItem(metric=AnalyticsMetric.GROSS_PROCEEDS, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE, items=[
                MetricItem(metric=AnalyticsMetric.FBA_PAYOUT_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.FBM_PAYOUT_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE, label="Total"),
            ]),
            MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT, items=[
                MetricItem(metric=AnalyticsMetric.FBA_PAYOUT_PER_UNIT),
                MetricItem(metric=AnalyticsMetric.FBM_PAYOUT_PER_UNIT),
                MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT, label="Total"),
            ]),
        ])
    ]

MONTH_DATE_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.SALES, items=[
            MetricItem(metric=AnalyticsMetric.REVENUE),
            MetricItem(metric=AnalyticsMetric.RETURN_VALUE),
            MetricItem(metric=AnalyticsMetric.NET_REVENUE),
            MetricItem(metric=AnalyticsMetric.ORDERS),
            MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS),
            MetricItem(metric=AnalyticsMetric.NET_ORDERS),
            MetricItem(metric=AnalyticsMetric.QUANTITY),
            MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY),
            MetricItem(metric=AnalyticsMetric.NET_QUANTITY),
            MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE),
            MetricItem(metric=AnalyticsMetric.FEES),
            MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES),
            MetricItem(metric=AnalyticsMetric.SPEND),
            MetricItem(metric=AnalyticsMetric.MISC_EXPENSES),
            MetricItem(metric=AnalyticsMetric.NET_EXPENSES),
            MetricItem(metric=AnalyticsMetric.NET_PROCEEDS),
            MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT),
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.ADVERTISEMENT, items = [
            MetricItem(metric=AnalyticsMetric.IMPRESSIONS),
            MetricItem(metric=AnalyticsMetric.CLICKS),
            MetricItem(metric=AnalyticsMetric.CTR),
            MetricItem(metric=AnalyticsMetric.SPEND),
            MetricItem(metric=AnalyticsMetric.CPC),
            MetricItem(metric=AnalyticsMetric.AD_UNITS),
            MetricItem(metric=AnalyticsMetric.AD_ORDERS),
            MetricItem(metric=AnalyticsMetric.CVR),
            MetricItem(metric=AnalyticsMetric.AD_SALES),
            MetricItem(metric=AnalyticsMetric.ACOS),
            MetricItem(metric=AnalyticsMetric.ROAS),
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.TRAFFIC, items = [
            MetricItem(metric=AnalyticsMetric.PAGE_VIEWS),
            MetricItem(metric=AnalyticsMetric.SESSIONS),
            MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE),
        ])
    ]

MONTH_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.SALES, items=[
            MetricItem(metric=AnalyticsMetric.NET_REVENUE, items=[
                    MetricItem(metric=AnalyticsMetric.REVENUE),
                    MetricItem(metric=AnalyticsMetric.RETURN_VALUE),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_REVENUE, items=[
                        MetricItem(metric=AnalyticsMetric.FBA_REVENUE),
                        MetricItem(metric=AnalyticsMetric.FBA_RETURN_VALUE),
                    ]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_REVENUE, items=[
                        MetricItem(metric=AnalyticsMetric.FBM_REVENUE),
                        MetricItem(metric=AnalyticsMetric.FBM_RETURN_VALUE),
                    ])
            ]),
            MetricItem(metric=AnalyticsMetric.NET_ORDERS, items=[
                    MetricItem(metric=AnalyticsMetric.ORDERS),
                    MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_ORDERS, items=[
                        MetricItem(metric=AnalyticsMetric.FBA_ORDERS),
                        MetricItem(metric=AnalyticsMetric.FBA_CANCELLED_ORDERS),
                    ]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_ORDERS, items=[
                        MetricItem(metric=AnalyticsMetric.FBM_ORDERS),
                        MetricItem(metric=AnalyticsMetric.FBM_CANCELLED_ORDERS),
                    ])
            ]),
            MetricItem(metric=AnalyticsMetric.NET_QUANTITY, items=[
                    MetricItem(metric=AnalyticsMetric.QUANTITY),
                    MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY),
                    MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_QUANTITY, items=[
                        MetricItem(metric=AnalyticsMetric.FBA_QUANTITY),
                        MetricItem(metric=AnalyticsMetric.FBA_RETURN_QUANTITY),
                        MetricItem(metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE),
                        MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE),
                    ]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_QUANTITY, items=[
                        MetricItem(metric=AnalyticsMetric.FBM_QUANTITY),
                        MetricItem(metric=AnalyticsMetric.FBM_RETURN_QUANTITY),
                        MetricItem(metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE),
                        MetricItem(metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE),
                    ])
            ]),
            MetricItem(metric=AnalyticsMetric.GROSS_EXPENSES, items=[
                    MetricItem(metric=AnalyticsMetric.FEES),
                    MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES),
                    MetricItem(metric=AnalyticsMetric.FBA_EXPENSES, items=[
                        MetricItem(metric=AnalyticsMetric.FBA_FEES),
                        MetricItem(metric=AnalyticsMetric.FBA_NON_FEES_EXPENSES),
                    ]),
                    MetricItem(metric=AnalyticsMetric.FBM_EXPENSES, items=[
                        MetricItem(metric=AnalyticsMetric.FBM_FEES),
                        MetricItem(metric=AnalyticsMetric.FBM_NON_FEES_EXPENSES),
                    ]),
            ]),
            MetricItem(metric=AnalyticsMetric.GROSS_PROCEEDS, items=[
                    MetricItem(metric=AnalyticsMetric.FBA_NET_PROCEEDS, items=[
                        MetricItem(metric=AnalyticsMetric.FBA_PAYOUT_PERCENTAGE),
                        MetricItem(metric=AnalyticsMetric.FBA_PAYOUT_PER_UNIT),
                    ]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_PROCEEDS, items=[
                        MetricItem(metric=AnalyticsMetric.FBM_PAYOUT_PERCENTAGE),
                        MetricItem(metric=AnalyticsMetric.FBM_PAYOUT_PER_UNIT),
                    ])
            ]),
            MetricItem(metric=AnalyticsMetric.NET_EXPENSES, items=[
                    MetricItem(metric=AnalyticsMetric.GROSS_EXPENSES),
                    MetricItem(metric=AnalyticsMetric.SPEND),
                    MetricItem(metric=AnalyticsMetric.MISC_EXPENSES),
            ]),
            MetricItem(metric=AnalyticsMetric.NET_PROCEEDS),
            MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT),
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.ADVERTISEMENT, items = [
            MetricItem(metric=AnalyticsMetric.IMPRESSIONS),
            MetricItem(metric=AnalyticsMetric.CLICKS),
            MetricItem(metric=AnalyticsMetric.CTR),
            MetricItem(metric=AnalyticsMetric.SPEND),
            MetricItem(metric=AnalyticsMetric.CPC),
            MetricItem(metric=AnalyticsMetric.AD_UNITS),
            MetricItem(metric=AnalyticsMetric.AD_ORDERS),
            MetricItem(metric=AnalyticsMetric.CVR),
            MetricItem(metric=AnalyticsMetric.AD_SALES),
            MetricItem(metric=AnalyticsMetric.ACOS),
            MetricItem(metric=AnalyticsMetric.ROAS),
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.TRAFFIC, items = [
            MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE),
            MetricItem(metric=AnalyticsMetric.SESSIONS, items=[
                MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS),
                MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS),
                MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE)
            ]),
            MetricItem(metric=AnalyticsMetric.PAGE_VIEWS, items=[
                MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS),
                MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE),
                MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS),
                MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE)
            ])
        ])
]

MONTH_METER_GROUPS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.MONTH_SESSIONS_METER_GROUPS, items = [
                    MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE, label=AnalyticsMetric.BROWSER.value),
                    MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE, label=AnalyticsMetric.MOBILE_APP.value)
    ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.MONTH_PAGE_VIEWS_METER_GROUPS, items = [
                    MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE, label=AnalyticsMetric.BROWSER.value),
                    MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE, label=AnalyticsMetric.MOBILE_APP.value),
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.MONTH_CHANNEL_SALES_METER_GROUPS, items = [
                    MetricItem(metric=AnalyticsMetric.FBA_REVENUE_PERCENTAGE, label=AnalyticsMetric.FBA.value),
                    MetricItem(metric=AnalyticsMetric.FBM_REVENUE_PERCENTAGE, label=AnalyticsMetric.FBM.value),
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.MONTH_CHANNEL_PROCEEDS_METER_GROUPS, items = [
                    MetricItem(metric=AnalyticsMetric.FBA_NET_PROCEEDS, label=AnalyticsMetric.FBA.value),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_PROCEEDS, label=AnalyticsMetric.FBM.value),
        ])
    ]

MONTH_BARS: MetricGroup = MetricGroup(
        metric=AnalyticGroupMetricLabel.MONTH_BARS, items = [
                    MetricItem(metric=AnalyticsMetric.TACOS),
                    MetricItem(metric=AnalyticsMetric.ACOS),
                    MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE),
        ])

MONTH_DATA = MetricGroup(
        metric=AnalyticGroupMetricLabel.MONTH_DATA, items = [
                    MetricItem(metric=AnalyticsMetric.NET_REVENUE),
                    MetricItem(metric=AnalyticsMetric.QUANTITY),
                    MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.SPEND),
                    MetricItem(metric=AnalyticsMetric.AD_SALES),
                    MetricItem(metric=AnalyticsMetric.ROAS),
                    MetricItem(metric=AnalyticsMetric.TACOS),
                    MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
        ])

KEY_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.SALES, items = [
                    MetricItem(metric=AnalyticsMetric.NET_REVENUE),
                    MetricItem(metric=AnalyticsMetric.ORDERS),
                    MetricItem(metric=AnalyticsMetric.QUANTITY),
                    MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.ADVERTISEMENT, items = [
                    MetricItem(metric=AnalyticsMetric.SPEND),
                    MetricItem(metric=AnalyticsMetric.AD_SALES),
                    MetricItem(metric=AnalyticsMetric.AD_UNITS),
                    MetricItem(metric=AnalyticsMetric.ROAS)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.FBA_SALES, items = [
                    MetricItem(metric=AnalyticsMetric.FBA_NET_REVENUE),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_ORDERS),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_QUANTITY),
                    MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.TRAFFIC, items = [
                    MetricItem(metric=AnalyticsMetric.PAGE_VIEWS),
                    MetricItem(metric=AnalyticsMetric.SESSIONS),
                    MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE)
        ]),
]

PERIOD_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.SALES, items = [
                    MetricItem(metric=AnalyticsMetric.NET_REVENUE, items=[ MetricItem(metric=AnalyticsMetric.REVENUE), MetricItem(metric=AnalyticsMetric.RETURN_VALUE)]),
                    MetricItem(metric=AnalyticsMetric.NET_ORDERS, items=[ MetricItem(metric=AnalyticsMetric.ORDERS), MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS) ]),
                    MetricItem(metric=AnalyticsMetric.NET_QUANTITY, items=[ MetricItem(metric=AnalyticsMetric.QUANTITY), MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY), MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.TACOS),
                    MetricItem(metric=AnalyticsMetric.ORGANIC_SALES_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE),
                    MetricItem(metric=AnalyticsMetric.NET_EXPENSES, items=[ MetricItem(metric=AnalyticsMetric.FEES), MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES), MetricItem(metric=AnalyticsMetric.SPEND), MetricItem(metric=AnalyticsMetric.MISC_EXPENSES) ]),
                    MetricItem(metric=AnalyticsMetric.NET_PROCEEDS, items=[ MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT), MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE) ])
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.FBA_SALES, items = [
                    MetricItem(metric=AnalyticsMetric.FBA_NET_REVENUE, items=[MetricItem(metric=AnalyticsMetric.FBA_REVENUE), MetricItem(metric=AnalyticsMetric.FBA_RETURN_VALUE)]),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_ORDERS, items=[ MetricItem(metric=AnalyticsMetric.FBA_ORDERS), MetricItem(metric=AnalyticsMetric.FBA_CANCELLED_ORDERS) ]),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_QUANTITY, items=[ MetricItem(metric=AnalyticsMetric.FBA_QUANTITY), MetricItem(metric=AnalyticsMetric.FBA_RETURN_QUANTITY), MetricItem(metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.FBM_SALES, items = [
                    MetricItem(metric=AnalyticsMetric.FBM_NET_REVENUE, items=[MetricItem(metric=AnalyticsMetric.FBM_REVENUE), MetricItem(metric=AnalyticsMetric.FBM_RETURN_VALUE)]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_ORDERS, items=[ MetricItem(metric=AnalyticsMetric.FBM_ORDERS), MetricItem(metric=AnalyticsMetric.FBM_CANCELLED_ORDERS) ]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_QUANTITY, items=[ MetricItem(metric=AnalyticsMetric.FBM_QUANTITY), MetricItem(metric=AnalyticsMetric.FBM_RETURN_QUANTITY), MetricItem(metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.ADVERTISEMENT, items = [
                    MetricItem(metric=AnalyticsMetric.IMPRESSIONS),
                    MetricItem(metric=AnalyticsMetric.CLICKS, items=[ MetricItem(metric=AnalyticsMetric.CTR) ]),
                    MetricItem(metric=AnalyticsMetric.SPEND, items=[ MetricItem(metric=AnalyticsMetric.CPC) ]),
                    MetricItem(metric=AnalyticsMetric.AD_UNITS, items=[ MetricItem(metric=AnalyticsMetric.AD_ORDERS), MetricItem(metric=AnalyticsMetric.CVR) ]),
                    MetricItem(metric=AnalyticsMetric.AD_SALES, items=[ MetricItem(metric=AnalyticsMetric.ACOS)]),
                    MetricItem(metric=AnalyticsMetric.ROAS)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.TRAFFIC, items = [
                    MetricItem(metric=AnalyticsMetric.SESSIONS, items=[ MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS), MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS), MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.PAGE_VIEWS, items=[ MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS), MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS), MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE)
        ])
]

COMPARISON_METRICS: list[MetricGroup] = [
    MetricGroup(
        metric=AnalyticGroupMetricLabel.TRAFFIC, items = [
                    MetricItem(
                        metric=AnalyticsMetric.SESSIONS,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS,
                                items=[MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE)]),
                            MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS,
                                items=[MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE)])
                    ]),
                    MetricItem(
                        metric=AnalyticsMetric.PAGE_VIEWS,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS,
                                items=[MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE)]),
                            MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS,
                                items=[MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE)])
                    ]),
                    MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.SALES, items = [
                    MetricItem(
                        metric=AnalyticsMetric.NET_REVENUE,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.REVENUE,
                                items=[MetricItem(metric=AnalyticsMetric.FBA_REVENUE), MetricItem(metric=AnalyticsMetric.FBM_REVENUE)]),
                            MetricItem(metric=AnalyticsMetric.RETURN_VALUE,
                                items=[MetricItem(metric=AnalyticsMetric.FBA_RETURN_VALUE), MetricItem(metric=AnalyticsMetric.FBM_RETURN_VALUE)])
                    ]),
                    MetricItem(
                        metric=AnalyticsMetric.NET_QUANTITY,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.QUANTITY,
                                items=[MetricItem(metric=AnalyticsMetric.FBA_QUANTITY), MetricItem(metric=AnalyticsMetric.FBM_QUANTITY)]),
                            MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE,
                                items=[MetricItem(metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE), MetricItem(metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE)])
                    ]),
                    MetricItem(
                        metric=AnalyticsMetric.AVERAGE_SALE_PRICE,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE),
                            MetricItem(metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE)
                    ]),
                    MetricItem(metric=AnalyticsMetric.TACOS)
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.PROCEEDS, items = [
                    MetricItem(
                        metric=AnalyticsMetric.GROSS_EXPENSES,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.FEES,
                                items=[MetricItem(metric=AnalyticsMetric.FBA_FEES), MetricItem(metric=AnalyticsMetric.FBM_FEES)]),
                            MetricItem(metric=AnalyticsMetric.NON_FEES_EXPENSES,
                                items=[MetricItem(metric=AnalyticsMetric.FBA_NON_FEES_EXPENSES), MetricItem(metric=AnalyticsMetric.FBM_NON_FEES_EXPENSES)])
                    ]),
                    MetricItem(
                        metric=AnalyticsMetric.GROSS_PROCEEDS,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.FBA_NET_PROCEEDS),
                            MetricItem(metric=AnalyticsMetric.FBM_NET_PROCEEDS)
                    ]),
                    MetricItem(
                        metric=AnalyticsMetric.NET_EXPENSES,
                        items=[ 
                            MetricItem(metric=AnalyticsMetric.GROSS_EXPENSES),
                            MetricItem(metric=AnalyticsMetric.SPEND),
                            MetricItem(metric=AnalyticsMetric.MISC_EXPENSES),
                    ]),
                    MetricItem(metric=AnalyticsMetric.NET_PROCEEDS,
                               items=[ 
                            MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE),
                            MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT)
                    ])
        ]),
    MetricGroup(
        metric=AnalyticGroupMetricLabel.ADVERTISEMENT, items = [
                    MetricItem(metric=AnalyticsMetric.CTR, items=[ MetricItem(metric=AnalyticsMetric.IMPRESSIONS), MetricItem(metric=AnalyticsMetric.CLICKS) ]),
                    MetricItem(metric=AnalyticsMetric.SPEND, items=[ MetricItem(metric=AnalyticsMetric.CPC) ]),
                    MetricItem(metric=AnalyticsMetric.AD_SALES, items=[ MetricItem(metric=AnalyticsMetric.AD_ORDERS), MetricItem(metric=AnalyticsMetric.CVR) , MetricItem(metric=AnalyticsMetric.ACOS), MetricItem(metric=AnalyticsMetric.AD_UNITS) ]),
                    MetricItem(metric=AnalyticsMetric.ROAS)
        ])
]



