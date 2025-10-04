from bson import ObjectId


def pipeline(marketplace: ObjectId, sku: str):
    return [
    {
        '$match': {
            'marketplace': marketplace, 
            'sku': sku
        }
    }, {
        '$lookup': {
            'from': 'products', 
            'let': {
                'marketplace': '$marketplace', 
                'sku': '$childskus'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$in': [
                                        '$sku', {
                                            '$ifNull': [
                                                '$$sku', []
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'asin': '$asin', 
                        'image': {
                            '$first': '$images'
                        }, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'children'
        }
    }, {
        '$set': {
            'children': {
                '$let': {
                    'vars': {
                        'count': {
                            '$size': '$children'
                        }
                    }, 
                    'in': {
                        '$mergeObjects': [
                            {
                                'asins': {
                                    '$slice': [
                                        '$children', 0, 5
                                    ]
                                }
                            }, {
                                '$cond': {
                                    'if': {
                                        '$gt': [
                                            '$$count', 5
                                        ]
                                    }, 
                                    'then': {
                                        'count': {
                                            '$subtract': [
                                                '$$count', 5
                                            ]
                                        }
                                    }, 
                                    'else': {}
                                }
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$project': {
            'sku': 1, 
            'asin': 1, 
            'title': 1, 
            'children': 1, 
            'producttype': 1,
            'images': 1,
            'variationtheme': 1, 
            '_id': 0
        }
    }
]