from bson import ObjectId
from datetime import datetime

from models.enums import AdAssetType, AdReportType
from models.extras.amazon_daily_report import AdUnitPerformance

class AdsReportConvertor:
    marketplace: str
    

    def __init__(self, marketplace: str) -> None:
        self.marketplace = marketplace


    def getAdReportData(self, reportTypeId: AdReportType, data: list[dict])->list[dict]:
        if reportTypeId==AdReportType.SPCAMPAIGNS: return self.getCampaignData(data)
        elif reportTypeId==AdReportType.SBCAMPAIGNS: return self.getCampaignData(data)
        elif reportTypeId==AdReportType.SDCAMPAIGNS: return self.getCampaignData(data)
        elif reportTypeId==AdReportType.SPSEARCHTERM: return self.getSearchTermData(data)
        elif reportTypeId==AdReportType.SBSEARCHTERM: return self.getSearchTermData(data)
        elif reportTypeId==AdReportType.SPTARGETING: return self.getTargetingData(data)
        elif reportTypeId==AdReportType.SPADVERTISEDPRODUCT: return self.getAdvertisedProductData(data)
        elif reportTypeId==AdReportType.SDADVERTISEDPRODUCT: return self.getAdvertisedProductData(data)
        raise ValueError("invalid Report Type")


    def getPerformance(self, item: dict)->dict:
        performance = AdUnitPerformance(
            impressions=item['impressions'],
            viewableimpressions = item.get("viewableImpressions",item.get("impressionsViews",None)),
            newtobrandpurchases = item.get("newToBrandPurchases",None),
            newtobrandsales = item.get("newToBrandSales",None),
            videofirstquartileviews= item.get("videoFirstQuartileViews",None),
            videomidpointviews= item.get("videoMidpointViews",None),
            videocompleteviews= item.get("videoCompleteViews",None),
            videothirdquartileviews= item.get("videoThirdQuartileViews",None),
            videounmutes = item.get("videoUnmutes",None),
            clicks=item['clicks'],
            cost=item['cost'],
            topofsearchimpressionshare=item.get("topOfSearchImpressionShare",None),
            sales=item.get("sales14d",item.get("sales",None)),
            units=item.get("purchases14d",item.get("purchases",None)),
            orders=item.get("unitsSoldClicks14d",item.get("unitsSold",None))
        )
        return performance.model_dump(exclude_none=True)

    
    def getCampaignData(self, data: list[dict])->list[dict]:
        rows: list[dict] = list(map(lambda x: {"ad": self.getPerformance(x), "assettype":AdAssetType.CAMPAIGN.value,
            "placementclassification": x.get("placementClassification",None),
            "date":datetime.strptime(x['date'],"%Y-%m-%d"),
            "id":str(x['campaignId']),
            "_id": f'{self.marketplace}_{str(x['campaignId'])}_{x.get("placementClassification",'pc')}_{x['date']}',
            "parent":str(x.get('portfolioId')) if 'portfolioId' in x else None,
            }, data))
        return self.convertRows(rows)

    def getSearchTermData(self, data: list[dict])->list[dict]:
        rows: list[dict] = list(map(lambda x: {"ad": self.getPerformance(x), "assettype": AdAssetType.SEARCH_TERM.value,
            "date":datetime.strptime(x['date'],"%Y-%m-%d"),
            "searchterm": x['searchTerm'],
            "parent":str(x.get('adGroupId')),
            "_id": f'{self.marketplace}_{x['adGroupId']}_{x['searchTerm']}_{x['date']}',
            "id":str(x['adGroupId'])}, data))
        return self.convertRows(rows)

    def getTargetingData(self, data: list[dict])->list[dict]:
        rows: list[dict] = list(map(lambda x: {"ad": self.getPerformance(x), "assettype": AdAssetType.TARGET.value,
            "date":datetime.strptime(x['date'],"%Y-%m-%d"),
            "adgroupid": str(x['adGroupId']),
            "parent":str(x.get('adGroupId')),
            "_id": f'{self.marketplace}_{x['keywordId']}_{x['date']}',
            "id":str(x['keywordId'])}, data))
        return self.convertRows(rows)
        
    def getAdvertisedProductData(self, data: list[dict],)->list[dict]:
        rows: list[dict] = list(map(lambda x: {"ad": self.getPerformance(x), "assettype": AdAssetType.AD.value,
            "date":datetime.strptime(x['date'],"%Y-%m-%d"),
            "adgroupid": str(x['adGroupId']),
            "parent":str(x.get('adGroupId')),
            "_id": f'{self.marketplace}_{x['adId']}_{x['date']}',
            "id":str(x['adId']),
            "asin": x.get("advertisedAsin",x.get("promotedAsin",None)), 
            "sku": x.get("advertisedSku",x.get("promotedSku",None))}, data))
        return self.convertRows(rows)

    def convertRows(self, rows: list[dict]):
        return [{k:v for k,v in row.items() if v is not None} for row in rows]

    


