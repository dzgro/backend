"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.amazonapi.adapi.sp.ad_groups import SPAdGroupsClient
from dzgroshared.amazonapi.adapi.sp.campaigns import SPCampaignsClient
from dzgroshared.amazonapi.adapi.sp.campaign_negative_keywords import SPCampaignNegativeKeywordsClient
from dzgroshared.amazonapi.adapi.sp.campaign_negative_targeting_clauses import SPCampaignNegativeTargetingClausesClient
from dzgroshared.amazonapi.adapi.sp.keywords import SPKeywordsClient
from dzgroshared.amazonapi.adapi.sp.product_ads import SPProductAdsClient
from dzgroshared.amazonapi.adapi.sp.targeting_clauses import SPTargetingClausesClient
from dzgroshared.amazonapi.adapi.sp.negative_keywords import SPNegativeKeywordsClient
from dzgroshared.amazonapi.adapi.sp.negative_targeting_clauses import SPNegativeTargetingClausesClient

class AdApiSPClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def spCampaignNegativeKeywordsClient(self):
        return SPCampaignNegativeKeywordsClient(self.object)

    @cached_property
    def spCampaignNegativeTargetingClausesClient(self):
        return SPCampaignNegativeTargetingClausesClient(self.object)

    @cached_property
    def spKeywordsClient(self):
        return SPKeywordsClient(self.object)

    @cached_property
    def spProductAdsClient(self):
        return SPProductAdsClient(self.object)

    @cached_property
    def spTargetingClausesClient(self):
        return SPTargetingClausesClient(self.object)

    @cached_property
    def spNegativeKeywordsClient(self):
        return SPNegativeKeywordsClient(self.object)

    @cached_property
    def spNegativeTargetingClausesClient(self):
        return SPNegativeTargetingClausesClient(self.object)

    @cached_property
    def spAdGroupsClient(self):
        return SPAdGroupsClient(self.object)

    @cached_property
    def spCampaignsClient(self):
        return SPCampaignsClient(self.object)
