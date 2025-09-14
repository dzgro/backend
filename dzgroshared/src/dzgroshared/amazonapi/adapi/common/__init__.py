"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property
from dzgroshared.amazonapi.model import AmazonApiObject


class AdApiCommonClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def adsAccountsClient(self):
        from dzgroshared.amazonapi.adapi.common.ad_accounts.controller import AdsAccountsClient
        return AdsAccountsClient(self.object)

    @cached_property
    def productsMetadataClient(self):
        from dzgroshared.amazonapi.adapi.common.products.controller import ProductsMetadataClient
        return ProductsMetadataClient(self.object)

    @cached_property
    def reportClient(self):
        from dzgroshared.amazonapi.adapi.common.reports.controller import ReportsClient
        return ReportsClient(self.object)

    @cached_property
    def exportsClient(self):
        from dzgroshared.amazonapi.adapi.common.exports.controller import ExportsClient
        return ExportsClient(self.object)

    @cached_property
    def portfoliosClient(self):
        from dzgroshared.amazonapi.adapi.common.portfolios.controller import PortfoliosClient
        return PortfoliosClient(self.object)

    @cached_property
    def amsClient(self):
        from dzgroshared.amazonapi.adapi.common.ams.controller import AMSClient
        return AMSClient(self.object)
