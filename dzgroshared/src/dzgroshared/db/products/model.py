from datetime import datetime
from pydantic import BaseModel, HttpUrl, model_validator
from pydantic.json_schema import SkipJsonSchema

class Asin(BaseModel):
    asin: str

class Sku(Asin):
    sku: str

class Parent(BaseModel):
    parentsku: str
    parentasin: str


class ProductCategory(BaseModel):
    producttype: str = 'Unspecified'
    category: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setCategory(self):
        self.category = self.producttype.replace('_',' ').title()
        return self
    
class VariationTheme(BaseModel):
    theme: list[str] = []
    variationtheme: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setDetail(self):
        self.theme = [x.replace('_'," ").title() for x in self.variationtheme.split('/')] if self.variationtheme else []
        self.variationtheme=None
        return self
    
class VariationDetails(BaseModel):
    themedetails: list[str] = []
    variationdetails: list[dict]|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setDetail(self):
        self.themedetails = []
        if self.variationdetails:
            for x in self.variationdetails:
                for k,v in x.items():
                    self.themedetails.append(f"{k.replace('_'," ").title()} : {v}")
            self.variationdetails = None
        return self
    


class AsinChild(Asin):
    image: HttpUrl|SkipJsonSchema[None] = None

class AsinChildren(BaseModel):
    asins: list[AsinChild]
    count: int|SkipJsonSchema[None] = None

class PerformanceResultParent(Sku, VariationTheme):
    children: AsinChildren

class PerformanceResultCategory(ProductCategory):
    children: AsinChildren

class PerformanceneResultAsin(Asin, VariationTheme, ProductCategory, Parent):
    sku: SkipJsonSchema[None]=None
    image: HttpUrl|SkipJsonSchema[None] = None

class PerformanceneResultSku(Sku, VariationTheme, ProductCategory, Parent):
    image: HttpUrl|SkipJsonSchema[None] = None

class AsinView(Asin, VariationTheme, ProductCategory, Parent):
    images: list[HttpUrl]|SkipJsonSchema[None] = None
    title: str
    lastUpdatedDate: datetime|SkipJsonSchema[None]=None
    
class Product(Sku, ProductCategory, VariationTheme, VariationDetails):
    fulfillment: str|SkipJsonSchema[None]=None
    parentsku: str|SkipJsonSchema[None]=None
    parentasin: str|SkipJsonSchema[None]=None
    images: list[HttpUrl] = []
    image: HttpUrl|SkipJsonSchema[None]=None
    title: str|SkipJsonSchema[None]=None
    lastUpdatedDate: datetime|SkipJsonSchema[None]=None
    children: int|SkipJsonSchema[None]=None
    childskus: list[str]|SkipJsonSchema[None]=None