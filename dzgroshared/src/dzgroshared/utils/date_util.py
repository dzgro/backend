from datetime import datetime, timedelta, timezone
import re
from pytz import timezone as PytzTimezone, utc
from typing import Literal

class DateHelper:

    def __init__(self):
        pass

    def getDateFormat(self, date: str)->str|None:
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

    def convertDateToZonalDate(self, date: datetime, zone: str)->datetime:
        tz = PytzTimezone(zone)
        offset_seconds = tz.utcoffset(datetime.now()).seconds
        return date + timedelta(seconds=offset_seconds)

    def getDate(self, date: str|datetime)->datetime:
        if isinstance(date, str):
            format = self.getDateFormat(date)
            if not format: raise ValueError("Invalid date format")
            return self.convertToDate(date, format)
        return date

    def convertToDate(self, date: str, format: str)->datetime:
        return datetime.strptime(date, format)
    
    def getDuration(self, startDate: datetime|str, endDate: datetime|str, unit: Literal['days', 'seconds', 'hours', 'minutes']) -> float:
        start = self.getDate(startDate)
        end = self.getDate(endDate)
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

    def convertToString(self, date: datetime, format: str)->str:
        return datetime.strftime(date, format)
    
    def getZonalCurrentDateTime(self, zone: str)->datetime:
        return datetime.now(PytzTimezone(zone))
    
    def getCurrentDateTime(self)->datetime:
        return datetime.now(timezone.utc)
    
    def changeDateFormat(self, date: datetime, format: str)->datetime:
        return self.convertToDate(self.convertToString(date, format), format)
    
    def convertToUtc(self, date: datetime)->datetime:
        return date.replace(tzinfo=utc)
    
    def getTimestamp(self)->int:
        return int(datetime.now().timestamp())
    
    def modify(self, add:bool,  date:datetime, months:float=0, days:float=0, hours: float=0, minutes: float=0, seconds: float=0, milliseconds: float=0)->datetime:
        if months: days=months*30
        modify_time = timedelta(days=days,hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
        return date+modify_time if add else date-modify_time
    
    def getAllDatesBetweenTwoDates(self, startDate: datetime, endDate: datetime)->list[datetime]:
        allDates = []
        duration = (endDate-startDate).days
        while duration>=0:
            allDates.append(startDate)
            startDate += timedelta(days=1)
            duration = (endDate-startDate).days
        return allDates