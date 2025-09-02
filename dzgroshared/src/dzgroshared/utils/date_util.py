from datetime import datetime, timedelta, timezone, time
import re, calendar
from zoneinfo import ZoneInfo
from pytz import timezone as PytzTimezone, utc
from typing import Literal


def getDateFormat(date: str)->str|None:
    match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", date)
    if match:return "%Y-%m-%dT%H:%M:%S.%fZ"
    match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", date)
    if match: return "%Y-%m-%dT%H:%M:%SZ"
    match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", date)
    if match: return "%Y-%m-%dT%H:%M:%S%z"
    match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{2}:\d{2}", date)
    if match: return "%Y-%m-%dT%H:%M:%S.%f%z"
    match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", date)
    if match:return "%Y-%m-%dT%H:%M:%S"
    match = re.match(r"\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2} UTC", date)
    if match:return "%d.%m.%Y %H:%M:%S %Z"
    match = re.match(r"\d{2}.\d{2}.\d{4}", date)
    if match:return "%d.%m.%Y"

def convertDateToZonalDate(date: datetime, zone: str)->datetime:
    tz = PytzTimezone(zone)
    offset_seconds = tz.utcoffset(datetime.now()).seconds
    return date + timedelta(seconds=offset_seconds)

def getDate(date: str|datetime)->datetime:
    if isinstance(date, str):
        format = getDateFormat(date)
        if not format: raise ValueError("Invalid date format")
        return convertToDate(date, format)
    return date

def convertToDate(date: str, format: str)->datetime:
    return datetime.strptime(date, format)

def getDuration( startDate: datetime|str, endDate: datetime|str, unit: Literal['days', 'seconds', 'hours', 'minutes']) -> float:
    start = getDate(startDate)
    end = getDate(endDate)
    duration = end - start
    if unit == 'seconds':
        return duration.total_seconds()
    elif unit == 'days':
        return duration.days
    elif unit == 'hours':
        return duration.total_seconds() / 3600
    elif unit == 'minutes':
        return duration.total_seconds() / 60
    else:
        raise ValueError("Invalid unit for duration")

def convertToString( date: datetime, format: str)->str:
    return datetime.strftime(date, format)

def getZonalCurrentDateTime( zone: str)->datetime:
    return datetime.now(PytzTimezone(zone))

def getCurrentDateTime()->datetime:
    return datetime.now(timezone.utc)

def changeDateFormat( date: datetime, format: str)->datetime:
    return convertToDate(convertToString(date, format), format)

def convertToUtc( date: datetime)->datetime:
    return date.replace(tzinfo=utc)

def getTimestamp()->int:
    return int(datetime.now().timestamp())

def __modify( add:bool,  date:datetime, months:float, days:float, hours: float, minutes: float, seconds: float, milliseconds: float, microseconds:float)->datetime:
    if months: days=months*30
    modify_time = timedelta(days=days,hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds, microseconds=microseconds)
    return date+modify_time if add else date-modify_time

def add( date: datetime, months: float=0, days: float=0, hours: float=0, minutes: float=0, seconds: float=0, milliseconds: float=0, microseconds: float=0)->datetime:
    return __modify(True, date, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds, microseconds=microseconds)

def subtract( date: datetime, months: float=0, days: float=0, hours: float=0, minutes: float=0, seconds: float=0, milliseconds: float=0, microseconds: float=0)->datetime:
    return __modify(False, date, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds, microseconds=microseconds)

def getAllDatesBetweenTwoDates( startDate: datetime, endDate: datetime)->list[datetime]:
    allDates = []
    duration = (endDate-startDate).days
    while duration>=0:
        allDates.append(startDate)
        startDate += timedelta(days=1)
        duration = (endDate-startDate).days
    return allDates

def normalize_date_to_midnight(date: str|datetime, timezone: str) -> datetime:
    """
    Given an ISO datetime string and a timezone (e.g. "Asia/Kolkata"),
    return the UTC datetime corresponding to midnight of that local date.
    """
    # Parse input datetime
    dt = datetime.fromisoformat(date) if isinstance(date, str) else date
    tz = PytzTimezone(timezone)
    # Convert to target timezone
    local_dt = dt.astimezone(tz)
    return datetime(local_dt.year, local_dt.month, local_dt.day, 0, 0, 0, tzinfo=utc)

def getMarketplaceRefreshDates(isNew: bool, timezone: str)->tuple[datetime, datetime]:
    diff = 59 if isNew else 30
    enddate = (datetime.now() - timedelta(days=1))
    tz = PytzTimezone(timezone)
    enddate = enddate.astimezone(tz)
    enddate = normalize_date_to_midnight(enddate.isoformat(), "UTC")
    startdate = normalize_date_to_midnight((enddate-timedelta(days=diff)).isoformat(), "UTC")
    return startdate, enddate

def getTrafficKioskReportDates(timezone: str, isNew: bool = True):
    startdate, enddate = getMarketplaceRefreshDates(isNew, timezone)
    return [(date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")) for date in getAllDatesBetweenTwoDates(startdate, enddate)]

def getEconomicsKioskReportDates(timezone: str, isNew: bool = True):
    import datetime as dt
    startdate, enddate = getMarketplaceRefreshDates(isNew, timezone)
    ranges: list[tuple[str,str]] = []
    current = dt.date(startdate.year, startdate.month, 1)

    # Normalize to last day of end month
    end_month_last_day = calendar.monthrange(enddate.year, enddate.month)[1]
    end_month = dt.date(enddate.year, enddate.month, end_month_last_day)

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

def getAdReportDates(timezone: str, allowedDuration: int, isNew: bool = True):
    startdate, enddate = getMarketplaceRefreshDates(isNew, timezone)
    dates = [(date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")) for date in getAllDatesBetweenTwoDates(startdate, enddate)]
    import math
    allDates: list[tuple[str,str]] = []
    iterations = math.ceil(len(dates)/allowedDuration)
    for i in range(iterations):
        first = min(i*allowedDuration, len(dates)-1)
        last = min((i+1)*allowedDuration-1, len(dates)-1)
        allDates.append((dates[first][0], dates[last][0]))
    return allDates

def getSPAPIReportDates(timezone: str, allowedDuration: int, isNew: bool = True):
    tz = PytzTimezone(timezone)
    def get_midnight(date_str: str) -> datetime:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        midnight_naive = datetime.combine(date_obj, datetime.min.time())
        midnight_local = tz.localize(midnight_naive)
        return midnight_local
    
    startdate, enddate = getMarketplaceRefreshDates(isNew, timezone)
    enddate = enddate + timedelta(days=1)  # Include the entire end date
    dates = [(date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")) for date in getAllDatesBetweenTwoDates(startdate, enddate)]
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