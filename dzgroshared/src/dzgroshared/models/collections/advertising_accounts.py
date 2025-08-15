
from pydantic import BaseModel
from dzgroshared.models.enums import CountryCode


class AdvertisingAccountRequest(BaseModel):
    name: str
    countrycode: CountryCode
    refreshtoken: str

class RenameAdvertisingAccount(BaseModel):
    id: str
    name: str
