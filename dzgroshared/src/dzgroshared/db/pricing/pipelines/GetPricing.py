from dzgroshared.db.model import PyObjectId


def pipeline() -> list[dict]:
    return [
    {
        '$sort': {
            'country': 1
        }
    }, {
        '$replaceWith': {
            'country': '$country', 
            'countryCode': '$_id'
        }
    }, {
        '$lookup': {
            'from': 'pricing', 
            'let': {
                'countryCode': {
                    '$cond': {
                        'if': {
                            '$eq': [
                                '$countryCode', 'IN'
                            ]
                        }, 
                        'then': 'IN', 
                        'else': 'US'
                    }
                }
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$countryCode', '$$countryCode'
                                    ]
                                }, {
                                    '$ifNull': [
                                        '$uid', True
                                    ]
                                }, {
                                    '$ifNull': [
                                        '$marketplace', True
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'plans': 1
                    }
                }
            ], 
            'as': 'plans'
        }
    }, {
        '$replaceWith': {
            '$mergeObjects': [
                '$$ROOT', {
                    '$first': '$plans'
                }, {
                    '$cond': {
                        'if': {
                            '$eq': [
                                '$countryCode', 'IN'
                            ]
                        }, 
                        'then': {
                            'currencyCode': 'INR', 
                            'currency': '₹'
                        }, 
                        'else': {
                            'currencyCode': 'USD', 
                            'currency': {
                                '$literal': '$'
                            }
                        }
                    }
                }
            ]
        }
    }
]