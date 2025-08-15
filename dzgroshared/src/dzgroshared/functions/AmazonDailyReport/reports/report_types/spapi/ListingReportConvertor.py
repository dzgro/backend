

from dzgroshared.models.extras.amazon_daily_report import MarketplaceObjectForReport


class ListingReportConvertor:
    marketplace: MarketplaceObjectForReport

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace

    def addListings(self, data: list[dict]):
        listings: list[dict] = []
        for listing in data:
            item = {
                '_id': f'{str(self.marketplace.id)}_{listing["seller-sku"]}',
                "sku": listing['seller-sku'],
                "asin": listing['asin1'],
                "quantity": int(listing['quantity']) if len(listing['quantity'])>0 else 0,
                "price": float(listing['price']) if len(listing['price'])>0 else None,
                "fulfillment": listing['fulfillment-channel'],
                "status": listing['status'],
            }
            listings.append(item)
        return listings

    
