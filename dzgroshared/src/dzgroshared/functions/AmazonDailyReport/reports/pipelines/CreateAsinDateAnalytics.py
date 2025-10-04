from bson import ObjectId
from dzgroshared.db.model import StartEndDate


def pipeline(marketplace: ObjectId, dates: StartEndDate):
    setdates = dates.model_dump()
    return [
    {
        '$match': {
            '_id': marketplace,
        }
    }, {
        '$set': {
            'dates': setdates
        }
    }, {
        '$set': {
            'date': {
                '$map': {
                    'input': {
                        '$range': [
                            0, {
                                '$sum': [
                                    {
                                        '$dateDiff': {
                                            'startDate': '$dates.startdate', 
                                            'endDate': '$dates.enddate', 
                                            'unit': 'day'
                                        }
                                    }, 1
                                ]
                            }, 1
                        ]
                    }, 
                    'as': 'day', 
                    'in': {
                        '$dateAdd': {
                            'startDate': '$dates.startdate', 
                            'unit': 'day', 
                            'amount': '$$day'
                        }
                    }
                }
            }
        }
    }, {
        '$unwind': '$date'
    }, {
        '$lookup': {
            'from': 'traffic', 
            'let': {
                'marketplace': '$_id', 
                'date': '$date'
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
                                        '$date', '$$date'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'asin': '$asin', 
                        'data': '$traffic', 
                        '_id': 0
                    }
                }
            ], 
            'as': 'traffic'
        }
    }, {
        '$lookup': {
            'from': 'date_analytics', 
            'let': {
                'marketplace': '$_id', 
                'collatetype': 'sku', 
                'date': '$date'
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
                                        '$collatetype', '$$collatetype'
                                    ]
                                }, {
                                    '$eq': [
                                        '$date', '$$date'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'value': '$asin', 
                        'data': '$data', 
                        '_id': 0
                    }
                }
            ], 
            'as': 'data'
        }
    }, {
        '$set': {
            'asindata': {
                '$reduce': {
                    'input': '$traffic', 
                    'initialValue': [], 
                    'in': {
                        '$let': {
                            'vars': {
                                'asin': '$$this.asin', 
                                'traffic': '$$this.data', 
                                'salesdata': {
                                    '$map': {
                                        'input': {
                                            '$filter': {
                                                'input': '$data', 
                                                'as': 'd', 
                                                'cond': {
                                                    '$eq': [
                                                        '$$d.value', '$$this.asin'
                                                    ]
                                                }
                                            }
                                        }, 
                                        'as': 'x', 
                                        'in': '$$x.data'
                                    }
                                }
                            }, 
                            'in': {
                                '$concatArrays': [
                                    '$$value', [
                                        {
                                            'value': '$$asin', 
                                            'data': {
                                                '$mergeObjects': [
                                                    '$$traffic', {
                                                        '$cond': {
                                                            'if': {
                                                                '$lte': [
                                                                    {
                                                                        '$size': '$$salesdata'
                                                                    }, 1
                                                                ]
                                                            }, 
                                                            'then': {
                                                                '$ifNull': [
                                                                    {
                                                                        '$first': '$$salesdata'
                                                                    }, {}
                                                                ]
                                                            }, 
                                                            'else': {
                                                                '$reduce': {
                                                                    'input': '$$salesdata', 
                                                                    'initialValue': {}, 
                                                                    'in': {
                                                                        '$arrayToObject': {
                                                                            '$filter': {
                                                                                'input': {
                                                                                    '$map': {
                                                                                        'input': {
                                                                                            '$setUnion': [
                                                                                                {
                                                                                                    '$map': {
                                                                                                        'input': {
                                                                                                            '$objectToArray': '$$value'
                                                                                                        }, 
                                                                                                        'as': 'v', 
                                                                                                        'in': '$$v.k'
                                                                                                    }
                                                                                                }, {
                                                                                                    '$map': {
                                                                                                        'input': {
                                                                                                            '$objectToArray': '$$this'
                                                                                                        }, 
                                                                                                        'as': 't', 
                                                                                                        'in': '$$t.k'
                                                                                                    }
                                                                                                }
                                                                                            ]
                                                                                        }, 
                                                                                        'as': 'key', 
                                                                                        'in': {
                                                                                            'k': '$$key', 
                                                                                            'v': {
                                                                                                '$round': [
                                                                                                    {
                                                                                                        '$add': [
                                                                                                            {
                                                                                                                '$ifNull': [
                                                                                                                    {
                                                                                                                        '$getField': {
                                                                                                                            'field': '$$key', 
                                                                                                                            'input': '$$value'
                                                                                                                        }
                                                                                                                    }, 0
                                                                                                                ]
                                                                                                            }, {
                                                                                                                '$ifNull': [
                                                                                                                    {
                                                                                                                        '$getField': {
                                                                                                                            'field': '$$key', 
                                                                                                                            'input': '$$this'
                                                                                                                        }
                                                                                                                    }, 0
                                                                                                                ]
                                                                                                            }
                                                                                                        ]
                                                                                                    }, 2
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }, 
                                                                                'as': 'item', 
                                                                                'cond': {
                                                                                    '$ne': [
                                                                                        '$$item.v', 0
                                                                                    ]
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
                                        }
                                    ]
                                ]
                            }
                        }
                    }
                }
            }
        }
    }, {
        '$set': {
            'excluded': {
                '$let': {
                    'vars': {
                        'allasins': {
                            '$reduce': {
                                'input': '$asindata', 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            '$$this.value'
                                        ]
                                    ]
                                }
                            }
                        }
                    }, 
                    'in': {
                        '$filter': {
                            'input': '$data', 
                            'as': 'd', 
                            'cond': {
                                '$not': {
                                    '$in': [
                                        '$$d.value', '$$allasins'
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                'marketplace': '$_id', 
                'date': '$date', 
                'collatetype': 'asin', 
                'data': {
                    '$concatArrays': [
                        '$asindata', '$excluded'
                    ]
                }
            }
        }
    }, {
        '$unwind': {
            'path': '$data', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$lookup': {
            'from': 'products', 
            'let': {
                'marketplace': '$marketplace', 
                'asin': '$data.value'
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
                                        '$asin', '$$asin'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'parentsku': '$parentsku', 
                        'parentasin': '$parentasin', 
                        'category': '$producttype', 
                        '_id': 0
                    }
                }
            ], 
            'as': 'result'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    {
                        '$unsetField': {
                            'input': '$$ROOT', 
                            'field': 'result'
                        }
                    }, '$data', {
                        '$first': '$result'
                    }
                ]
            }
        }
    }, {
        '$merge': 'date_analytics'
    }
]