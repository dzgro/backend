from bson import ObjectId

def pipeline(uid: str, marketplace: ObjectId):
    return [
    {
        '$match': {
            'uid': '41e34d1a-6031-70d2-9ff3-d1a704240921', 
            'marketplace': ObjectId('6868c2eeab11a9bc9236a3df'), 
            'assettype': 'Target', 
            'negative': False
        }
    }, {
        '$group': {
            '_id': '$parent', 
            'targets': {
                '$push': {
                    'targetid': '$id', 
                    'targettype': '$targettype', 
                    'targetdetails': '$targetdetails'
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'adv_assets', 
            'let': {
                'adgroupid': '$_id'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$uid', '41e34d1a-6031-70d2-9ff3-d1a704240921'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', ObjectId('6868c2eeab11a9bc9236a3df')
                                    ]
                                }, {
                                    '$eq': [
                                        '$assettype', 'Ad'
                                    ]
                                }, {
                                    '$eq': [
                                        '$parent', '$$adgroupid'
                                    ]
                                }, {
                                    '$eq': [
                                        '$state', 'ENABLED'
                                    ]
                                }, {
                                    '$eq': [
                                        '$deliverystatus', 'DELIVERING'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$unwind': '$creative.products'
                }, {
                    '$match': {
                        'creative.products.productIdType': 'ASIN'
                    }
                }, {
                    '$group': {
                        '_id': '$parent', 
                        'ads': {
                            '$push': {
                                'adid': '$id', 
                                'asin': '$creative.products.productId'
                            }
                        }
                    }
                }
            ], 
            'as': 'adsInfo'
        }
    }, {
        '$lookup': {
            'from': 'adv_assets', 
            'let': {
                'adgroupid': '$_id'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$id', '$$adgroupid'
                                    ]
                                }, {
                                    '$eq': [
                                        '$assettype', 'Ad Group'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'name': 1, 
                        'campaignid': 1, 
                        'campaignName': 1
                    }
                }
            ], 
            'as': 'adgroupInfo'
        }
    }, {
        '$unwind': {
            'path': '$adgroupInfo', 
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$addFields': {
            'targetKeys': {
                '$map': {
                    'input': '$targets', 
                    'as': 't', 
                    'in': {
                        '$cond': [
                            {
                                '$ifNull': [
                                    '$$t.targetdetails.asin', False
                                ]
                            }, {
                                '$concat': [
                                    'asin:', {
                                        '$toString': '$$t.targetdetails.asin'
                                    }, '|mt:', {
                                        '$toString': '$$t.targetdetails.matchType'
                                    }
                                ]
                            }, {
                                '$cond': [
                                    {
                                        '$ifNull': [
                                            '$$t.targetdetails.keyword', False
                                        ]
                                    }, {
                                        '$concat': [
                                            'kw:', {
                                                '$toString': '$$t.targetdetails.keyword'
                                            }, '|mt:', {
                                                '$toString': '$$t.targetdetails.matchType'
                                            }
                                        ]
                                    }, {
                                        '$cond': [
                                            {
                                                '$ifNull': [
                                                    '$$t.targetdetails.productCategoryId', False
                                                ]
                                            }, {
                                                '$concat': [
                                                    'cat:', {
                                                        '$toString': '$$t.targetdetails.productCategoryId'
                                                    }, '|mt:', {
                                                        '$toString': '$$t.targetdetails.matchType'
                                                    }
                                                ]
                                            }, {
                                                '$toString': '$$t.targetdetails.matchType'
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$addFields': {
            'hasDuplicateTargets': {
                '$gt': [
                    {
                        '$size': '$targetKeys'
                    }, {
                        '$size': {
                            '$setUnion': '$targetKeys'
                        }
                    }
                ]
            }
        }
    }, {
        '$match': {
            'hasDuplicateTargets': True
        }
    }, {
        '$project': {
            'adgroupid': '$_id', 
            'adgroupName': '$adgroupInfo.name', 
            'campaignid': '$adgroupInfo.campaignid', 
            'campaignName': '$adgroupInfo.campaignName', 
            'ads': {
                '$arrayElemAt': [
                    '$adsInfo.ads', 0
                ]
            }, 
            'targets': 1, 
            'hasDuplicateTargets': 1
        }
    }, {
        '$merge': {
            'into': 'test'
        }
    }
]