from dzgroshared.db.marketplaces.model import MarketplaceObjectForReport


class FBAInventoryConvertor:
    marketplace: MarketplaceObjectForReport
    

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace

    def convert(self, data: list[dict]):
        try:
            return [{"sku": item['sku'], "fnsku": item['fnsku'], "asin": item['asin']} for item in data]
        except Exception as e:
            print(f"Error in converting FBA Storage Fees: {e}")
            print(data)
            return []
    
    