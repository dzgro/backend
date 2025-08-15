from functools import cached_property
from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.amazonapi.adapi import AdApiClient
from dzgroshared.amazonapi.spapi import SpApiClient

class AmazonApiClient:
    def __init__(self, object: AmazonApiObject):
        self.object = object

    @cached_property
    def ad(self):
        return AdApiClient(self.object)

    @cached_property
    def spapi(self):
        return SpApiClient(self.object)