import re
from models.collections.user import datetime
from models.model import Paginator
from bson import ObjectId


def pipeline(uid: str, marketplace: ObjectId, endDate: datetime, timezone:str, paginator: Paginator):
    return [
    {
        '$match': {
            'uid': uid, 
            'marketplace': marketplace, 
            'state': 'ENABLED', 
            'deliveryStatus': 'DELIVERING', 
            'adProduct': 'SPONSORED_PRODUCTS', 
            # 'campaignId': '168298282334797'
        }
    }, {
        '$set': {
            'asins': {
                '$setUnion': {
                    '$reduce': {
                        'input': '$creative.products', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', {
                                    '$cond': [
                                        {
                                            '$eq': [
                                                '$$this.productIdType', 'ASIN'
                                            ]
                                        }, [
                                            '$$this.productId'
                                        ], []
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }, {
        '$group': {
            '_id': {
                'adGroupId': '$adGroupId', 
                'campaignId': '$$ROOT.campaignId', 
                'marketplace': '$marketplace'
            }, 
            'asins': {
                '$push': {
                    '$first': '$asins'
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'adv_campaigns', 
            'let': {
                'campaignId': '$_id.campaignId', 
                'marketplace': '$_id.marketplace'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$campaignId', '$$campaignId'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$set': {
                        'campaignName': '$name'
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'campaignName': 1, 
                        'portfolioId': 1
                    }
                }
            ], 
            'as': 'campaignResult'
        }
    }, {
        '$lookup': {
            'from': 'adv_ad_groups', 
            'let': {
                'adGroupId': '$_id.adGroupId', 
                'marketplace': '$_id.marketplace'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$adGroupId', '$$adGroupId'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$set': {
                        'adGroupName': '$name'
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'adGroupName': 1
                    }
                }
            ], 
            'as': 'adGroupResult'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    '$_id', {
                        'asins': '$asins'
                    }, {
                        '$first': '$campaignResult'
                    }, {
                        '$first': '$adGroupResult'
                    }
                ]
            }
        }
    }, {
        '$group': {
            '_id': {
                'asins': '$asins', 
                'marketplace': '$marketplace'
            }, 
            'data': {
                '$push': {
                    'adGroupId': '$$ROOT.adGroupId', 
                    'campaignId': '$$ROOT.campaignId', 
                    'campaignName': '$$ROOT.campaignName', 
                    'adGroupName': '$$ROOT.adGroupName', 
                    'portfolioId': '$$ROOT.portfolioId'
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'adv_targets', 
            'let': {
                'adGroupIds': {
                    '$reduce': {
                        'input': '$data', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', [
                                    '$$this.adGroupId'
                                ]
                            ]
                        }
                    }
                }, 
                'marketplace': '$_id.marketplace'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$state', 'ENABLED'
                                    ]
                                }, {
                                    '$eq': [
                                        '$negative', False
                                    ]
                                }, {
                                    '$eq': [
                                        '$deliveryStatus', 'DELIVERING'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$in': [
                                        '$adGroupId', '$$adGroupIds'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'targetType': 1, 
                        'adGroupId': 1, 
                        'campaignId': 1, 
                        'targetDetails': '$targetDetails.matchType', 
                        'productCategories': '$targetDetails.productCategoryResolved'
                    }
                }, {
                    '$group': {
                        '_id': '$adGroupId', 
                        'targetType': {
                            '$first': '$$ROOT.targetType'
                        }, 
                        'targetDetails': {
                            '$addToSet': {
                                '$ifNull': [
                                    '$$ROOT.targetDetails', '$$ROOT.productCategories'
                                ]
                            }
                        }, 
                        'count': {
                            '$sum': 1
                        }
                    }
                }
            ], 
            'as': 'targets'
        }
    }, {
        '$set': {
            'data': {
                '$map': {
                    'input': '$data', 
                    'as': 'd', 
                    'in': {
                        '$mergeObjects': [
                            '$$d', {
                                '$unsetField': {
                                    'input': {
                                        '$first': {
                                            '$filter': {
                                                'input': '$targets', 
                                                'as': 't', 
                                                'cond': {
                                                    '$eq': [
                                                        '$$t._id', '$$d.adGroupId'
                                                    ]
                                                }
                                            }
                                        }
                                    }, 
                                    'field': '_id'
                                }
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$set': {
            'data': {
                '$map': {
                    'input': '$data', 
                    'as': 'x', 
                    'in': {
                        '$mergeObjects': [
                            '$$x', {
                                'options': {
                                    '$switch': {
                                        'branches': [
                                            {
                                                'case': {
                                                    '$eq': [
                                                        '$$x.targetType', 'PRODUCT_CATEGORY'
                                                    ]
                                                }, 
                                                'then': {
                                                    '$let': {
                                                        'vars': {
                                                            'data': {
                                                                '$reduce': {
                                                                    'input': {
                                                                        '$filter': {
                                                                            'input': '$data', 
                                                                            'as': 'f', 
                                                                            'cond': {
                                                                                '$eq': [
                                                                                    '$$f.targetType', 'PRODUCT'
                                                                                ]
                                                                            }
                                                                        }
                                                                    }, 
                                                                    'initialValue': [], 
                                                                    'in': {
                                                                        '$concatArrays': [
                                                                            '$$value', [
                                                                                '$$this.adGroupId'
                                                                            ]
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'in': {
                                                            'productAdGroups': '$$data'
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$and': [
                                                        {
                                                            '$eq': [
                                                                '$$x.targetType', 'PRODUCT'
                                                            ]
                                                        }, {
                                                            '$anyElementTrue': {
                                                                '$reduce': {
                                                                    'input': '$$x.targetDetails', 
                                                                    'initialValue': [], 
                                                                    'in': {
                                                                        '$concatArrays': [
                                                                            '$$value', [
                                                                                {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$regexMatch': {
                                                                                                'input': '$$this', 
                                                                                                'regex': re.compile(r"EXACT")
                                                                                            }
                                                                                        }, False, True
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }, 
                                                'then': {
                                                    '$let': {
                                                        'vars': {
                                                            'data': {
                                                                '$reduce': {
                                                                    'input': {
                                                                        '$filter': {
                                                                            'input': '$data', 
                                                                            'as': 'f', 
                                                                            'cond': {
                                                                                '$and': [
                                                                                    {
                                                                                        '$ne': [
                                                                                            '$$x.adGroupId', '$$f.adGroupId'
                                                                                        ]
                                                                                    }, {
                                                                                        '$eq': [
                                                                                            '$$x.targetType', '$$f.targetType'
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        }
                                                                    }, 
                                                                    'initialValue': [], 
                                                                    'in': {
                                                                        '$concatArrays': [
                                                                            '$$value', [
                                                                                '$$this.adGroupId'
                                                                            ]
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'in': {
                                                            'productAdGroups': '$$data'
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$and': [
                                                        {
                                                            '$eq': [
                                                                '$$x.targetType', 'KEYWORD'
                                                            ]
                                                        }, {
                                                            '$anyElementTrue': {
                                                                '$reduce': {
                                                                    'input': '$$x.targetDetails', 
                                                                    'initialValue': [], 
                                                                    'in': {
                                                                        '$concatArrays': [
                                                                            '$$value', [
                                                                                {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$regexMatch': {
                                                                                                'input': '$$this', 
                                                                                                'regex': re.compile(r"EXACT")
                                                                                            }
                                                                                        }, False, True
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }, 
                                                'then': {
                                                    '$let': {
                                                        'vars': {
                                                            'data': {
                                                                '$reduce': {
                                                                    'input': {
                                                                        '$filter': {
                                                                            'input': '$data', 
                                                                            'as': 'f', 
                                                                            'cond': {
                                                                                '$and': [
                                                                                    {
                                                                                        '$ne': [
                                                                                            '$$x.adGroupId', '$$f.adGroupId'
                                                                                        ]
                                                                                    }, {
                                                                                        '$eq': [
                                                                                            '$$x.targetType', '$$f.targetType'
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        }
                                                                    }, 
                                                                    'initialValue': [], 
                                                                    'in': {
                                                                        '$concatArrays': [
                                                                            '$$value', [
                                                                                '$$this.adGroupId'
                                                                            ]
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'in': {
                                                            'keywordAdGroups': '$$data'
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$x.targetType', 'AUTO'
                                                    ]
                                                }, 
                                                'then': {
                                                    'keywordAdGroups': {
                                                        '$reduce': {
                                                            'input': {
                                                                '$filter': {
                                                                    'input': '$data', 
                                                                    'as': 'd', 
                                                                    'cond': {
                                                                        '$eq': [
                                                                            '$$d.targetType', 'KEYWORD'
                                                                        ]
                                                                    }
                                                                }
                                                            }, 
                                                            'initialValue': [], 
                                                            'in': {
                                                                '$concatArrays': [
                                                                    '$$value', [
                                                                        '$$this.adGroupId'
                                                                    ]
                                                                ]
                                                            }
                                                        }
                                                    }, 
                                                    'productAdGroups': {
                                                        '$reduce': {
                                                            'input': {
                                                                '$filter': {
                                                                    'input': '$data', 
                                                                    'as': 'd', 
                                                                    'cond': {
                                                                        '$eq': [
                                                                            '$$d.targetType', 'PRODUCT'
                                                                        ]
                                                                    }
                                                                }
                                                            }, 
                                                            'initialValue': [], 
                                                            'in': {
                                                                '$concatArrays': [
                                                                    '$$value', [
                                                                        '$$this.adGroupId'
                                                                    ]
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        ], 
                                        'default': None
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'adv_data', 
            'let': {
                'marketplace': '$_id.marketplace', 
                'adGroupIds': {
                    '$reduce': {
                        'input': '$data', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', [
                                    '$$this.adGroupId'
                                ]
                            ]
                        }
                    }
                }, 
                'type': 'adGroup'
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
                                    '$eq': [
                                        '$type', '$$type'
                                    ]
                                }, {
                                    '$in': [
                                        '$adGroupId', '$$adGroupIds'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'marketplace': 0, 
                        'type': 0
                    }
                }, {
                    '$group': {
                        '_id': '$adGroupId', 
                        'data': {
                            '$push': '$$ROOT'
                        }
                    }
                }, {
                    '$addFields': {
                        'dates': {
                            '$let': {
                                'vars': {
                                    'currDate': {
                                        '$dateFromString': {
                                            'dateString': {
                                                '$dateToString': {
                                                    'date': {
                                                        '$dateSubtract': {
                                                            'startDate': endDate, 
                                                            'unit': 'day', 
                                                            'amount': 1
                                                        }
                                                    }, 
                                                    'timezone': timezone, 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        }
                                    }
                                }, 
                                'in': {
                                    'last30Days': [
                                        '$$currDate', {
                                            '$dateSubtract': {
                                                'startDate': '$$currDate', 
                                                'unit': 'day', 
                                                'amount': 30
                                            }
                                        }
                                    ], 
                                    'prev30Days': [
                                        {
                                            '$dateSubtract': {
                                                'startDate': '$$currDate', 
                                                'unit': 'day', 
                                                'amount': 30
                                            }
                                        }, {
                                            '$dateSubtract': {
                                                'startDate': '$$currDate', 
                                                'unit': 'day', 
                                                'amount': 60
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }, {
                    '$replaceRoot': {
                        'newRoot': {
                            '$mergeObjects': [
                                {
                                    'adGroupId': '$_id'
                                }, {
                                    '$arrayToObject': {
                                        '$reduce': {
                                            'input': {
                                                '$objectToArray': '$dates'
                                            }, 
                                            'initialValue': [], 
                                            'in': {
                                                '$let': {
                                                    'vars': {
                                                        'data': {
                                                            '$filter': {
                                                                'input': '$data', 
                                                                'as': 'f', 
                                                                'cond': {
                                                                    '$cond': [
                                                                        {
                                                                            '$eq': [
                                                                                {
                                                                                    '$type': '$$this.v'
                                                                                }, 'object'
                                                                            ]
                                                                        }, {
                                                                            '$and': [
                                                                                {
                                                                                    '$eq': [
                                                                                        '$$this.v.month', {
                                                                                            '$month': '$$f.date'
                                                                                        }
                                                                                    ]
                                                                                }, {
                                                                                    '$eq': [
                                                                                        '$$this.v.year', {
                                                                                            '$year': '$$f.date'
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }, {
                                                                            '$and': [
                                                                                {
                                                                                    '$lte': [
                                                                                        '$$f.date', {
                                                                                            '$arrayElemAt': [
                                                                                                '$$this.v', 0
                                                                                            ]
                                                                                        }
                                                                                    ]
                                                                                }, {
                                                                                    '$gt': [
                                                                                        '$$f.date', {
                                                                                            '$arrayElemAt': [
                                                                                                '$$this.v', 1
                                                                                            ]
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            }
                                                        }
                                                    }, 
                                                    'in': {
                                                        '$concatArrays': [
                                                            '$$value', [
                                                                {
                                                                    'k': '$$this.k', 
                                                                    'v': {
                                                                        '$cond': [
                                                                            {
                                                                                '$eq': [
                                                                                    {
                                                                                        '$size': '$$data'
                                                                                    }, 0
                                                                                ]
                                                                            }, None, {
                                                                                '$arrayToObject': {
                                                                                    '$reduce': {
                                                                                        'input': '$$data', 
                                                                                        'initialValue': [], 
                                                                                        'in': {
                                                                                            '$cond': [
                                                                                                {
                                                                                                    '$eq': [
                                                                                                        {
                                                                                                            '$size': '$$value'
                                                                                                        }, 0
                                                                                                    ]
                                                                                                }, {
                                                                                                    '$filter': {
                                                                                                        'input': {
                                                                                                            '$objectToArray': '$$this'
                                                                                                        }, 
                                                                                                        'as': 'f', 
                                                                                                        'cond': {
                                                                                                            '$not': {
                                                                                                                '$in': [
                                                                                                                    '$$f.k', [
                                                                                                                        'date', 'adGroupId'
                                                                                                                    ]
                                                                                                                ]
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }, {
                                                                                                    '$map': {
                                                                                                        'input': '$$value', 
                                                                                                        'as': 'm', 
                                                                                                        'in': {
                                                                                                            '$mergeObjects': [
                                                                                                                '$$m', {
                                                                                                                    'v': {
                                                                                                                        '$sum': [
                                                                                                                            '$$m.v', {
                                                                                                                                '$getField': {
                                                                                                                                    'input': '$$this', 
                                                                                                                                    'field': '$$m.k'
                                                                                                                                }
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }
                                                                                                            ]
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            ]
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            ]
                                                        ]
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }, {
                    '$replaceRoot': {
                        'newRoot': {
                            '$mergeObjects': [
                                '$$ROOT', {
                                    '$arrayToObject': {
                                        '$reduce': {
                                            'input': {
                                                '$objectToArray': '$$ROOT'
                                            }, 
                                            'initialValue': [], 
                                            'in': {
                                                '$concatArrays': [
                                                    '$$value', [
                                                        {
                                                            '$cond': [
                                                                {
                                                                    '$ne': [
                                                                        {
                                                                            '$type': '$$this.v'
                                                                        }, 'object'
                                                                    ]
                                                                }, '$$this', {
                                                                    'k': '$$this.k', 
                                                                    'v': {
                                                                        '$arrayToObject': {
                                                                            '$reduce': {
                                                                                'input': {
                                                                                    '$objectToArray': '$$this.v'
                                                                                }, 
                                                                                'initialValue': [], 
                                                                                'in': {
                                                                                    '$concatArrays': [
                                                                                        '$$value', [
                                                                                            {
                                                                                                'k': '$$this.k', 
                                                                                                'v': {
                                                                                                    '$round': [
                                                                                                        '$$this.v', 0
                                                                                                    ]
                                                                                                }
                                                                                            }
                                                                                        ]
                                                                                    ]
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                ]
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }, {
                    '$set': {
                        'performance': {
                            '$arrayToObject': {
                                '$reduce': {
                                    'input': [
                                        'sales', 'cost'
                                    ], 
                                    'initialValue': [], 
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                {
                                                    'k': '$$this', 
                                                    'v': {
                                                        '$let': {
                                                            'vars': {
                                                                'curr': {
                                                                    '$getField': {
                                                                        'input': '$last30Days', 
                                                                        'field': '$$this'
                                                                    }
                                                                }, 
                                                                'pre': {
                                                                    '$getField': {
                                                                        'input': '$prev30Days', 
                                                                        'field': '$$this'
                                                                    }
                                                                }
                                                            }, 
                                                            'in': {
                                                                'curr': {
                                                                    '$ifNull': [
                                                                        '$$curr', 0
                                                                    ]
                                                                }, 
                                                                'pre': {
                                                                    '$ifNull': [
                                                                        '$$pre', 0
                                                                    ]
                                                                }, 
                                                                'growth': {
                                                                    '$cond': [
                                                                        {
                                                                            '$or': [
                                                                                {
                                                                                    '$eq': [
                                                                                        {
                                                                                            '$ifNull': [
                                                                                                '$$pre', None
                                                                                            ]
                                                                                        }, None
                                                                                    ]
                                                                                }, {
                                                                                    '$eq': [
                                                                                        {
                                                                                            '$ifNull': [
                                                                                                '$$curr', None
                                                                                            ]
                                                                                        }, None
                                                                                    ]
                                                                                }, {
                                                                                    '$eq': [
                                                                                        '$$pre', 0
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }, None, {
                                                                            '$divide': [
                                                                                {
                                                                                    '$subtract': [
                                                                                        '$$curr', '$$pre'
                                                                                    ]
                                                                                }, '$$pre'
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }, {
                    '$set': {
                        'performance.roas': {
                            'curr': {
                                '$cond': [
                                    {
                                        '$or': [
                                            {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.sales.curr', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.cost.curr', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$performance.cost.curr', 0
                                                ]
                                            }
                                        ]
                                    }, 0, {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$performance.sales.curr', '$performance.cost.curr'
                                                ]
                                            }, 1
                                        ]
                                    }
                                ]
                            }, 
                            'pre': {
                                '$cond': [
                                    {
                                        '$or': [
                                            {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.sales.pre', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.cost.pre', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$performance.cost.pre', 0
                                                ]
                                            }
                                        ]
                                    }, 0, {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$performance.sales.pre', '$performance.cost.pre'
                                                ]
                                            }, 1
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }, {
                    '$set': {
                        'performance.roas.growth': {
                            '$cond': [
                                {
                                    '$eq': [
                                        '$performance.roas.pre', 0
                                    ]
                                }, None, {
                                    '$divide': [
                                        {
                                            '$subtract': [
                                                '$performance.roas.curr', '$performance.roas.pre'
                                            ]
                                        }, '$performance.roas.pre'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'last30Days': 0, 
                        'prev30Days': 0
                    }
                }, {
                    '$group': {
                        '_id': None, 
                        'data': {
                            '$push': '$$ROOT'
                        }
                    }
                }, {
                    '$set': {
                        'performance': {
                            '$reduce': {
                                'input': '$data', 
                                'initialValue': {
                                    'sales': {
                                        'curr': 0, 
                                        'pre': 0
                                    }, 
                                    'cost': {
                                        'curr': 0, 
                                        'pre': 0
                                    }
                                }, 
                                'in': {
                                    '$arrayToObject': {
                                        '$let': {
                                            'vars': {
                                                'curr': '$$this.performance'
                                            }, 
                                            'in': {
                                                '$reduce': {
                                                    'input': {
                                                        '$objectToArray': '$$value'
                                                    }, 
                                                    'initialValue': [], 
                                                    'in': {
                                                        '$concatArrays': [
                                                            '$$value', [
                                                                {
                                                                    'k': '$$this.k', 
                                                                    'v': {
                                                                        '$let': {
                                                                            'vars': {
                                                                                'c': {
                                                                                    '$getField': {
                                                                                        'input': {
                                                                                            '$getField': {
                                                                                                'input': '$$curr', 
                                                                                                'field': '$$this.k'
                                                                                            }
                                                                                        }, 
                                                                                        'field': 'curr'
                                                                                    }
                                                                                }, 
                                                                                'p': {
                                                                                    '$getField': {
                                                                                        'input': {
                                                                                            '$getField': {
                                                                                                'input': '$$curr', 
                                                                                                'field': '$$this.k'
                                                                                            }
                                                                                        }, 
                                                                                        'field': 'pre'
                                                                                    }
                                                                                }
                                                                            }, 
                                                                            'in': {
                                                                                'curr': {
                                                                                    '$sum': [
                                                                                        '$$this.v.curr', '$$c'
                                                                                    ]
                                                                                }, 
                                                                                'pre': {
                                                                                    '$sum': [
                                                                                        '$$this.v.pre', '$$p'
                                                                                    ]
                                                                                }, 
                                                                                'growth': {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$or': [
                                                                                                {
                                                                                                    '$eq': [
                                                                                                        {
                                                                                                            '$ifNull': [
                                                                                                                '$$p', None
                                                                                                            ]
                                                                                                        }, None
                                                                                                    ]
                                                                                                }, {
                                                                                                    '$eq': [
                                                                                                        {
                                                                                                            '$ifNull': [
                                                                                                                '$$p', None
                                                                                                            ]
                                                                                                        }, None
                                                                                                    ]
                                                                                                }, {
                                                                                                    '$eq': [
                                                                                                        '$$p', 0
                                                                                                    ]
                                                                                                }
                                                                                            ]
                                                                                        }, None, {
                                                                                            '$divide': [
                                                                                                {
                                                                                                    '$subtract': [
                                                                                                        '$$c', '$$p'
                                                                                                    ]
                                                                                                }, '$$p'
                                                                                            ]
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            ]
                                                        ]
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }, {
                    '$set': {
                        'performance.roas': {
                            'curr': {
                                '$cond': [
                                    {
                                        '$or': [
                                            {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.sales.curr', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.cost.curr', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$performance.cost.curr', 0
                                                ]
                                            }
                                        ]
                                    }, 0, {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$performance.sales.curr', '$performance.cost.curr'
                                                ]
                                            }, 1
                                        ]
                                    }
                                ]
                            }, 
                            'pre': {
                                '$cond': [
                                    {
                                        '$or': [
                                            {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.sales.pre', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    {
                                                        '$ifNull': [
                                                            '$performance.cost.pre', None
                                                        ]
                                                    }, None
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$performance.cost.pre', 0
                                                ]
                                            }
                                        ]
                                    }, 0, {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$performance.sales.pre', '$performance.cost.pre'
                                                ]
                                            }, 1
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }, {
                    '$set': {
                        'performance.roas.growth': {
                            '$cond': [
                                {
                                    '$eq': [
                                        '$performance.roas.pre', 0
                                    ]
                                }, None, {
                                    '$divide': [
                                        {
                                            '$subtract': [
                                                '$performance.roas.curr', '$performance.roas.pre'
                                            ]
                                        }, '$performance.roas.pre'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0
                    }
                }
            ], 
            'as': 'result'
        }
    }, {
        '$set': {
            'performance': {
                '$first': '$result.performance'
            }, 
            'result': {
                '$first': '$result.data'
            }
        }
    }, {
        '$sort': {
            'performance.cost.curr': -1
        }
    }, {
        '$skip': paginator.skip
    }, {
        '$limit': paginator.limit
    }, {
        '$lookup': {
            'from': 'products', 
            'let': {
                'asins': '$_id.asins', 
                'marketplace': '$_id.marketplace'
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
                                        '$asin', '$$asins'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'asin': 1, 
                        'imageUrl': 1, 
                        'variationTheme': 1, 
                        'fulfillment': 1
                    }
                }
            ], 
            'as': 'products'
        }
    }, {
        '$lookup': {
            'from': 'adv_ad_group_mapping', 
            'let': {
                'marketplace': '$_id.marketplace', 
                'adGroupIds': {
                    '$reduce': {
                        'input': '$data', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', [
                                    '$$this.adGroupId'
                                ]
                            ]
                        }
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
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$in': [
                                        '$adGroupId', '$$adGroupIds'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'marketplace': 0
                    }
                }
            ], 
            'as': 'mapping'
        }
    }, {
        '$set': {
            'data': {
                '$map': {
                    'input': '$data', 
                    'as': 'd', 
                    'in': {
                        '$mergeObjects': [
                            '$$d', {
                                '$first': {
                                    '$filter': {
                                        'input': '$result', 
                                        'as': 'f', 
                                        'cond': {
                                            '$eq': [
                                                '$$f.adGroupId', '$$d.adGroupId'
                                            ]
                                        }
                                    }
                                }
                            }, {
                                'options': {
                                    '$mergeObjects': [
                                        '$$d.options', {
                                            '$first': {
                                                '$filter': {
                                                    'input': '$mapping', 
                                                    'as': 'f', 
                                                    'cond': {
                                                        '$eq': [
                                                            '$$f.adGroupId', '$$d.adGroupId'
                                                        ]
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }, 
            'count': {
                '$reduce': {
                    'input': '$data', 
                    'initialValue': 0, 
                    'in': {
                        '$sum': [
                            '$$value', '$$this.count'
                        ]
                    }
                }
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'targets': 0, 
            'mapping': 0, 
            'result': 0
        }
    }
]