from dzgroshared.db.model import PyObjectId


def pipeline(marketplace: PyObjectId, revenueMonth: float, orderMonth: int, revenueYear: float, orderYear: int) -> list[dict]:
    return [
    {
        '$match': {
            '_id': marketplace
        }
    }, {
        '$set': {
            'orderMonth': orderMonth, 
            'revenueMonth': revenueMonth, 
            'orderYear': orderYear, 
            'revenueYear': revenueYear
        }
    }, {
        '$lookup': {
            'from': 'pricing', 
            'let': {
                'countryCode': {
                    '$cond': {
                        'if': {
                            '$eq': [
                                '$countrycode', 'IN'
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
                        'plans': '$plans'
                    }
                }
            ], 
            'as': 'active_plan'
        }
    }, {
        '$lookup': {
            'from': 'marketplace_plans', 
            'localField': '_id', 
            'foreignField': 'marketplace', 
            'pipeline': [
                {
                    '$lookup': {
                        'from': 'pricing', 
                        'localField': 'pricing', 
                        'foreignField': '_id', 
                        'pipeline': [
                            {
                                '$project': {
                                    'plans': '$plans', 
                                    '_id': 0
                                }
                            }
                        ], 
                        'as': 'plans'
                    }
                }, {
                    '$set': {
                        'plans': {
                            '$first': '$plans.plans'
                        }
                    }
                }, {
                    '$project': {
                        'marketplace': 0
                    }
                }
            ], 
            'as': 'current_plan'
        }
    }, {
        '$set': {
            'active_plan': {
                '$first': '$active_plan'
            }, 
            'current_plan': {
                '$first': '$current_plan'
            }
        }
    }, {
        '$set': {
            'plan': {
                '$unsetField': {
                    'input': '$current_plan', 
                    'field': 'plans'
                }
            }, 
            'plans': {
                '$ifNull': [
                    '$current_plan.plans', '$active_plan.plans'
                ]
            }, 
            'pricingid': {
                '$ifNull': [
                    '$current_plan._id', '$active_plan._id'
                ]
            }
        }
    }, {
        '$project': {
            '_id': 1, 
            'uid': 1, 
            'storename': 1, 
            'countrycode': 1, 
            'marketplaceid': 1, 
            'plan': 1, 
            'plans': 1, 
            'pricingid': 1, 
            'orderMonth': 1, 
            'revenueMonth': 1, 
            'orderYear': 1, 
            'revenueYear': 1, 
            'gstin': 1
        }
    }, {
        '$lookup': {
            'from': 'country_details', 
            'localField': 'countrycode', 
            'foreignField': '_id', 
            'pipeline': [
                {
                    '$set': {
                        'countryCode': '$_id', 
                        'currency': {
                            '$cond': {
                                'if': {
                                    '$eq': [
                                        '$_id', 'IN'
                                    ]
                                }, 
                                'then': '\u20b9', 
                                'else': {
                                    '$literal': '$'
                                }
                            }
                        }
                    }
                }, {
                    '$project': {
                        'currencyCode': 1, 
                        'countryCode': 1, 
                        'currency': 1, 
                        'country': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'country'
        }
    }, {
        '$replaceWith': {
            '$mergeObjects': [
                '$$ROOT', {
                    '$first': '$country'
                }
            ]
        }
    }, {
        '$set': {
            'details': {
                '$reduce': {
                    'input': '$plans', 
                    'initialValue': [], 
                    'in': {
                        '$concatArrays': [
                            '$$value', {
                                '$let': {
                                    'vars': {
                                        'name': '$$this.name'
                                    }, 
                                    'in': {
                                        '$reduce': {
                                            'input': '$$this.durations', 
                                            'initialValue': [], 
                                            'in': {
                                                '$concatArrays': [
                                                    '$$value', [
                                                        {
                                                            '$mergeObjects': [
                                                                {
                                                                    'name': '$$name', 
                                                                    'duration': '$$this.duration'
                                                                }, {
                                                                    '$let': {
                                                                        'vars': {
                                                                            'value': {
                                                                                '$cond': {
                                                                                    'if': {
                                                                                        '$eq': [
                                                                                            '$$this.variableType', 'Orders'
                                                                                        ]
                                                                                    }, 
                                                                                    'then': {
                                                                                        '$cond': {
                                                                                            'if': {
                                                                                                '$eq': [
                                                                                                    '$$this.duration', 'Month'
                                                                                                ]
                                                                                            }, 
                                                                                            'then': '$orderMonth', 
                                                                                            'else': '$orderYear'
                                                                                        }
                                                                                    }, 
                                                                                    'else': {
                                                                                        '$cond': {
                                                                                            'if': {
                                                                                                '$eq': [
                                                                                                    '$$this.duration', 'Month'
                                                                                                ]
                                                                                            }, 
                                                                                            'then': '$revenueMonth', 
                                                                                            'else': '$revenueYear'
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }, 
                                                                        'in': {
                                                                            '$let': {
                                                                                'vars': {
                                                                                    'variableLabel': {
                                                                                        '$cond': {
                                                                                            'if': {
                                                                                                '$eq': [
                                                                                                    '$$this.variableType', 'Orders'
                                                                                                ]
                                                                                            }, 
                                                                                            'then': {
                                                                                                '$concat': [
                                                                                                    '$currency', {
                                                                                                        '$toString': '$$this.variable'
                                                                                                    }, ' per ', {
                                                                                                        '$toString': '$$this.variableUnit'
                                                                                                    }, ' ', '$$this.variableType'
                                                                                                ]
                                                                                            }, 
                                                                                            'else': {
                                                                                                '$concat': [
                                                                                                    {
                                                                                                        '$toString': '$$this.variable'
                                                                                                    }, '% of ', '$$this.variableType'
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    }, 
                                                                                    'variableValue': {
                                                                                        '$round': [
                                                                                            {
                                                                                                '$cond': {
                                                                                                    'if': {
                                                                                                        '$eq': [
                                                                                                            '$$this.variableType', 'Orders'
                                                                                                        ]
                                                                                                    }, 
                                                                                                    'then': {
                                                                                                        '$multiply': [
                                                                                                            '$$this.variable', {
                                                                                                                '$divide': [
                                                                                                                    '$$value', '$$this.variableUnit'
                                                                                                                ]
                                                                                                            }
                                                                                                        ]
                                                                                                    }, 
                                                                                                    'else': {
                                                                                                        '$multiply': {
                                                                                                            '$divide': [
                                                                                                                {
                                                                                                                    '$multiply': [
                                                                                                                        '$$value', '$$this.variable'
                                                                                                                    ]
                                                                                                                }, 100
                                                                                                            ]
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }, 1
                                                                                        ]
                                                                                    }
                                                                                }, 
                                                                                'in': {
                                                                                    '$let': {
                                                                                        'vars': {
                                                                                            'total': {
                                                                                                '$sum': [
                                                                                                    '$$this.price', '$$variableValue'
                                                                                                ]
                                                                                            }
                                                                                        }, 
                                                                                        'in': {
                                                                                            '$let': {
                                                                                                'vars': {
                                                                                                    'gst': {
                                                                                                        '$round': [
                                                                                                            {
                                                                                                                '$multiply': [
                                                                                                                    '$$total', 0.18
                                                                                                                ]
                                                                                                            }, 2
                                                                                                        ]
                                                                                                    }
                                                                                                }, 
                                                                                                'in': {
                                                                                                    '$let': {
                                                                                                        'vars': {
                                                                                                            'payable': {
                                                                                                                '$round': [
                                                                                                                    {
                                                                                                                        '$sum': [
                                                                                                                            '$$total', '$$gst'
                                                                                                                        ]
                                                                                                                    }, 2
                                                                                                                ]
                                                                                                            }
                                                                                                        }, 
                                                                                                        'in': {
                                                                                                            'total': '$$payable',
                                                                                                            'groups': [
                                                                                                                {
                                                                                                                    'label': 'A. Base Price', 
                                                                                                                    'value': {
                                                                                                                        '$concat': [
                                                                                                                            '$currency', {
                                                                                                                                '$toString': '$$this.price'
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }, {
                                                                                                                    'label': {
                                                                                                                        '$concat': [
                                                                                                                            'B. ', '$$this.variableType'
                                                                                                                        ]
                                                                                                                    }, 
                                                                                                                    'sublabel': {
                                                                                                                        '$cond': {
                                                                                                                            'if': {
                                                                                                                                '$eq': [
                                                                                                                                    '$$this.duration', 'Month'
                                                                                                                                ]
                                                                                                                            }, 
                                                                                                                            'then': 'Last 30 Days', 
                                                                                                                            'else': 'Last 1 Year'
                                                                                                                        }
                                                                                                                    }, 
                                                                                                                    'value': {
                                                                                                                        '$concat': [
                                                                                                                            {
                                                                                                                                '$cond': {
                                                                                                                                    'if': {
                                                                                                                                        '$eq': [
                                                                                                                                            '$$this.variableType', 'Orders'
                                                                                                                                        ]
                                                                                                                                    }, 
                                                                                                                                    'then': '', 
                                                                                                                                    'else': '$currency'
                                                                                                                                }
                                                                                                                            }, {
                                                                                                                                '$toString': '$$value'
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }, {
                                                                                                                    'label': 'C. Variable Price', 
                                                                                                                    'sublabel': '$variableLabel', 
                                                                                                                    'value': {
                                                                                                                        '$concat': [
                                                                                                                            '$currency', {
                                                                                                                                '$toString': '$$variableValue'
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }, {
                                                                                                                    'label': 'D. Gross Total', 
                                                                                                                    'sublabel': 'Base Price + Variable', 
                                                                                                                    'value': {
                                                                                                                        '$concat': [
                                                                                                                            '$currency', {
                                                                                                                                '$toString': '$$total'
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }, {
                                                                                                                    'label': 'E. GST', 
                                                                                                                    'sublabel': 'Applicable Taxes', 
                                                                                                                    'value': {
                                                                                                                        '$concat': [
                                                                                                                            '$currency', {
                                                                                                                                '$toString': '$$gst'
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }, {
                                                                                                                    'label': 'F. Net Payable', 
                                                                                                                    'value': {
                                                                                                                        '$concat': [
                                                                                                                            '$currency', {
                                                                                                                                '$toString': '$$payable'
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }
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
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$project': {
            'value': 0, 
            'plan._id': 0, 
            'revenueMonth': 0, 
            'orderMonth': 0, 
            'orderYear': 0, 
            'revenueYear': 0
        }
    }, {
        '$lookup': {
            'from': 'gstin', 
            'localField': 'uid', 
            'foreignField': 'uid', 
            'as': 'gstins'
        }
    }
]