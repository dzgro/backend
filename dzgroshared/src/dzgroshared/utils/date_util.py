from datetime import datetime, timedelta, timezone, time
import re
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

def __modify( add:bool,  date:datetime, months:float=0, days:float=0, hours: float=0, minutes: float=0, seconds: float=0, milliseconds: float=0)->datetime:
    if months: days=months*30
    modify_time = timedelta(days=days,hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
    return date+modify_time if add else date-modify_time

def add( date: datetime, months: float=0, days: float=0, hours: float=0, minutes: float=0, seconds: float=0, milliseconds: float=0)->datetime:
    return __modify(True, date, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

def subtract( date: datetime, months: float=0, days: float=0, hours: float=0, minutes: float=0, seconds: float=0, milliseconds: float=0)->datetime:
    return __modify(False, date, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

def getAllDatesBetweenTwoDates( startDate: datetime, endDate: datetime)->list[datetime]:
    allDates = []
    duration = (endDate-startDate).days
    while duration>=0:
        allDates.append(startDate)
        startDate += timedelta(days=1)
        duration = (endDate-startDate).days
    return allDates

def normalize_date_to_midnight(date: str, timezone: str) -> datetime:
    """
    Given an ISO datetime string and a timezone (e.g. "Asia/Kolkata"),
    return the UTC datetime corresponding to midnight of that local date.
    """
    # Parse input datetime
    dt = datetime.fromisoformat(date)
    tz = PytzTimezone(timezone)
    # Convert to target timezone
    local_dt = dt.astimezone(tz)
    return datetime(local_dt.year, local_dt.month, local_dt.day, 0, 0, 0, tzinfo=utc)

