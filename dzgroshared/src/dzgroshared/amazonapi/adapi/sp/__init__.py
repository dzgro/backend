"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from dzgroshared.amazonapi.model import AmazonApiObject

class AdApiSPClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def spCampaignNegativeKeywordsClient(self):
        from dzgroshared.amazonapi.adapi.sp.campaign_negative_keywords.controller import SPCampaignNegativeKeywordsClient
        return SPCampaignNegativeKeywordsClient(self.object)

    @cached_property
    def spCampaignNegativeTargetingClausesClient(self):
        from dzgroshared.amazonapi.adapi.sp.campaign_negative_targeting_clauses.controller import SPCampaignNegativeTargetingClausesClient
        return SPCampaignNegativeTargetingClausesClient(self.object)

    @cached_property
    def spKeywordsClient(self):
        from dzgroshared.amazonapi.adapi.sp.keywords.controller import SPKeywordsClient
        return SPKeywordsClient(self.object)

    @cached_property
    def spProductAdsClient(self):
        from dzgroshared.amazonapi.adapi.sp.product_ads.controller import SPProductAdsClient
        return SPProductAdsClient(self.object)

    @cached_property
    def spTargetingClausesClient(self):
        from dzgroshared.amazonapi.adapi.sp.targeting_clauses.controller import SPTargetingClausesClient
        return SPTargetingClausesClient(self.object)

    @cached_property
    def spNegativeKeywordsClient(self):
        from dzgroshared.amazonapi.adapi.sp.negative_keywords.controller import SPNegativeKeywordsClient
        return SPNegativeKeywordsClient(self.object)

    @cached_property
    def spNegativeTargetingClausesClient(self):
        from dzgroshared.amazonapi.adapi.sp.negative_targeting_clauses.controller import SPNegativeTargetingClausesClient
        return SPNegativeTargetingClausesClient(self.object)

    @cached_property
    def spAdGroupsClient(self):
        from dzgroshared.amazonapi.adapi.sp.ad_groups.controller import SPAdGroupsClient
        return SPAdGroupsClient(self.object)

    @cached_property
    def spCampaignsClient(self):
        from dzgroshared.amazonapi.adapi.sp.campaigns.controller import SPCampaignsClient
        return SPCampaignsClient(self.object)
