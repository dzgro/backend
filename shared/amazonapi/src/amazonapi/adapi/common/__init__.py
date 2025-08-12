"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from models.amazonapi.model import AmazonApiObject
from amazonapi.adapi.common.ad_accounts import AdsAccountsClient
from amazonapi.adapi.common.products import ProductsMetadataClient
from amazonapi.adapi.common.reports import ReportsClient
from amazonapi.adapi.common.exports import ExportsClient
from amazonapi.adapi.common.portfolios import PortfoliosClient
from amazonapi.adapi.common.ams import AMSClient

class AdApiCommonClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def adsAccountsClient(self):
        return AdsAccountsClient(self.object)

    @cached_property
    def productsMetadataClient(self):
        return ProductsMetadataClient(self.object)

    @cached_property
    def reportClient(self):
        return ReportsClient(self.object)

    @cached_property
    def exportsClient(self):
        return ExportsClient(self.object)

    @cached_property
    def portfoliosClient(self):
        return PortfoliosClient(self.object)

    @cached_property
    def amsClient(self):
        return AMSClient(self.object)
