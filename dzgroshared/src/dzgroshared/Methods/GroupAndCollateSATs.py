def execute(groupBy: str|dict|None)->list[dict]:
    return [
        {
        '$group': {
            '_id': groupBy, 
            'sales': {
                '$push': '$sales'
            }, 
            'ad': {
                '$push': '$ad'
            }, 
            'traffic': {
                '$push': '$traffic'
            }
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    '$$ROOT', {
                        '$arrayToObject': {
                            '$reduce': {
                                'input': [
                                    'sales', 'ad', 'traffic'
                                ], 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                'k': '$$this', 
                                                'v': {
                                                    '$arrayToObject': {
                                                        '$reduce': {
                                                            'input': {
                                                                '$getField': {
                                                                    'input': '$$ROOT', 
                                                                    'field': '$$this'
                                                                }
                                                            }, 
                                                            'initialValue': [], 
                                                            'in': {
                                                                '$let': {
                                                                    'vars': {
                                                                        'curr': '$$value'
                                                                    }, 
                                                                    'in': {
                                                                        '$reduce': {
                                                                            'input': {
                                                                                '$objectToArray': '$$this'
                                                                            }, 
                                                                            'initialValue': [], 
                                                                            'in': {
                                                                                '$concatArrays': [
                                                                                    '$$value', [
                                                                                        {
                                                                                            'k': '$$this.k', 
                                                                                            'v': {
                                                                                                '$sum': [
                                                                                                    '$$this.v', {
                                                                                                        '$ifNull': [
                                                                                                            {
                                                                                                                '$getField': {
                                                                                                                    'input': {
                                                                                                                        '$first': {
                                                                                                                            '$filter': {
                                                                                                                                'input': '$$curr', 
                                                                                                                                'as': 'c', 
                                                                                                                                'cond': {
                                                                                                                                    '$eq': [
                                                                                                                                        '$$c.k', '$$this.k'
                                                                                                                                    ]
                                                                                                                                }
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }, 
                                                                                                                    'field': 'v'
                                                                                                                }
                                                                                                            }, 0
                                                                                                        ]
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
                                                    }
                                                }
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
    }
    ]