from dzgroshared.db.model import ItemId
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.enums import Region


class AmazonApiObject(ItemId):
    isad: bool
    refreshtoken:str
    url:str
    profile: int
    marketplaceid: str
    sellerid:str
    client_id:str
    client_secret:str
    region: Region|SkipJsonSchema[None]=None
    scope: str|SkipJsonSchema[None]=None

    @model_validator(mode="before")
    def setDefaults(cls, data):
        if data.get('marketplaceid',None) is None: data['marketplaceid'] = ''
        if data.get('profile',None) is None: data['profile'] = 0
        if data.get('sellerid',None) is None: data['sellerid'] = ''
        return data