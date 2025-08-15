
from pydantic import BaseModel
from dzgroshared.models.enums import CountryCode


class SPAPIAccountRequest(BaseModel):
    sellerid: str
    name: str
    countrycode: CountryCode
    refreshtoken: str

class RenameSPAPIAccount(BaseModel):
    id: str
    name: str
