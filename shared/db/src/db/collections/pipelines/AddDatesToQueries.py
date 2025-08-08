def execute():
    return [
        {
        '$lookup': {
            'from': 'queries', 
            'let': {
                'marketplace': '$_id'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$or': [
                                {
                                    '$eq': [
                                        {
                                            '$ifNull': [
                                                '$marketplace', None
                                            ]
                                        }, None
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }
                            ]
                        }
                    }
                }
            ], 
            'as': 'query'
        }
    }, {
        '$unwind': {
            'path': '$query'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    '$query', {
                        'marketplace': '$_id', 
                        'uid': '$uid', 
                        'endDate': '$endDate'
                    }
                ]
            }
        }
    }, {
        '$set': {
            'currParts': {
                '$dateToParts': {
                    'date': '$endDate'
                }
            }
        }
    }, {
        '$set': {
            'dates': {
                '$cond': [
                    {
                        '$eq': [
                            '$group', 'Days'
                        ]
                    }, {
                        'curr': {
                            '$reduce': {
                                'input': {
                                    '$range': [
                                        1, {
                                            '$sum': [
                                                '$days', 1
                                            ]
                                        }, 1
                                    ]
                                }, 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                '$dateSubtract': {
                                                    'startDate': '$endDate', 
                                                    'unit': 'day', 
                                                    'amount': '$$this'
                                                }
                                            }
                                        ]
                                    ]
                                }
                            }
                        }, 
                        'pre': {
                            '$reduce': {
                                'input': {
                                    '$range': [
                                        {
                                            '$sum': [
                                                '$days', 1
                                            ]
                                        }, {
                                            '$sum': [
                                                {
                                                    '$multiply': [
                                                        '$days', 2
                                                    ]
                                                }, 1
                                            ]
                                        }, 1
                                    ]
                                }, 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                '$dateSubtract': {
                                                    'startDate': '$endDate', 
                                                    'unit': 'day', 
                                                    'amount': '$$this'
                                                }
                                            }
                                        ]
                                    ]
                                }
                            }
                        }
                    }, '$dates'
                ]
            }
        }
    }, {
        '$set': {
            'dates': {
                '$cond': [
                    {
                        '$eq': [
                            '$group', 'Current Month'
                        ]
                    }, {
                        'curr': {
                            '$reduce': {
                                'input': {
                                    '$range': [
                                        {
                                            '$subtract': [
                                                '$currParts.day', 1
                                            ]
                                        }, 0, -1
                                    ]
                                }, 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                '$dateFromParts': {
                                                    'year': '$currParts.year', 
                                                    'month': '$currParts.month', 
                                                    'day': '$$this'
                                                }
                                            }
                                        ]
                                    ]
                                }
                            }
                        }, 
                        'pre': {
                            '$let': {
                                'vars': {
                                    'month': {
                                        '$cond': [
                                            {
                                                '$eq': [
                                                    '$currParts.month', 1
                                                ]
                                            }, 12, {
                                                '$subtract': [
                                                    '$currParts.month', 1
                                                ]
                                            }
                                        ]
                                    }, 
                                    'year': {
                                        '$cond': [
                                            {
                                                '$eq': [
                                                    '$currParts.month', 1
                                                ]
                                            }, {
                                                '$subtract': [
                                                    '$currParts.year', 1
                                                ]
                                            }, '$currParts.year'
                                        ]
                                    }, 
                                    'range': {
                                        '$cond': [
                                            {
                                                '$eq': [
                                                    '$tag', 'Current vs Previous (Full)'
                                                ]
                                            }, {
                                                '$range': [
                                                    0, 31, 1
                                                ]
                                            }, {
                                                '$range': [
                                                    0, {
                                                        '$subtract': [
                                                            '$currParts.day', 1
                                                        ]
                                                    }, 1
                                                ]
                                            }
                                        ]
                                    }
                                }, 
                                'in': {
                                    '$let': {
                                        'vars': {
                                            'startDate': {
                                                '$dateFromParts': {
                                                    'year': '$$year', 
                                                    'month': '$$month', 
                                                    'day': 1
                                                }
                                            }
                                        }, 
                                        'in': {
                                            '$reduce': {
                                                'input': '$$range', 
                                                'initialValue': [], 
                                                'in': {
                                                    '$concatArrays': [
                                                        '$$value', {
                                                            '$let': {
                                                                'vars': {
                                                                    'date': {
                                                                        '$dateAdd': {
                                                                            'startDate': '$$startDate', 
                                                                            'unit': 'day', 
                                                                            'amount': '$$this'
                                                                        }
                                                                    }
                                                                }, 
                                                                'in': {
                                                                    '$cond': [
                                                                        {
                                                                            '$eq': [
                                                                                {
                                                                                    '$month': '$$date'
                                                                                }, '$$month'
                                                                            ]
                                                                        }, [
                                                                            '$$date'
                                                                        ], []
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
                    }, '$dates'
                ]
            }
        }
    }, {
        '$set': {
            'dates': {
                '$cond': [
                    {
                        '$eq': [
                            '$tag', 'Custom'
                        ]
                    }, {
                        'curr': {
                            '$reduce': {
                                'input': {
                                    '$range': [
                                        0, {
                                            '$sum': [
                                                {
                                                    '$dateDiff': {
                                                        'startDate': '$curr.startDate', 
                                                        'endDate': '$curr.endDate', 
                                                        'unit': 'day'
                                                    }
                                                }, 1
                                            ]
                                        }, 1
                                    ]
                                }, 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                '$dateAdd': {
                                                    'startDate': '$curr.startDate', 
                                                    'unit': 'day', 
                                                    'amount': '$$this'
                                                }
                                            }
                                        ]
                                    ]
                                }
                            }
                        }, 
                        'pre': {
                            '$reduce': {
                                'input': {
                                    '$range': [
                                        0, {
                                            '$sum': [
                                                {
                                                    '$dateDiff': {
                                                        'startDate': '$pre.startDate', 
                                                        'endDate': '$pre.endDate', 
                                                        'unit': 'day'
                                                    }
                                                }, 1
                                            ]
                                        }, 1
                                    ]
                                }, 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                '$dateAdd': {
                                                    'startDate': '$pre.startDate', 
                                                    'unit': 'day', 
                                                    'amount': '$$this'
                                                }
                                            }
                                        ]
                                    ]
                                }
                            }
                        }
                    }, '$dates'
                ]
            }
        }
    }, {
        '$set': {
            '_id': '$_id', 
            'marketplace': '$marketplace', 
            'dates': '$dates', 
            'allDates': {
                '$concatArrays': [
                    '$dates.curr', '$dates.pre'
                ]
            }
        }
    }
    ]