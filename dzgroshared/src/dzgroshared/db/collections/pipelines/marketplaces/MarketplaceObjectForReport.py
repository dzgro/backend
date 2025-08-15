from bson import ObjectId


def pipeline(marketplace: ObjectId, uid: str):
    return [ { '$match': { '_id': marketplace, 'uid': uid } }, {
        '$lookup': {
            'from': 'spapi_accounts', 
            'localField': 'seller', 
            'foreignField': '_id', 
            'pipeline': [
                {
                    '$lookup': {
                        'from': 'country_details', 
                        'localField': 'countrycode', 
                        'foreignField': '_id', 
                        'pipeline': [
                            {
                                '$project': {
                                    'url': '$spapi_url', 
                                    '_id': 0
                                }
                            }
                        ], 
                        'as': 'url'
                    }
                }, {
                    '$unwind': {
                        'path': '$url'
                    }
                }, {
                    '$replaceWith': {
                        '_id': '$_id', 
                        'sellerid': '$sellerid', 
                        'url': '$url.url', 
                        'refreshtoken': '$refreshtoken', 
                        'isad': False, 
                        'client_id': 'x', 
                        'client_secret': 'x'
                    }
                }
            ], 
            'as': 'spapi'
        }
    }, {
        '$lookup': {
            'from': 'advertising_accounts', 
            'localField': 'ad', 
            'foreignField': '_id', 
            'pipeline': [
                {
                    '$lookup': {
                        'from': 'country_details', 
                        'localField': 'countrycode', 
                        'foreignField': '_id', 
                        'pipeline': [
                            {
                                '$project': {
                                    'url': '$ad_url', 
                                    '_id': 0
                                }
                            }
                        ], 
                        'as': 'url'
                    }
                }, {
                    '$unwind': {
                        'path': '$url'
                    }
                }, {
                    '$replaceWith': {
                        '_id': '$_id', 
                        'sellerid': '$sellerid', 
                        'url': '$url.url', 
                        'refreshtoken': '$refreshtoken', 
                        'client_id': 'x', 
                        'client_secret': 'x', 
                        'isad': True
                    }
                }
            ], 
            'as': 'ad'
        }
    }, {
        '$lookup': {
            'from': 'country_details', 
            'localField': 'countrycode', 
            'foreignField': '_id', 
            'as': 'details'
        }
    }, {
        '$unwind': {
            'path': '$spapi'
        }
    }, {
        '$unwind': {
            'path': '$ad'
        }
    }, {
        '$unwind': {
            'path': '$details'
        }
    }, {
        '$set': {
            'spapi.marketplaceid': '$marketplaceid', 
            'spapi.profile': '$profileid', 
            'ad.profile': '$profileid', 
            'ad.sellerid': '$sellerid'
        }
    }]