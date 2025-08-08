def execute(month: str|None):
    pipeline = [
    {
        '$set': {
            'dateDiff': {
                '$sum': [
                    {
                        '$dateDiff': {
                            'startDate': '$startdate', 
                            'endDate': '$enddate', 
                            'unit': 'day'
                        }
                    }, 1
                ]
            }
        }
    }, {
        '$set': {
            'month': {
                '$reduce': {
                    'input': {
                        '$range': [
                            0, '$dateDiff', 1
                        ]
                    }, 
                    'initialValue': [], 
                    'in': {
                        '$let': {
                            'vars': {
                                'date': {
                                    '$dateAdd': {
                                        'startDate': '$startdate', 
                                        'amount': '$$this', 
                                        'unit': 'day'
                                    }
                                }
                            }, 
                            'in': {
                                '$let': {
                                    'vars': {
                                        'month': {
                                            '$month': '$$date'
                                        }, 
                                        'year': {
                                            '$year': '$$date'
                                        }, 
                                        'monthStr': {
                                            '$dateToString': {
                                                'date': {
                                                    '$dateFromParts': {
                                                        'month': {
                                                            '$month': '$$date'
                                                        }, 
                                                        'year': {
                                                            '$year': '$$date'
                                                        }
                                                    }
                                                }, 
                                                'format': '%b %Y'
                                            }
                                        }
                                    }, 
                                    'in': {
                                        '$cond': [
                                            {
                                                '$eq': [
                                                    {
                                                        '$indexOfArray': [
                                                            '$$value.monthStr', '$$monthStr'
                                                        ]
                                                    }, -1
                                                ]
                                            }, {
                                                '$concatArrays': [
                                                    '$$value', [
                                                        {
                                                            'month': '$$month', 
                                                            'year': '$$year', 
                                                            'monthStr': '$$monthStr', 
                                                            'date': [
                                                                '$$date'
                                                            ]
                                                        }
                                                    ]
                                                ]
                                            }, {
                                                '$map': {
                                                    'input': '$$value', 
                                                    'as': 'v', 
                                                    'in': {
                                                        '$cond': [
                                                            {
                                                                '$ne': [
                                                                    '$$v.monthStr', '$$monthStr'
                                                                ]
                                                            }, '$$v', {
                                                                '$mergeObjects': [
                                                                    '$$v', {
                                                                        'date': {
                                                                            '$concatArrays': [
                                                                                '$$v.date', [
                                                                                    '$$date'
                                                                                ]
                                                                            ]
                                                                        }
                                                                    }
                                                                ]
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
                    }
                }
            }
        }
    }, {
        '$project': {
            'month': 1,
            'uid': 1,
        }
    }, {
        '$unwind': {
            'path': '$month'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                "$mergeObjects": [
                    '$month',
                    {
                    "uid": "$uid",
                    "marketplace": "$_id",
      }
                ]
            }
        }
    }, {
        '$set': {
            'period': {
                '$let': {
                    'vars': {
                        'date': {
                            '$sortArray': {
                                'input': '$date', 
                                'sortBy': 1
                            }
                        }
                    }, 
                    'in': {
                        '$concat': [
                            {
                                '$dateToString': {
                                    'date': {
                                        '$first': '$$date'
                                    }, 
                                    'format': '%d'
                                }
                            }, '-', {
                                '$dateToString': {
                                    'date': {
                                        '$last': '$$date'
                                    }, 
                                    'format': '%d %b, %Y'
                                }
                            }
                        ]
                    }
                }
            }
        }
    },
    {
        "$sort": {
            "year": -1,
            "month": -1
        }
    }
]
    
    if month: pipeline.append({"$match": {"monthStr": month}})
    return pipeline
        
