"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.amazonapi.adapi.common.ad_accounts import AdsAccountsClient
from dzgroshared.amazonapi.adapi.common.products import ProductsMetadataClient
from dzgroshared.amazonapi.adapi.common.reports import ReportsClient
from dzgroshared.amazonapi.adapi.common.exports import ExportsClient
from dzgroshared.amazonapi.adapi.common.portfolios import PortfoliosClient
from dzgroshared.amazonapi.adapi.common.ams import AMSClient

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
