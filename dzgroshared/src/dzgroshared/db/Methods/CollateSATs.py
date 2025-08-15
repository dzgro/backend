def execute():
    return {
        '$arrayToObject': {
            '$reduce': {
                'input': [
                    'sales', 'ad', 'traffic'
                ], 
                'initialValue': [], 
                'in': {
                    "$let": {
                        "vars": {
                            "input": {
                                "$ifNull": [
                                    {
                                        '$getField': {
                                            'input': '$$ROOT', 
                                            'field': '$$this'
                                        }
                                    },
                                    []
                                ]
                            }
                        },
                        "in": {
                            "$cond": [
                                {"$eq": [{"$size": "$$input"}, 0]},
                                "$$value",
                                {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                'k': '$$this', 
                                                'v': {
                                                    '$arrayToObject': {
                                                        '$reduce': {
                                                            'input': "$$input", 
                                                            'initialValue': [], 
                                                            'in': {
                                                                '$let': {
                                                                    'vars': {
                                                                        'val': '$$value',
                                                                        'curr': {
                                                                                '$objectToArray': '$$this'
                                                                            }
                                                                    }, 
                                                                    'in': {
                                                                        '$reduce': {
                                                                            'input': '$$curr', 
                                                                            'initialValue': '$$val', 
                                                                            'in': {
                                                                                '$cond': [
                                                                                    {
                                                                                        '$eq': [
                                                                                            {
                                                                                                '$indexOfArray': [
                                                                                                    '$$value.k', '$$this.k'
                                                                                                ]
                                                                                            }, -1
                                                                                        ]
                                                                                    }, {
                                                                                        '$concatArrays': [
                                                                                            '$$value', [
                                                                                                '$$this'
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
                                                                                                            '$$v.k', '$$this.k'
                                                                                                        ]
                                                                                                    }, '$$v', {
                                                                                                        '$mergeObjects': [
                                                                                                            '$$v', {
                                                                                                                'v': {
                                                                                                                    '$sum': [
                                                                                                                        '$$v.v', '$$this.v'
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
                                            }
                                        ]
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }