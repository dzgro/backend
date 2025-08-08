from bson import ObjectId


def pipeline(uid: str, marketplace: ObjectId, adgroup: str, matchtype: str|None):
    matchStage = {
        '$match': {
            "uid": uid,
            "marketplace": marketplace, 
            'assettype': 'Target', 
            'parent': adgroup, 
            'state': 'ENABLED', 
            'negative': False, 
            'adproduct': 'SPONSORED_PRODUCTS', 
            'deliverystatus': 'DELIVERING', 
            'targetdetails.matchType': matchtype
        }
    }
    if not matchtype: del matchStage['$match']['targetdetails.matchType']
    return [
    matchStage, {
        '$lookup': {
            'from': 'adv', 
            'let': {
                'uid': '$uid', 
                'marketplace': '$marketplace', 
                'id': '$id'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$uid', '$$uid'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$eq': [
                                        '$assettype', 'Target'
                                    ]
                                }, {
                                    '$eq': [
                                        '$id', '$$id'
                                    ]
                                }, {
                                    '$gte': [
                                        '$date', {
                                            '$dateSubtract': {
                                                'startDate': '$$NOW', 
                                                'unit': 'day', 
                                                'amount': 30
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$group': {
                        '_id': None, 
                        'impressions': {
                            '$sum': '$ad.impressions'
                        }, 
                        'clicks': {
                            '$sum': '$ad.clicks'
                        }, 
                        'spend': {
                            '$sum': '$ad.cost'
                        }, 
                        'sales': {
                            '$sum': '$ad.sales'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0
                    }
                }
            ], 
            'as': 'perf'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    '$$ROOT', {
                        '$first': '$perf'
                    }
                ]
            }
        }
    }, {
        '$addFields': {
            'spend': {
                '$ifNull': [
                    '$spend', 0
                ]
            }, 
            'sales': {
                '$ifNull': [
                    '$sales', 0
                ]
            }, 
            'impressions': {
                '$ifNull': [
                    '$impressions', 0
                ]
            }, 
            'clicks': {
                '$ifNull': [
                    '$clicks', 0
                ]
            }, 
            'acos': {
                '$cond': [
                    {
                        '$gt': [
                            '$sales', 0
                        ]
                    }, {
                        '$round': [
                            {
                                '$multiply': [
                                    {
                                        '$divide': [
                                            '$spend', '$sales'
                                        ]
                                    }, 100
                                ]
                            }, 1
                        ]
                    }, None
                ]
            }, 
            'zeroImpressions': {
                '$eq': [
                    {
                        '$ifNull': [
                            '$impressions', 0
                        ]
                    }, 0
                ]
            }, 
            'zeroClicks': {
                '$eq': [
                    {
                        '$ifNull': [
                            '$clicks', 0
                        ]
                    }, 0
                ]
            }, 
            'zeroSales': {
                '$eq': [
                    {
                        '$ifNull': [
                            '$sales', 0
                        ]
                    }, 0
                ]
            }, 
            'shouldPause': {
                '$or': [
                    {
                        '$eq': [
                            {
                                '$ifNull': [
                                    '$impressions', 0
                                ]
                            }, 0
                        ]
                    }, {
                        '$eq': [
                            {
                                '$ifNull': [
                                    '$clicks', 0
                                ]
                            }, 0
                        ]
                    }, {
                        '$eq': [
                            {
                                '$ifNull': [
                                    '$sales', 0
                                ]
                            }, 0
                        ]
                    }
                ]
            }, 
            'shouldRenew': {
                '$gt': [
                    '$sales', 0
                ]
            }
        }
    }, {
        '$project': {
            'id': 1, 
            'targetdetails': 1, 
            'targettype': 1, 
            'impressions': 1, 
            'clicks': 1, 
            'spend': 1, 
            'sales': 1, 
            'acos': 1, 
            'zeroImpressions': 1, 
            'zeroClicks': 1, 
            'zeroSales': 1, 
            'shouldPause': 1, 
            'shouldRenew': 1, 
            '_id': 0
        }
    }, {
        '$addFields': {
            'compositeScore': {
                '$add': [
                    {
                        '$multiply': [
                            '$sales', 1000000
                        ]
                    }, {
                        '$multiply': [
                            '$spend', 1000
                        ]
                    }, {
                        '$multiply': [
                            '$clicks', 10
                        ]
                    }, '$impressions'
                ]
            }
        }
    }, {
        '$setWindowFields': {
            'partitionBy': None, 
            'sortBy': {
                'compositeScore': -1
            }, 
            'output': {
                'rank': {
                    '$rank': {}
                }
            }
        }
    }, {
        '$addFields': {
            'retain': {
                '$eq': [
                    '$rank', 1
                ]
            }
        }
    }, {
        '$set': {
            'acos': {
                '$cond': [
                    {
                        '$eq': [
                            '$sales', 0
                        ]
                    }, '0%', {
                        '$concat': [
                            {
                                '$toString': {
                                    '$round': [
                                        {
                                            '$multiply': [
                                                {
                                                    '$divide': [
                                                        '$spend', '$sales'
                                                    ]
                                                }, 100
                                            ]
                                        }, 1
                                    ]
                                }
                            }, '%'
                        ]
                    }
                ]
            }, 
            'sales': {
                '$round': [
                    '$sales', 0
                ]
            }, 
            'spend': {
                '$round': [
                    '$spend', 0
                ]
            }
        }
    }
]