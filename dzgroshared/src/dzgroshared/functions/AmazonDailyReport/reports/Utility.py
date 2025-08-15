from datetime import datetime
from dzgroshared.utils.date_util import DateHelper
from typing import Literal

def getEndDate(zone: str)->datetime:
    helper = DateHelper()
    current = helper.getZonalCurrentDateTime(zone)
    endDate = helper.changeDateFormat(current, "%Y-%m-%d")
    endDate = helper.modify(False, endDate, milliseconds=1)
    return helper.changeDateFormat(endDate, "%Y-%m-%dT%H:%M:%S.%fZ")

def getConfDatesByMonths(months: int, zone: str, type: Literal['ad','spapi','kiosk'], allowedDuration: int)->list[tuple[datetime,datetime]]:
    helper = DateHelper()
    current = helper.getZonalCurrentDateTime(zone)
    endDate = helper.changeDateFormat(current, "%Y-%m-%d")
    if type=='spapi': endDate = helper.modify(False, endDate, milliseconds=1)
    if type=='ad': endDate = helper.modify(False, endDate, days=1)
    endDate = helper.convertDateToZonalDate(endDate, zone)
    if type=='spapi': endDate = helper.changeDateFormat(endDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    dates: list[tuple[datetime,datetime]] = []
    if type=='kiosk':
        startDate = helper.modify(False, endDate, months=months)
        while (endDate-startDate).days>0:
            newEndDate = helper.modify(True, startDate, days=allowedDuration)
            dates.append((startDate, newEndDate))
            startDate = newEndDate
    else:
        while months!=0:
            startDate = helper.modify(False, endDate, days=allowedDuration)
            if type=='spapi': startDate = helper.modify(True, startDate, milliseconds=1)
            if type=='ad': startDate = helper.modify(True, startDate, days=1)
            dates.append((startDate, endDate))
            endDate = startDate if type=='kiosk' else helper.modify(False, startDate, milliseconds=1) if type=='spapi' else helper.modify(False, startDate, days=1)
            months-=1
    return dates


                         