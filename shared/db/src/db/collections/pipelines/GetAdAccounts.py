from bson.objectid import ObjectId
from models.model import Paginator
from models.enums import CollectionType


def pipeline(uid: str, paginator: Paginator, accountId: str|None=None):

    def match():
        matchDict:dict = { 'uid': uid }
        if accountId: matchDict['_id'] = ObjectId(accountId)
        return {"$match": matchDict}
    
    def getAdAccounts():
        return { '$lookup': { 'from': CollectionType.AD_ACCOUNTS, 'let': { 'advertisingAccount': '$_id', 'uid': '$uid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$advertisingAccount', '$$advertisingAccount' ] }, { '$eq': [ '$uid', '$$uid' ] } ] } } }, {"$project": {"uid": 0, "_id": 0}} ], 'as': 'adAccounts' } }
    
    def skipAndLimit():
        return [{ '$skip': paginator.skip }, { '$limit': paginator.limit }]
    
    def project():
        return {"$project": {"refreshToken": 0, "accessToken": 0, "uid": 0}}
    
    pipeline = [match(),getAdAccounts()]
    pipeline.extend(skipAndLimit())
    return pipeline