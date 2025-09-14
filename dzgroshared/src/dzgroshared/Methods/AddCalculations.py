def execute(currPreGrowth: bool, objectKey:str):
    return {
        '$set': {
            objectKey: {
                '$reduce': {
                    'input': {
                        "$filter": {
                        "input":"$keys",
                        "as": "k",
                        "cond": {"$ne": [{"$ifNull": ["$$k.subkeys", None]},None]}
                        }
                    }, 
                    'initialValue': f'${objectKey}', 
                    'in': {
                        '$mergeObjects': [
                            '$$value', {
                                '$let': {
                                    'vars': {
                                        'key': '$$this', 
                                        'val': '$$value', 
                                        'num': {
                                            '$getField': {
                                                'input': '$$value', 
                                                'field': {
                                                    '$arrayElemAt': [
                                                        '$$this.subkeys', 0
                                                    ]
                                                }
                                            }
                                        }, 
                                        'denom': {
                                            '$getField': {
                                                'input': '$$value', 
                                                'field': {
                                                    '$arrayElemAt': [
                                                        '$$this.subkeys', 1
                                                    ]
                                                }
                                            }
                                        }
                                    }, 
                                    'in': {
                                        '$cond': [
                                            {
                                                '$and': [
                                                    {
                                                        '$ne': [
                                                            {
                                                                '$ifNull': [
                                                                    '$$num', None
                                                                ]
                                                            }, None
                                                        ]
                                                    }, {
                                                        '$ne': [
                                                            {
                                                                '$ifNull': [
                                                                    '$$denom', None
                                                                ]
                                                            }, None
                                                        ]
                                                    }
                                                ]
                                            }, currPre() if currPreGrowth else notCurrPre(), {}
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

def notCurrPre():
    return {
        '$arrayToObject': [
            [
                {
                    'k': '$$key.key', 
                    'v': {
                                                        '$let': {
                                                            'vars': {
                                                                'isPercent': '$$key.isPercent', 
                                                                'isDivide': {
                                                                    '$eq': [
                                                                        '$$key.operation', 'divide'
                                                                    ]
                                                                }, 
                                                                'isAdd': {
                                                                    '$eq': [
                                                                        '$$key.operation', 'add'
                                                                    ]
                                                                }, 
                                                                'isSubtract': {
                                                                    '$eq': [
                                                                        '$$key.operation', 'subtract'
                                                                    ]
                                                                }
                                                            }, 
                                                            'in': {
                                                                '$cond': [
                                                                    '$$isAdd', {
                                                                        '$sum': [
                                                                            '$$num', '$$denom'
                                                                        ]
                                                                    }, {
                                                                        '$cond': [
                                                                            '$$isSubtract', {
                                                                                '$subtract': [
                                                                                    '$$num', '$$denom'
                                                                                ]
                                                                            }, {
                                                                                '$cond': [
                                                                                    {
                                                                                        '$eq': [
                                                                                            '$$denom', 0
                                                                                        ]
                                                                                    }, 0, {
                                                                                        '$multiply': [
                                                                                            {
                                                                                                '$divide': [
                                                                                                    '$$num', '$$denom'
                                                                                                ]
                                                                                            }, {
                                                                                                '$cond': [
                                                                                                    '$$isPercent', 100, 1
                                                                                                ]
                                                                                            }
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
                }
            ]
        ]
    }


def currPre():
    return {
        '$let': {
            'vars': {
                'curr': {
                    'num': {
                        '$getField': {
                            'input': '$$num', 
                            'field': 'curr'
                        }
                    }, 
                    'denom': {
                        '$getField': {
                            'input': '$$denom', 
                            'field': 'curr'
                        }
                    }
                }, 
                'pre': {
                    'num': {
                        '$getField': {
                            'input': '$$num', 
                            'field': 'pre'
                        }
                    }, 
                    'denom': {
                        '$getField': {
                            'input': '$$denom', 
                            'field': 'pre'
                        }
                    }
                }
            }, 
            'in': {
                '$let': {
                    'vars': {
                        'curr': {
                            'num': {
                                '$ifNull': [
                                    '$$curr.num', 0
                                ]
                            }, 
                            'denom': {
                                '$ifNull': [
                                    '$$curr.denom', 0
                                ]
                            }
                        }, 
                        'pre': {
                            'num': {
                                '$ifNull': [
                                    '$$pre.num', 0
                                ]
                            }, 
                            'denom': {
                                '$ifNull': [
                                    '$$pre.denom', 0
                                ]
                            }
                        }
                    }, 
                    'in': {
                        '$arrayToObject': [
                            [
                                {
                                    'k': '$$key.key', 
                                    'v': {
                                        '$reduce': {
                                            'input': [
                                                'curr', 'pre'
                                            ], 
                                            'initialValue': {}, 
                                            'in': {
                                                '$mergeObjects': [
                                                    '$$value', {
                                                        '$arrayToObject': [
                                                            [
                                                                {
                                                                    'k': '$$this', 
                                                                    'v': {
                                                                        '$let': {
                                                                            'vars': {
                                                                                'num': {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$eq': [
                                                                                                '$$this', 'curr'
                                                                                            ]
                                                                                        }, '$$curr.num', '$$pre.num'
                                                                                    ]
                                                                                }, 
                                                                                'denom': {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$eq': [
                                                                                                '$$this', 'curr'
                                                                                            ]
                                                                                        }, '$$curr.denom', '$$pre.denom'
                                                                                    ]
                                                                                }, 
                                                                                'isPercent': '$$key.isPercent', 
                                                                                'isDivide': {
                                                                                    '$eq': [
                                                                                        '$$key.operation', 'divide'
                                                                                    ]
                                                                                }, 
                                                                                'isAdd': {
                                                                                    '$eq': [
                                                                                        '$$key.operation', 'add'
                                                                                    ]
                                                                                }, 
                                                                                'isSubtract': {
                                                                                    '$eq': [
                                                                                        '$$key.operation', 'subtract'
                                                                                    ]
                                                                                }
                                                                            }, 
                                                                            'in': {
                                                                                '$cond': [
                                                                                    '$$isAdd', {
                                                                                        '$sum': [
                                                                                            '$$num', '$$denom'
                                                                                        ]
                                                                                    }, {
                                                                                        '$cond': [
                                                                                            '$$isSubtract', {
                                                                                                '$subtract': [
                                                                                                    '$$num', '$$denom'
                                                                                                ]
                                                                                            }, {
                                                                                                '$cond': [
                                                                                                    {
                                                                                                        '$eq': [
                                                                                                            '$$denom', 0
                                                                                                        ]
                                                                                                    }, 0, {
                                                                                                        '$multiply': [
                                                                                                            {
                                                                                                                '$divide': [
                                                                                                                    '$$num', '$$denom'
                                                                                                                ]
                                                                                                            }, {
                                                                                                                '$cond': [
                                                                                                                    '$$isPercent', 100, 1
                                                                                                                ]
                                                                                                            }
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
                                                                }
                                                            ]
                                                        ]
                                                    }
                                                ]
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