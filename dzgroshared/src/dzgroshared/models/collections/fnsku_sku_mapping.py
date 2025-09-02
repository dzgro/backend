
from pydantic import BaseModel


class FBASkuFnSkuMapping(BaseModel):
    asin: str
    sku: str
    fnsku: str