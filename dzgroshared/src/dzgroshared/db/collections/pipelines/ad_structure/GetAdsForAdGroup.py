from dzgroshared.models.model import PyObjectId

def pipeline(marketplace: PyObjectId, adgroup: str):
    return [
    {
        '$match': {
            "marketplace": marketplace,
            'assettype': 'Ad', 
            'parent': adgroup, 
            'state': 'ENABLED', 
            'adproduct': 'SPONSORED_PRODUCTS', 
            'deliverystatus': 'DELIVERING'
        }
    }, {
        '$unwind': '$creative.products'
    }, {
        '$group': {
            '_id': '$_id', 
            'ad': {
                '$first': '$id'
            }, 
            'adgroupid': {
                '$first': '$adgroupid'
            }, 
            'asin': {
                '$first': {
                    '$cond': [
                        {
                            '$eq': [
                                '$creative.products.productIdType', 'ASIN'
                            ]
                        }, '$creative.products.productId', None
                    ]
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'adv', 
            'let': {
                'marketplace': marketplace,
                'id': '$ad'
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
                                        '$assettype', 'Ad'
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
                }
            ], 
            'as': 'perf'
        }
    }, {
        '$unwind': {
            'path': '$perf', 
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$addFields': {
            'spend': {
                '$ifNull': [
                    '$perf.spend', 0
                ]
            }, 
            'sales': {
                '$ifNull': [
                    '$perf.sales', 0
                ]
            }, 
            'impressions': {
                '$ifNull': [
                    '$perf.impressions', 0
                ]
            }, 
            'clicks': {
                '$ifNull': [
                    '$perf.clicks', 0
                ]
            }, 
            'acos': {
                '$cond': [
                    {
                        '$gt': [
                            '$perf.sales', 0
                        ]
                    }, {
                        '$round': [
                            {
                                '$multiply': [
                                    {
                                        '$divide': [
                                            '$perf.spend', '$perf.sales'
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
                            '$perf.impressions', 0
                        ]
                    }, 0
                ]
            }, 
            'zeroClicks': {
                '$eq': [
                    {
                        '$ifNull': [
                            '$perf.clicks', 0
                        ]
                    }, 0
                ]
            }, 
            'zeroSales': {
                '$eq': [
                    {
                        '$ifNull': [
                            '$perf.sales', 0
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
                                    '$perf.impressions', 0
                                ]
                            }, 0
                        ]
                    }, {
                        '$eq': [
                            {
                                '$ifNull': [
                                    '$perf.clicks', 0
                                ]
                            }, 0
                        ]
                    }, {
                        '$eq': [
                            {
                                '$ifNull': [
                                    '$perf.sales', 0
                                ]
                            }, 0
                        ]
                    }
                ]
            }, 
            'shouldRenew': {
                '$gt': [
                    '$perf.sales', 0
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
        '$project': {
            'id': 1, 
            'ad': 1, 
            'parent': 1, 
            'asin': 1, 
            'sku': 1, 
            'imageurl': 1, 
            'spend': 1, 
            'sales': 1, 
            'acos': 1, 
            'impressions': 1, 
            'clicks': 1, 
            'zeroImpressions': 1, 
            'zeroClicks': 1, 
            'zeroSales': 1, 
            'shouldPause': 1, 
            'shouldRenew': 1, 
            'retain': 1
        }
    }, {
        '$lookup': {
            'from': 'adv_ads', 
            'localField': '_id', 
            'foreignField': '_id', 
            'pipeline': [
                {
                    '$replaceWith': {
                        '$first': '$products'
                    }
                }
            ], 
            'as': 'product'
        }
    }, {
        '$set': {
            'product': {
                '$arrayElemAt': [
                    '$product', 0
                ]
            }, 
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
            '_id': 0, 
            'asin': 0
        }
    }
]