from dzgroshared.models.model import PyObjectId

def pipeline(marketplace: PyObjectId):
    return [
    {
        '$match': {
            'marketplace': marketplace, 
            'state': 'ENABLED', 
            'adproduct': 'SPONSORED_PRODUCTS',
            'deliverystatus': "DELIVERING"
        }
    }, {
        '$facet': {
            'rule1': [
                {
                    '$match': {
                        'assettype': 'Ad'
                    }
                }, {
                    '$unwind': '$creative.products'
                }, {
                    '$match': {
                        'creative.products.productIdType': 'ASIN'
                    }
                }, {
                    '$group': {
                        '_id': '$adgroupid', 
                        'asins': {
                            '$addToSet': '$creative.products.productId'
                        }
                    }
                }, {
                    '$project': {
                        'passed': {
                            '$cond': [
                                {
                                    '$eq': [
                                        {
                                            '$size': '$asins'
                                        }, 1
                                    ]
                                }, 1, 0
                            ]
                        }
                    }
                }
            ],
            'rule2': [
                {
                    '$match': {
                        'assettype': 'Target', 
                        'negative': False
                    }
                }, {
                    '$group': {
                        '_id': '$adgroupid', 
                        'matchTypes': {
                            '$addToSet': '$targetdetails.matchType'
                        }
                    }
                }, {
                    '$project': {
                        'matchTypes': '$matchTypes', 
                        'passed': {
                            '$cond': [
                                {
                                    '$eq': [
                                        {
                                            '$size': '$matchTypes'
                                        }, 1
                                    ]
                                }, 1, 0
                            ]
                        }
                    }
                }
            ], 
            
            'rule3': [
                {
                    '$match': {
                        'assettype': 'Target', 
                        'negative': False
                    }
                }, {
                    '$group': {
                        '_id': '$adgroupid', 
                        'count': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$project': {
                        'passed': {
                            '$cond': [
                                {
                                    '$lte': [
                                        '$count', 10
                                    ]
                                }, 1, 0
                            ]
                        }
                    }
                }
            ], 
            'rule4': [
                {
                    '$match': {
                        'assettype': 'Target', 
                        'negative': False
                    }
                }, {
                    '$group': {
                        '_id': '$campaignid', 
                        'adGroups': {
                            '$addToSet': '$adgroupid'
                        }
                    }
                }, {
                    '$project': {
                        'passed': {
                            '$cond': [
                                {
                                    '$eq': [
                                        {
                                            '$size': '$adGroups'
                                        }, 1
                                    ]
                                }, 1, 0
                            ]
                        }
                    }
                }
            ], 
            'rule5': [
                {
                    '$match': {
                        'assettype': 'Campaign'
                    }
                }, {
                    '$project': {
                        'passed': {
                            '$cond': [
                                {
                                    '$ifNull': [
                                        '$portfolioid', False
                                    ]
                                }, 1, 0
                            ]
                        }
                    }
                }
            ]
        }
    }, {
        '$lookup': {
            'from': 'defaults', 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$eq': [
                                '$_id', 'adv_structure_rules'
                            ]
                        }
                    }
                }
            ], 
            'as': 'ruleConfig'
        }
    }, {
        '$unwind': '$ruleConfig'
    }, {
        '$project': {
            'items': {
                '$map': {
                    'input': '$ruleConfig.rules', 
                    'as': 'ruleMeta', 
                    'in': {
                        'label': '$$ruleMeta.label', 
                        'ruleid': "$$ruleMeta.ruleId",
                        'ruleId': '$$ruleMeta.ruleId', 
                        'weight': '$$ruleMeta.weight', 
                        'assettype': '$$ruleMeta.assettype', 
                        'colorScale': '$$ruleMeta.colorScale', 
                        'description': '$$ruleMeta.description', 
                        'benefits': '$$ruleMeta.benefits', 
                        'passed': {
                            '$size': {
                                '$filter': {
                                    'input': {
                                        '$getField': {
                                            'input': '$$ROOT', 
                                            'field': '$$ruleMeta.ruleId'
                                        }
                                    }, 
                                    'as': 'r', 
                                    'cond': {
                                        '$eq': [
                                            '$$r.passed', 1
                                        ]
                                    }
                                }
                            }
                        }, 
                        'total': {
                            '$size': {
                                '$getField': {
                                    'input': '$$ROOT', 
                                    'field': '$$ruleMeta.ruleId'
                                }
                            }
                        }
                    }
                }
            }
        }
    }, {
        '$addFields': {
            'items': {
                '$map': {
                    'input': '$items', 
                    'as': 'item', 
                    'in': {
                        'label': '$$item.label', 
                        'ruleid': '$$item.ruleid', 
                        'assettype': '$$item.assettype', 
                        'description': '$$item.description', 
                        'benefits': '$$item.benefits', 
                        "remaining": {"$subtract": ["$$item.total","$$item.passed"]},
                        'value': {
                            '$cond': [
                                {
                                    '$eq': [
                                        '$$item.total', 0
                                    ]
                                }, '0', {
                                    '$toString': {
                                        '$round': [
                                            {
                                                '$multiply': [
                                                    {
                                                        '$divide': [
                                                            '$$item.passed', '$$item.total'
                                                        ]
                                                    }, 100
                                                ]
                                            }, 0
                                        ]
                                    }
                                }
                            ]
                        }, 
                        'weight': '$$item.weight', 
                        'weightedScore': {
                            '$cond': [
                                {
                                    '$eq': [
                                        '$$item.total', 0
                                    ]
                                }, 0, {
                                    '$multiply': [
                                        {
                                            '$divide': [
                                                '$$item.passed', '$$item.total'
                                            ]
                                        }, {
                                            '$divide': [
                                                '$$item.weight', 30
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }, 
                        'color': {
                            '$let': {
                                'vars': {
                                    'percent': {
                                        '$multiply': [
                                            {
                                                '$divide': [
                                                    '$$item.passed', {
                                                        '$cond': [
                                                            {
                                                                '$eq': [
                                                                    '$$item.total', 0
                                                                ]
                                                            }, 1, '$$item.total'
                                                        ]
                                                    }
                                                ]
                                            }, 100
                                        ]
                                    }
                                }, 
                                'in': {
                                    '$first': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$$item.colorScale', 
                                                    'as': 'scale', 
                                                    'cond': {
                                                        '$lte': [
                                                            '$$percent', '$$scale.threshold'
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'as': 'matched', 
                                            'in': '$$matched.color'
                                        }
                                    }
                                }
                            }
                        }, 
                        'comment': {
                            '$let': {
                                'vars': {
                                    'percent': {
                                        '$multiply': [
                                            {
                                                '$divide': [
                                                    '$$item.passed', {
                                                        '$cond': [
                                                            {
                                                                '$eq': [
                                                                    '$$item.total', 0
                                                                ]
                                                            }, 1, '$$item.total'
                                                        ]
                                                    }
                                                ]
                                            }, 100
                                        ]
                                    }
                                }, 
                                'in': {
                                    '$first': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$$item.colorScale', 
                                                    'as': 'scale', 
                                                    'cond': {
                                                        '$lte': [
                                                            '$$percent', '$$scale.threshold'
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'as': 'matched', 
                                            'in': '$$matched.comment'
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
        '$addFields': {
            'score': {
                '$toString': {
                    '$round': [
                        {
                            '$multiply': [
                                {
                                    '$sum': '$items.weightedScore'
                                }, 100
                            ]
                        }, 0
                    ]
                }
            }, 
            'rawScore': {
                '$multiply': [
                    {
                        '$sum': '$items.weightedScore'
                    }, 100
                ]
            }
        }
    }, {
        '$addFields': {
            'comment': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$lte': [
                                    '$rawScore', 19.9
                                ]
                            }, 
                            'then': 'Very Poor'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 39.9
                                ]
                            }, 
                            'then': 'Poor'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 59.9
                                ]
                            }, 
                            'then': 'Average'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 79.9
                                ]
                            }, 
                            'then': 'Good'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 99.9
                                ]
                            }, 
                            'then': 'Excellent'
                        }, {
                            'case': {
                                '$eq': [
                                    '$rawScore', 100
                                ]
                            }, 
                            'then': 'Perfect'
                        }
                    ], 
                    'default': 'Unknown'
                }
            }, 
            'color': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$lte': [
                                    '$rawScore', 19.9
                                ]
                            }, 
                            'then': '#B71C1C'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 39.9
                                ]
                            }, 
                            'then': '#E53935'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 59.9
                                ]
                            }, 
                            'then': '#FB8C00'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 79.9
                                ]
                            }, 
                            'then': '#FBC02D'
                        }, {
                            'case': {
                                '$lte': [
                                    '$rawScore', 99.9
                                ]
                            }, 
                            'then': '#FFA000'
                        }, {
                            'case': {
                                '$eq': [
                                    '$rawScore', 100
                                ]
                            }, 
                            'then': '#2E7D32'
                        }
                    ], 
                    'default': '#000000'
                }
            }, 
            'score': {
                '$concat': [
                    {
                        '$toString': {
                            '$round': [
                                {
                                    '$multiply': [
                                        {
                                            '$sum': '$items.weightedScore'
                                        }, 100
                                    ]
                                }, 0
                            ]
                        }
                    }, '%'
                ]
            }, 
            'rawScore': {
                '$round': [
                    {
                        '$multiply': [
                            {
                                '$sum': '$items.weightedScore'
                            }, 100
                        ]
                    }, 0
                ]
            }
        }
    }
]