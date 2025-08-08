"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from models.amazonapi.model import AmazonApiObject
from .aplus import AplusClient
from .catalog import CatalogClient
from .feeds import FeedsClient
from .finances import FinancesClient
from .inventory import InventoryClient
from .listings import ListingsClient
from .notifications import NotificationsClient
from .orders import OrdersClient
from .pricing import PricingClient
from .product_types import ProductTypesClient
from .reports import ReportsClient
from .sales import SalesClient
from .sellers import SellersClient
from .solicitations import SolicitationsClient
from .datakiosk import DataKioskClient
from typing import Optional

class SpApiClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def aplus(self):
        return AplusClient(self.object)

    @cached_property
    def catalog(self):
        return CatalogClient(self.object)

    @cached_property
    def feeds(self):
        return FeedsClient(self.object)

    @cached_property
    def finances(self):
        return FinancesClient(self.object)

    @cached_property
    def inventory(self):
        return InventoryClient(self.object)

    @cached_property
    def listings(self):
        return ListingsClient(self.object)

    @cached_property
    def notifications(self):
        return NotificationsClient(self.object)

    @cached_property
    def orders(self):
        return OrdersClient(self.object)

    @cached_property
    def pricing(self):
        return PricingClient(self.object)

    @cached_property
    def product_types(self):
        return ProductTypesClient(self.object)

    @cached_property
    def reports(self):
        return ReportsClient(self.object)

    @cached_property
    def sales(self):
        return SalesClient(self.object)

    @cached_property
    def sellers(self):
        return SellersClient(self.object)

    @cached_property
    def solicitations(self):
        return SolicitationsClient(self.object)

    @cached_property
    def datakiosk(self):
        return DataKioskClient(self.object) 