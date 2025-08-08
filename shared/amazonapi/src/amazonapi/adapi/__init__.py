"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from models.amazonapi.model import AmazonApiObject
from amazonapi.adapi.sp import AdApiSPClient
from amazonapi.adapi.common import AdApiCommonClient

class AdApiClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def sp(self):
        return AdApiSPClient(self.object)

    @cached_property
    def common(self):
        return AdApiCommonClient(self.object)