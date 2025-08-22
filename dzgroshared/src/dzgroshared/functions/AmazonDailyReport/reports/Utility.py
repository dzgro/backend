from datetime import datetime
from dzgroshared.utils import date_util
from typing import Literal

def getEndDate(zone: str)->datetime:
    current = date_util.getZonalCurrentDateTime(zone)
    endDate = date_util.changeDateFormat(current, "%Y-%m-%d")
    endDate = date_util.subtract(endDate, milliseconds=1)
    return date_util.changeDateFormat(endDate, "%Y-%m-%dT%H:%M:%S.%fZ")

def getConfDatesByMonths(months: int, zone: str, type: Literal['ad','spapi','kiosk'], allowedDuration: int)->list[tuple[datetime,datetime]]:
    current = date_util.getZonalCurrentDateTime(zone)
    endDate = date_util.changeDateFormat(current, "%Y-%m-%d")
    if type=='spapi': endDate = date_util.subtract(endDate, milliseconds=1)
    if type=='ad': endDate = date_util.subtract(endDate, days=1)
    endDate = date_util.convertDateToZonalDate(endDate, zone)
    if type=='spapi': endDate = date_util.changeDateFormat(endDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    dates: list[tuple[datetime,datetime]] = []
    if type=='kiosk':
        startDate = date_util.subtract(endDate, months=months)
        while (endDate-startDate).days>0:
            newEndDate = date_util.add(startDate, days=allowedDuration)
            dates.append((startDate, newEndDate))
            startDate = newEndDate
    else:
        while months!=0:
            startDate = date_util.subtract(endDate, days=allowedDuration)
            if type=='spapi': startDate = date_util.add(startDate, milliseconds=1)
            if type=='ad': startDate = date_util.add(startDate, days=1)
            dates.append((startDate, endDate))
            endDate = startDate if type=='kiosk' else date_util.subtract(startDate, milliseconds=1) if type=='spapi' else date_util.subtract(startDate, days=1)
            months-=1
    return dates


                         