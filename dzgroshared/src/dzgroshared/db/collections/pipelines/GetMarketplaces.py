from bson.objectid import ObjectId

from dzgroshared.models.model import Paginator


def pipeline(uid: str, id: str|None=None):
    def match():
        matchDict: dict = { 'uid': uid }
        if id: matchDict['_id'] = ObjectId(id)
        return {"$match": matchDict}
    
    def getMarketplaces():
        return { '$lookup': { 'from': 'marketplaces', 'let': { 'seller': '$_id', 'uid': '$uid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$seller', '$$seller' ] }, { '$eq': [ '$uid', '$$uid' ] } ] } } }, { '$lookup': { 'from': 'country_details', 'localField': 'countryCode', 'foreignField': '_id', 'as': 'detail' } }, { '$unwind': { 'path': '$detail' } } ], 'as': 'marketplaces' } }
    
    pipeline = [match(),getMarketplaces()]
    return pipeline