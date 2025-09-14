from pydantic import BaseModel, HttpUrl, model_validator
from pydantic.json_schema import SkipJsonSchema
class ProductCategory(BaseModel):
    producttype: str = 'Unspecified'
    category: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setCategory(self):
        self.category = self.producttype.replace('_',' ').title()
        return self
    
class Product(ProductCategory):
    asin: str|SkipJsonSchema[None]=None
    sku: str|SkipJsonSchema[None]=None
    fulfillment: str|SkipJsonSchema[None]=None
    parentsku: str|SkipJsonSchema[None]=None
    parentasin: str|SkipJsonSchema[None]=None
    images: list[HttpUrl] = []
    image: HttpUrl|SkipJsonSchema[None]=None
    title: str|SkipJsonSchema[None]=None
    lastUpdatedDate: str|SkipJsonSchema[None]=None
    children: int|SkipJsonSchema[None]=None
    theme: list[str]|SkipJsonSchema[None]=None
    themedetails: list[str]|SkipJsonSchema[None]=None
    variationtheme: str|SkipJsonSchema[None]=None
    variationdetails: list[dict]|SkipJsonSchema[None]=None
    childskus: list[str]|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setDetail(self):
        if self.variationtheme:
            self.theme = [x.replace('_'," ").title() for x in self.variationtheme.split('/')]
            self.variationtheme=None
        if self.variationdetails:
            self.themedetails = []
            for x in self.variationdetails:
                for k,v in x.items():
                    self.themedetails.append(f"{k.replace('_'," ").title()} : {v}")
            self.variationdetails = None
        return self
    

class ParentProduct(Product):
    children: list[Product] = []