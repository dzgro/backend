from datetime import datetime

from date_util import DateHelper
from models.extras.amazon_daily_report import MarketplaceObjectForReport

class TrafficReportConvertor:
    dateHelper: DateHelper
    dateFormat = "%Y-%m-%d"

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace
        self.dateHelper = DateHelper()


    def convertTrafficData(self, trafficSkus: list[dict]):
        data: list[dict] = []
        for item in trafficSkus: 
            keys = ['pageViews','sessions','browserPageViews','browserSessions','mobileAppPageViews','mobileAppSessions']
            traffic = item['traffic']
            date = datetime.strptime(item['startDate'],self.dateFormat)
            itemData = {k.lower():traffic[k] for k in keys if traffic[k]>0}
            if len(list(itemData.keys()))>0:
                if traffic['buyBoxPercentage']>0: itemData['buyboxviews']=int(traffic['buyBoxPercentage']*itemData['pageviews']/100)
                if traffic['unitSessionPercentage']>0: itemData['unitsessions']=int(traffic['unitSessionPercentage']*itemData['sessions']/100)
                data.append({"_id": f'{str(self.marketplace.id)}_{item['parentAsin']}_{item['startDate']}', 'asin': item['parentAsin'], 'date': date, "traffic": itemData})
        return data
        
