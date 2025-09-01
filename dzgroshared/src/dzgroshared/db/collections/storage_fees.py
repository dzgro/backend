from dzgroshared.models.model import ObjectIdStr

class FnSkuStorageFees(ObjectIdStr):
    fnsku: str
    asin: str
    date: str
    fees: float
    center:str