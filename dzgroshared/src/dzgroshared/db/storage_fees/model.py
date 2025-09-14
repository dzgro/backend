from dzgroshared.db.model import ObjectIdStr

class FnSkuStorageFees(ObjectIdStr):
    fnsku: str
    asin: str
    date: str
    fees: float
    center:str