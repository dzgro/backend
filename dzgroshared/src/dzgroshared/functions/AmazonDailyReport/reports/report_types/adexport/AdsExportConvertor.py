
from dzgroshared.db.enums import AdAssetType, AdExportType


class AdsExportConvertor:

    def __init__(self) -> None:
        pass


    def getExportData(self, adExport: AdExportType, data: list[dict], marketplace: str)->list[dict]:
        print(adExport.value)
        if adExport==AdExportType.CAMPAIGN:
            return self.campaigns(data, marketplace)
        elif adExport==AdExportType.AD_GROUP:
            return self.ad_groups(data, marketplace)
        elif adExport==AdExportType.TARGET: 
            return self.targets(data, marketplace)
        elif adExport==AdExportType.AD:
            return self.ads(data, marketplace)
    
    def campaigns(self, data: list[dict], marketplace: str) -> list[dict]:
        finaldata: list[dict] = []
        for item in data:
            asset = {
                "_id": f'{marketplace}_{item['campaignId']}',
                "assettype":AdAssetType.CAMPAIGN.value,
                "id": item['campaignId'],
                "name": item['name'],
                "state": item['state'],
                "adproduct": item['adProduct']
            }
            portfolio = item.get('portfolioId',None)
            if portfolio: asset['parent'] = portfolio

            budget = item.get('budgetCaps', {"budgetValue": None}).get("budgetValue", {"monetaryBudget": None}).get("monetaryBudget", {"amount", None}).get("amount", None)
            if budget: asset['budget'] = budget
            finaldata.append(asset)
        return finaldata

    def ad_groups(self, data: list[dict], marketplace: str) -> list[dict]:
        finaldata: list[dict] = []
        for item in data:
            asset = {
                "_id": f'{marketplace}_{item['adGroupId']}',
                "assettype":AdAssetType.AD_GROUP.value,
                "id": item['adGroupId'],
                "parent": item['campaignId'],
                "name": item['name'],
                "state": item['state'],
            }
            bid = item.get('bid', {"defaultBid": None}).get("defaultBid", None)
            if bid: asset['bid'] = bid
            finaldata.append(asset)
        return finaldata

    def targets(self, data: list[dict], marketplace: str) -> list[dict]:
        targets: list[dict] = []
        adgroupNegatives: list[dict] = []
        adgroupCampaigns: list[dict] = []
        for item in data:
            negative = item.get('negative', False)
            if negative:
                asset = {
                    "_id": f'{marketplace}_{item['targetId']}',
                    "id": item['targetId'],
                    "state": item['state'],
                    "assettype": AdAssetType.NEGATIVE_ADGROUP if 'adGroupId' in item else AdAssetType.NEGATIVE_CAMPAIGN,
                    "parent": item['adGroupId'] if 'adGroupId' in item else item['campaignId']
                }
                adgroupNegatives.append(asset) if 'adGroupId' in item else adgroupCampaigns.append(asset)
            else:
                asset = {
                    "_id": f'{marketplace}_{item['targetId']}',
                    "assettype":AdAssetType.TARGET.value,
                    "id": item['targetId'],
                    "parent": item['adGroupId'],
                    "state": item['state'],
                    "targetdetails": item.get('targetDetails', None),
                    "targettype": item.get('targetType', None)
                }
                bid = item.get('bid', {"bid": None}).get("bid", None)
                if bid: asset['bid'] = bid
                targets.append(asset)
        return targets + adgroupNegatives + adgroupCampaigns

    def ads(self, data: list[dict], marketplace: str) -> list[dict]:
        finaldata: list[dict] = []
        for item in data:
            if 'adId' in item:
                asset = {
                    "_id": f'{marketplace}_{item['adId']}',
                    "assettype":AdAssetType.AD.value,
                    "id": item['adId'],
                    "parent": item['adGroupId'],
                    "campaignid": item['campaignId'],
                    "state": item['state']
                }
                creative = item.get('creative', {})
                if creative and item['adProduct']!='SPONSORED_BRANDS':
                    products = creative.get('products', [])
                    asset['sku'] = next((x['productId'] for x in products if x['productIdType']=="SKU"), None)
                    asset['asin'] = next((x['productId'] for x in products if x['productIdType']=="ASIN"), None)
                finaldata.append(asset)
        return finaldata
