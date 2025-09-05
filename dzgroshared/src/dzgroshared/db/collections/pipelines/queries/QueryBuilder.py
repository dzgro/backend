from dzgroshared.models.enums import AnalyticsMetric, AnalyticsMetricOperation, CountryCode
from dzgroshared.models.model import MetricCalculation, MetricDetail, MetricGroup, MetricItem

calculations: list[MetricCalculation] = [
    MetricCalculation( metric=AnalyticsMetric.REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.FBA_REVENUE]),
    MetricCalculation( metric=AnalyticsMetric.RETURN_VALUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_RETURN_VALUE, AnalyticsMetric.FBA_RETURN_VALUE] ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.FBM_RETURN_VALUE] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_REVENUE, AnalyticsMetric.FBA_RETURN_VALUE] ),
    MetricCalculation( metric=AnalyticsMetric.TAX, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_TAX, AnalyticsMetric.FBA_TAX] ),
    MetricCalculation( metric=AnalyticsMetric.NET_REVENUE, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.REVENUE, AnalyticsMetric.RETURN_VALUE], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.ORDERS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_ORDERS, AnalyticsMetric.FBA_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.CANCELLED_ORDERS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_CANCELLED_ORDERS, AnalyticsMetric.FBA_CANCELLED_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.NET_ORDERS, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.ORDERS, AnalyticsMetric.CANCELLED_ORDERS], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_ORDERS, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.FBM_NET_ORDERS, AnalyticsMetric.FBM_CANCELLED_ORDERS] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_ORDERS, operation=AnalyticsMetricOperation.SUBTRACT, metrics=[AnalyticsMetric.FBA_NET_ORDERS, AnalyticsMetric.FBA_CANCELLED_ORDERS] ),
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
    MetricCalculation( metric=AnalyticsMetric.OTHER_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_OTHER_EXPENSES, AnalyticsMetric.FBA_OTHER_EXPENSES] ),
    MetricCalculation( metric=AnalyticsMetric.FBA_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_FEES, AnalyticsMetric.FBA_OTHER_EXPENSES] ),
    MetricCalculation( metric=AnalyticsMetric.FBM_EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_FEES, AnalyticsMetric.FBM_OTHER_EXPENSES] ),
    MetricCalculation( metric=AnalyticsMetric.EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_EXPENSES, AnalyticsMetric.FBM_EXPENSES], level=1 ),
    MetricCalculation( metric=AnalyticsMetric.EXPENSES, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.EXPENSES, AnalyticsMetric.SPEND], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_NET_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBA_NET_REVENUE, AnalyticsMetric.FBA_EXPENSES], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_NET_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.FBM_NET_REVENUE, AnalyticsMetric.FBM_EXPENSES], level=2 ),
    MetricCalculation( metric=AnalyticsMetric.NET_PROCEEDS, operation=AnalyticsMetricOperation.SUM, metrics=[AnalyticsMetric.NET_REVENUE,AnalyticsMetric.EXPENSES], level=3 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_PAYOUT_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_NET_PROCEEDS, AnalyticsMetric.FBA_REVENUE], level=4 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_PAYOUT_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_NET_PROCEEDS, AnalyticsMetric.FBM_REVENUE], level=4 ),
    MetricCalculation( metric=AnalyticsMetric.PAYOUT_PERCENTAGE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.NET_PROCEEDS, AnalyticsMetric.REVENUE], level=4 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_PAYOUT_PER_UNIT, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_NET_PROCEEDS, AnalyticsMetric.FBA_QUANTITY],avoidMultiplier=True, level=4 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_PAYOUT_PER_UNIT, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_NET_PROCEEDS, AnalyticsMetric.FBM_QUANTITY],avoidMultiplier=True, level=4 ),
    MetricCalculation( metric=AnalyticsMetric.PAYOUT_PER_UNIT, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.NET_PROCEEDS, AnalyticsMetric.QUANTITY],avoidMultiplier=True, level=4 ),
    MetricCalculation( metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBA_REVENUE, AnalyticsMetric.FBA_QUANTITY],avoidMultiplier=True, level=1 ),
    MetricCalculation( metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.FBM_REVENUE, AnalyticsMetric.FBM_QUANTITY],avoidMultiplier=True, level=1 ),
    MetricCalculation( metric=AnalyticsMetric.AVERAGE_SALE_PRICE, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.REVENUE, AnalyticsMetric.QUANTITY] , avoidMultiplier=True, level=2),
    MetricCalculation( metric=AnalyticsMetric.CTR, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.CLICKS, AnalyticsMetric.IMPRESSIONS] ),
    MetricCalculation( metric=AnalyticsMetric.ACOS, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.SPEND, AnalyticsMetric.AD_SALES] ),
    MetricCalculation( metric=AnalyticsMetric.CPC, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.SPEND, AnalyticsMetric.CLICKS], avoidMultiplier=True ),
    MetricCalculation( metric=AnalyticsMetric.ROAS, operation=AnalyticsMetricOperation.DIVIDE, metrics=[AnalyticsMetric.AD_SALES, AnalyticsMetric.SPEND], avoidMultiplier=True ),
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

details: list[MetricDetail] = [
    MetricDetail( metric=AnalyticsMetric.NET_REVENUE, ispercentage=False, label="Net Revenue", description="Total value of orders after returns including tax"),
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
    MetricDetail( metric=AnalyticsMetric.TACOS, ispercentage=True, label="TACOS", description="Total Ad Cost as a percentage of Pre Tax Revenue"),
    MetricDetail( metric=AnalyticsMetric.ORGANIC_SALES_PERCENTAGE, ispercentage=True, label="Organic Sales %", description="Percentage of revenue generated from non-ad sources"),
    MetricDetail( metric=AnalyticsMetric.NET_QUANTITY, ispercentage=False, label="Net Units", description="Total items purchased after returns"),
    MetricDetail( metric=AnalyticsMetric.QUANTITY, ispercentage=False, label="Total Units", description="Total Items Ordered"),
    MetricDetail( metric=AnalyticsMetric.RETURN_QUANTITY, ispercentage=False, label="Return Units", description="Items returned by customers"),
    MetricDetail( metric=AnalyticsMetric.RETURN_PERCENTAGE, ispercentage=True, label="Return %", description="Items returned as a percentage of total items sold"),
    MetricDetail( metric=AnalyticsMetric.AVERAGE_SALE_PRICE, ispercentage=False, label="Average Selling Price", description="Average selling price of items sold"),
    MetricDetail( metric=AnalyticsMetric.EXPENSES, ispercentage=False, label="Expenses", description="Total Expenses"),
    MetricDetail( metric=AnalyticsMetric.FEES, ispercentage=False, label="Fees", description="Fees charged by the platform"),
    MetricDetail( metric=AnalyticsMetric.OTHER_EXPENSES, ispercentage=False, label="Other Expenses", description="Additional adjustments or costs"),
    MetricDetail( metric=AnalyticsMetric.NET_PROCEEDS, ispercentage=False, label="Net Payout", description="Net revenue after fees, returns, and adjustments"),
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
    MetricDetail( metric=AnalyticsMetric.ROAS, ispercentage=False, label="ROAS", description="Revenue generated for every unit of ad cost"),
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
    MetricDetail( metric=AnalyticsMetric.BUY_BOX_PERCENTAGE, ispercentage=True, label="Buy Box %", description="% times the featured offer was with your brand")
]

metricGroups: list[MetricGroup] = [
    MetricGroup(
        metric="Sales", items = [
                    MetricItem(metric=AnalyticsMetric.NET_REVENUE, items=[ MetricItem(metric=AnalyticsMetric.REVENUE), MetricItem(metric=AnalyticsMetric.RETURN_VALUE)]),
                    MetricItem(metric=AnalyticsMetric.NET_ORDERS, items=[ MetricItem(metric=AnalyticsMetric.ORDERS), MetricItem(metric=AnalyticsMetric.CANCELLED_ORDERS) ]),
                    MetricItem(metric=AnalyticsMetric.NET_QUANTITY, items=[ MetricItem(metric=AnalyticsMetric.QUANTITY), MetricItem(metric=AnalyticsMetric.RETURN_QUANTITY), MetricItem(metric=AnalyticsMetric.RETURN_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.TACOS),
                    MetricItem(metric=AnalyticsMetric.ORGANIC_SALES_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.AVERAGE_SALE_PRICE),
                    MetricItem(metric=AnalyticsMetric.EXPENSES, items=[ MetricItem(metric=AnalyticsMetric.FEES), MetricItem(metric=AnalyticsMetric.OTHER_EXPENSES), MetricItem(metric=AnalyticsMetric.SPEND) ]),
                    MetricItem(metric=AnalyticsMetric.NET_PROCEEDS, items=[ MetricItem(metric=AnalyticsMetric.PAYOUT_PER_UNIT), MetricItem(metric=AnalyticsMetric.PAYOUT_PERCENTAGE) ])
        ]),
    MetricGroup(
        metric="FBA Sales", items = [
                    MetricItem(metric=AnalyticsMetric.FBA_NET_REVENUE, items=[MetricItem(metric=AnalyticsMetric.FBA_REVENUE), MetricItem(metric=AnalyticsMetric.FBA_RETURN_VALUE)]),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_ORDERS, items=[ MetricItem(metric=AnalyticsMetric.FBA_ORDERS), MetricItem(metric=AnalyticsMetric.FBA_CANCELLED_ORDERS) ]),
                    MetricItem(metric=AnalyticsMetric.FBA_NET_QUANTITY, items=[ MetricItem(metric=AnalyticsMetric.FBA_QUANTITY), MetricItem(metric=AnalyticsMetric.FBA_RETURN_QUANTITY), MetricItem(metric=AnalyticsMetric.FBA_RETURN_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.FBA_AVERAGE_SALE_PRICE)
        ]),
    MetricGroup(
        metric="FBM Sales", items = [
                    MetricItem(metric=AnalyticsMetric.FBM_NET_REVENUE, items=[MetricItem(metric=AnalyticsMetric.FBM_REVENUE), MetricItem(metric=AnalyticsMetric.FBM_RETURN_VALUE)]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_ORDERS, items=[ MetricItem(metric=AnalyticsMetric.FBM_ORDERS), MetricItem(metric=AnalyticsMetric.FBM_CANCELLED_ORDERS) ]),
                    MetricItem(metric=AnalyticsMetric.FBM_NET_QUANTITY, items=[ MetricItem(metric=AnalyticsMetric.FBM_QUANTITY), MetricItem(metric=AnalyticsMetric.FBM_RETURN_QUANTITY), MetricItem(metric=AnalyticsMetric.FBM_RETURN_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.FBM_AVERAGE_SALE_PRICE)
        ]),
    MetricGroup(
        metric="Advertisement", items = [
                    MetricItem(metric=AnalyticsMetric.IMPRESSIONS),
                    MetricItem(metric=AnalyticsMetric.CLICKS, items=[ MetricItem(metric=AnalyticsMetric.CTR) ]),
                    MetricItem(metric=AnalyticsMetric.SPEND, items=[ MetricItem(metric=AnalyticsMetric.CPC) ]),
                    MetricItem(metric=AnalyticsMetric.AD_UNITS, items=[ MetricItem(metric=AnalyticsMetric.AD_ORDERS), MetricItem(metric=AnalyticsMetric.CVR) ]),
                    MetricItem(metric=AnalyticsMetric.AD_SALES, items=[ MetricItem(metric=AnalyticsMetric.ACOS), MetricItem(metric=AnalyticsMetric.AD_SALES) ]),
                    MetricItem(metric=AnalyticsMetric.ROAS)
        ]),
    MetricGroup(
        metric="Traffic", items = [
                    MetricItem(metric=AnalyticsMetric.SESSIONS, items=[ MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS), MetricItem(metric=AnalyticsMetric.BROWSER_SESSIONS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS), MetricItem(metric=AnalyticsMetric.MOBILE_APP_SESSIONS_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.UNIT_SESSION_PERCENTAGE),
                    MetricItem(metric=AnalyticsMetric.PAGE_VIEWS, items=[ MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS), MetricItem(metric=AnalyticsMetric.BROWSER_PAGE_VIEWS_PERCENTAGE), MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS), MetricItem(metric=AnalyticsMetric.MOBILE_APP_PAGE_VIEWS_PERCENTAGE) ]),
                    MetricItem(metric=AnalyticsMetric.BUY_BOX_PERCENTAGE)
        ])
]

percent_fields = [d.metric.value for d in details if d.ispercentage]
non_percent_fields = [d.metric.value for d in details if not d.ispercentage]

def addMissingFields(data_key: str = "data"):
    return { "$addFields": {f"{data_key}.{key.value}": {"$round": [{ "$ifNull": [f"${data_key}.{key.value}", 0] },2]} for key in AnalyticsMetric.values()} }

def format_number(value, key, countrycode: CountryCode):
    if value is None:
        return None

    # percent formatting
    if key in percent_fields:
        return f"{value:.2f}%"

    # non-percent big number formatting
    if key in non_percent_fields:
        abs_val = abs(value)


        # Universal: thousands (K)
        if abs_val >= 1e3 and abs_val < 1e5:  # 1,000 to < 1,00,000
            return f"{abs_val/1e3:.2f} K"

        if countrycode==CountryCode.INDIA:
            # Indian system: Lacs / Crores
            if abs_val >= 1e7:  # 1 Crore
                return f"{abs_val/1e7:.2f} Cr"
            elif abs_val >= 1e5:  # 1 Lakh
                return f"{abs_val/1e5:.2f} Lacs"
        else:
            # International system: M / B
            if abs_val >= 1e9:
                return f"{abs_val/1e9:.2f} B"
            elif abs_val >= 1e6:
                return f"{abs_val/1e6:.2f} M"

        # fallback (small numbers)
        return f"{abs_val:.1f}" if isinstance(value, float) else f"{abs_val:.0f}"

    # default formatting (non-percent, not in big number keys)
    return f"{value:.2f}"


def transform(schema, data, countrycode: CountryCode, level=1):
    result: dict = {"label": schema['metric']}
    if level > 1 and "metric" in schema:
        key = AnalyticsMetric(schema['metric'])
        value = data.get(key.value)
        result['label'] = next((d.label for d in details if d.metric == key), schema['metric'])
        result["value"] = value
        result["valueString"] = format_number(value, key, countrycode)

    if schema.get("items"):
        result["items"] = [
            transform(item, data, countrycode, level + 1)
            for item in schema["items"]
        ]

    return result

def addDerivedMetrics(data_key: str = "data"):
    level1: dict = {}
    level2: dict = {}
    level3: dict = {}
    level4: dict = {}
    level5: dict = {}
    dk = f"${data_key}."
    for item in calculations:
        result: dict = {}
        if item.operation == AnalyticsMetricOperation.SUM:
            result = { "$sum": [f"{dk}{m.value}" for m in item.metrics] }
        elif item.operation == AnalyticsMetricOperation.SUBTRACT:
            result = { "$subtract": [f"{dk}{m.value}" for m in item.metrics] }
        elif item.operation == AnalyticsMetricOperation.DIVIDE:
            multiplier = 100 if not item.avoidMultiplier else 1
            result = { "$cond": [ {"$gt": [f"{dk}{item.metrics[1].value}", 0]}, {"$round": [ {"$multiply": [ {"$divide": [f"{dk}{item.metrics[0].value}", f"{dk}{item.metrics[1].value}"]}, multiplier ]}, 2 ]}, 0 ] }
        elif item.operation == AnalyticsMetricOperation.MULTIPLY:
            result = { "$multiply": [f"{dk}{m.value}" for m in item.metrics] }
        if item.level == 0:
            level1.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 1:
            level2.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 2:
            level3.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 3:
            level4.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 4:
            level5.update( {f"{data_key}.{item.metric.value}": result} )
    return [{ "$addFields": level1 }, { "$addFields": level2 }, { "$addFields": level3 }, { "$addFields": level4 }, { "$addFields": level5 }]

def addGrowth():
    return { "$addFields": { "growth": { "$arrayToObject": { "$map": { "input": { "$objectToArray": "$curr" }, "as": "kv", "in": { "k": "$$kv.k", "v": { "$let": { "vars": { "currVal": "$$kv.v.rawvalue", "preVal": { "$getField": { "input": { "$getField": { "field": "$$kv.k", "input": "$pre" } }, "field": "rawvalue" } }, "percentFields": percent_fields }, "in": { "$cond": [ { "$in": ["$$kv.k", "$$percentFields"] }, { "$cond": [ { "$lt": [{ "$abs": { "$subtract": ["$$currVal", "$$preVal"] } }, 10] }, { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 2] }, { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 1] } ] }, { "$cond": [ { "$or": [{ "$eq": ["$$preVal", 0] }, { "$eq": ["$$preVal", None] }] }, 0, { "$cond": [ { "$lt": [ { "$abs": { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] } }, 10 ] }, { "$round": [ { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] }, 2 ] }, { "$round": [ { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] }, 1 ] } ] } ] } ] } } } } } } } } }

def create_comparison_data():
    return { "$addFields": { "data": { "$arrayToObject": { "$map": { "input": { "$objectToArray": "$curr" }, "as": "kv", "in": { "k": "$$kv.k", "v": { "$let": { "vars": { "currVal": "$$kv.v", "preVal": { "$getField": { "field": "$$kv.k", "input": "$pre" } }, "growthVal": { "$getField": { "field": "$$kv.k", "input": "$growth" } } }, "in": { "curr": "$$currVal.rawvalue", "pre": "$$preVal.rawvalue", "growth": { "$cond": [ { "$in": ["$$kv.k", percent_fields] }, "$$growthVal", { "$round": ["$$growthVal", 1] } ] } } } } } } } } } }

