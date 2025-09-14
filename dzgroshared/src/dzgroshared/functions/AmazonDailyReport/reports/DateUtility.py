from datetime import datetime, timedelta
from dzgroshared.db.daily_report_group.model import MarketplaceObjectForReport
from dzgroshared.db.model import StartEndDate
from dzgroshared.utils import date_util
from pytz import timezone as PytzTimezone, utc

class MarketplaceDatesUtility:
    marketplace: MarketplaceObjectForReport
    timezone: str
    isNew: bool
    diffdates: int|None

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace
        self.timezone = marketplace.details.timezone
        self.isNew = marketplace.dates is None

    def getMarketplaceRefreshDates(self)->StartEndDate:
        if self.isNew: days = 59
        else: days = 30
        enddate = (datetime.now() - timedelta(days=1))
        tz = PytzTimezone(self.timezone)
        enddate = enddate.astimezone(tz)
        enddate = date_util.normalize_date_to_midnight(enddate.isoformat(), "UTC")
        startdate = date_util.normalize_date_to_midnight((enddate-timedelta(days=days)).isoformat(), "UTC")
        return StartEndDate(startdate=startdate, enddate=enddate)   

    def getTrafficKioskReportDates(self):
        dates = self.getMarketplaceRefreshDates()
        if self.marketplace.dates: dates.startdate = self.marketplace.dates.enddate.astimezone(PytzTimezone(self.timezone))
        return [date.strftime("%Y-%m-%d") for date in date_util.getAllDatesBetweenTwoDates(dates.startdate, dates.enddate)]

    def getEconomicsKioskReportDates(self):
        import calendar
        import datetime as dt
        dates = self.getMarketplaceRefreshDates()
        ranges: list[tuple[str,str]] = []
        current = dt.date(dates.startdate.year, dates.startdate.month, 1)

        # Normalize to last day of end month
        end_month_last_day = calendar.monthrange(dates.enddate.year, dates.enddate.month)[1]
        end_month = dt.date(dates.enddate.year, dates.enddate.month, end_month_last_day)

        while current <= end_month:
            last_day = calendar.monthrange(current.year, current.month)[1]
            month_start = dt.date(current.year, current.month, 1)
            month_end = dt.date(current.year, current.month, last_day)

            ranges.append((month_start.strftime("%Y-%m-%d"),
                        month_end.strftime("%Y-%m-%d")))

            # move to next month
            if current.month == 12:
                current = dt.date(current.year + 1, 1, 1)
            else:
                current = dt.date(current.year, current.month + 1, 1)

        return ranges

    def getAdReportDates(self, allowedDuration: int):
        dates = self.getMarketplaceRefreshDates()
        dates = [(date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")) for date in date_util.getAllDatesBetweenTwoDates(dates.startdate, dates.enddate)]
        import math
        allDates: list[tuple[str,str]] = []
        iterations = math.ceil(len(dates)/allowedDuration)
        for i in range(iterations):
            first = min(i*allowedDuration, len(dates)-1)
            last = min((i+1)*allowedDuration-1, len(dates)-1)
            allDates.append((dates[first][0], dates[last][0]))
        return allDates

    def getSPAPIReportDates(self, allowedDuration: int):
        tz = PytzTimezone(self.timezone)
        def get_midnight(date_str: str) -> datetime:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            midnight_naive = datetime.combine(date_obj, datetime.min.time())
            midnight_local = tz.localize(midnight_naive)
            return midnight_local
        
        dates = self.getMarketplaceRefreshDates()
        dates.enddate = dates.enddate + timedelta(days=1)  # Include the entire end date
        dates = [(date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")) for date in date_util.getAllDatesBetweenTwoDates(dates.startdate, dates.enddate)]
        import math
        strDates: list[tuple[str,str]] = []
        iterations = math.ceil(len(dates)/allowedDuration)
        for i in range(iterations):
            first = min(i*allowedDuration, len(dates)-1)
            last = min((i+1)*allowedDuration-1, len(dates)-1)
            strDates.append((dates[first][0], dates[last][0]))
        spapiDates: list[tuple[datetime,datetime]] = []
        for i, date in enumerate(strDates):
            start, end = date
            startdate = get_midnight(start)
            enddate = get_midnight(end)
            if i>0: startdate = startdate - timedelta(days=1)
            enddate = enddate - timedelta(microseconds=1)
            spapiDate = (startdate.astimezone(utc), enddate.astimezone(utc))
            print(spapiDate[0].isoformat(), spapiDate[1].isoformat())
            spapiDates.append(spapiDate)

        return spapiDates


                         