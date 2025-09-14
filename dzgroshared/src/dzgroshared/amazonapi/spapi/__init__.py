"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from dzgroshared.amazonapi.model import AmazonApiObject




class SpApiClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def aplus(self):
        from .aplus.controller import AplusClient
        return AplusClient(self.object)

    @cached_property
    def catalog(self):
        from .catalog.controller import CatalogClient
        return CatalogClient(self.object)

    @cached_property
    def feeds(self):
        from .feeds.controller import FeedsClient
        return FeedsClient(self.object)

    @cached_property
    def finances(self):
        from .finances.controller import FinancesClient
        return FinancesClient(self.object)

    @cached_property
    def inventory(self):
        from .inventory.controller import InventoryClient
        return InventoryClient(self.object)

    @cached_property
    def listings(self):
        from .listings.controller import ListingsClient
        return ListingsClient(self.object)

    @cached_property
    def notifications(self):
        from .notifications.controller import NotificationsClient
        return NotificationsClient(self.object)

    @cached_property
    def orders(self):
        from .orders.controller import OrdersClient
        return OrdersClient(self.object)

    @cached_property
    def pricing(self):
        from .pricing.controller import PricingClient
        return PricingClient(self.object)

    @cached_property
    def product_types(self):
        from .product_types.controller import ProductTypesClient
        return ProductTypesClient(self.object)

    @cached_property
    def reports(self):
        from .reports.controller import ReportsClient
        return ReportsClient(self.object)

    @cached_property
    def sales(self):
        from .sales.controller import SalesClient
        return SalesClient(self.object)

    @cached_property
    def sellers(self):
        from .sellers.controller import SellersClient
        return SellersClient(self.object)

    @cached_property
    def solicitations(self):
        from .solicitations.controller import SolicitationsClient
        return SolicitationsClient(self.object)

    @cached_property
    def datakiosk(self):
        from .datakiosk.controller import DataKioskClient
        return DataKioskClient(self.object) 