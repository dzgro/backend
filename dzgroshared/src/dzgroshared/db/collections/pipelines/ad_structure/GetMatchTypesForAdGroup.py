from bson import ObjectId


def pipeline(uid: str, marketplace: ObjectId, adgroup: str):
    return  [
    {
        '$match': {
            "uid": uid,
            "marketplace": marketplace,
            'assettype': 'Target', 
            'parent': adgroup, 
            'state': 'ENABLED', 
            'negative': False, 
            'adproduct': 'SPONSORED_PRODUCTS', 
            'deliverystatus': 'DELIVERING'
        }
    }, {
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
        '$addFields': {
            'perf': {
                '$first': '$perf'
            }
        }
    }, {
        '$group': {
            '_id': '$targetdetails.matchType', 
            'count': {'$sum': 1},
            'impressions': {
                '$sum': '$perf.impressions'
            }, 
            'clicks': {
                '$sum': '$perf.clicks'
            }, 
            'spend': {
                '$sum': '$perf.spend'
            }, 
            'sales': {
                '$sum': '$perf.sales'
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
            'partitionBy': '$parent', 
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
            'matchtype': '$_id', 
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
    }, {
        '$project': {
            '_id': 0
        }
    }
]