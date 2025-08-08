
from models.enums import AdAssetType, AdExportType


class AdsExportConvertor:

    def __init__(self) -> None:
        pass


    def getExportData(self, adExport: AdExportType, data: list[dict], marketplace: str)->list[dict]:
        print(adExport.value)
        if adExport==AdExportType.CAMPAIGN:
            data = list(map(lambda x:{**{k.lower(): v for k,v in x.items()}, "_id": f'{marketplace}_{x['campaignId']}', "assettype":AdAssetType.CAMPAIGN.value, "id": x['campaignId'], "parent": x.get('portfolioId',None)}, data)) 
        elif adExport==AdExportType.AD_GROUP:
            data = list(map(lambda x:{**{k.lower(): v for k,v in x.items()}, "_id": f'{marketplace}_{x['adGroupId']}',  "assettype": AdAssetType.AD_GROUP.value, "id": x['adGroupId'], "parent": x.get('campaignId')}, data)) 
        elif adExport==AdExportType.TARGET: 
            data = list(map(lambda x:{**{k.lower(): v for k,v in x.items()}, "_id": f'{marketplace}_{x['targetId']}',  "assettype": AdAssetType.TARGET.value, "id": x['targetId'], "parent": x.get('adGroupId',None)}, data)) 
        elif adExport==AdExportType.AD:
            data = list(filter(lambda x: 'adId' in x, data)) 
            data = list(map(lambda x:{**{k.lower(): v for k,v in x.items()}, "_id": f'{marketplace}_{x['adId']}',  "assettype": AdAssetType.AD.value,"id": x['adId'], "parent": x.get('adGroupId',None)}, data))
        return data
    


