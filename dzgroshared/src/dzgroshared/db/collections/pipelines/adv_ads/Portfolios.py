from bson import ObjectId


def pipeline(uid: str, marketplace: ObjectId) -> list[dict]:
    return [
    {
        '$match': {
            'uid': uid, 
            'marketplace': marketplace, 
            'assettype': 'Campaign'
        }
    },
    {
        '$lookup': {
            'from': 'adv_assets', 
            'let': {
                'uid': '$uid', 
                'marketplace': '$marketplace', 
                'assettype': 'Ad Group', 
                'parent': '$id'
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
                                        '$assettype', '$$assettype'
                                    ]
                                }, {
                                    '$eq': [
                                        '$parent', '$$parent'
                                    ]
                                }, {
                                    '$eq': [
                                        '$state', 'ENABLED'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'id': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'adgroupid'
        }
    }, {
        '$set': {
            'adgroupid': {
                '$reduce': {
                    'input': '$adgroupid', 
                    'initialValue': [], 
                    'in': {
                        '$concatArrays': [
                            '$$value', [
                                '$$this.id'
                            ]
                        ]
                    }
                }
            }
        }
    }, {
        '$unwind': {
            'path': '$adgroupid', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$lookup': {
            'from': 'adv_assets', 
            'let': {
                'uid': '$uid', 
                'marketplace': '$marketplace', 
                'assettype': 'Ad', 
                'parent': '$adgroupid'
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
                                        '$assettype', '$$assettype'
                                    ]
                                }, {
                                    '$eq': [
                                        '$parent', '$$parent'
                                    ]
                                }, {
                                    '$eq': [
                                        '$state', 'ENABLED'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'asin': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'asin'
        }
    }, {
        '$set': {
            'asin': {
                '$reduce': {
                    'input': '$asin', 
                    'initialValue': [], 
                    'in': {
                        '$concatArrays': [
                            '$$value', {
                                '$cond': {
                                    'if': {
                                        '$eq': [
                                            {
                                                '$ifNull': [
                                                    '$$this.asin', None
                                                ]
                                            }, None
                                        ]
                                    }, 
                                    'then': [], 
                                    'else': [
                                        '$$this.asin'
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$unwind': {
            'path': '$asin', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$lookup': {
            'from': 'products', 
            'let': {
                'uid': '$uid', 
                'marketplace': '$marketplace', 
                'asin': '$asin'
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
                                        '$asin', '$$asin'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$set': {
                        'image': {
                            '$first': '$images'
                        }
                    }
                }, {
                    '$project': {
                        'asin': 1, 
                        'image': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'product'
        }
    }, {
        '$unwind': {
            'path': '$product'
        }
    }, {
        '$group': {
            '_id': '$parent', 
            'products': {
                '$push': '$product'
            }, 
            'id': {
                '$push': {
                    '$concat': [
                        {
                            '$toString': '$marketplace'
                        }, '_', '$parent'
                    ]
                }
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$match': {
            '_id': {
                '$ne': None
            }
        }
    }, {
        '$set': {
            'products': {
                '$slice': [
                    '$products', 10
                ]
            }
        }
    }, {
        '$project': {
            '_id': {
                '$first': '$id'
            }, 
            'products': 1, 
            'count': 1
        }
    }, {
        '$merge': {
            'into': 'adv_ads'
        }
    }
]