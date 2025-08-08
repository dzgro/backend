"""Amazon Selling Partner API Python SDK."""

__version__ = "1.0.0"

from functools import cached_property

from models.amazonapi.model import AmazonApiObject
from amazonapi.adapi import AdApiClient
from amazonapi.spapi import SpApiClient

class AmazonApiClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def ad(self):
        return AdApiClient(self.object)

    @cached_property
    def spapi(self):
        return SpApiClient(self.object)