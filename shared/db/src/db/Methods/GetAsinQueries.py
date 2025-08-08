from bson import ObjectId


def getAsinQueries(marketplace: ObjectId|None):
    return {
        '$match': {
            '$expr': {
                '$or': [
                    {
                        '$eq': [
                            {
                                '$ifNull': [
                                    '$marketplace', None
                                ]
                            }, None
                        ]
                    }, {
                        '$eq': [
                            '$marketplace', marketplace
                        ]
                    }
                ]
            }
        }
    }