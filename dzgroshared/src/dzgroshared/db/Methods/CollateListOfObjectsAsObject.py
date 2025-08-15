def execute(key: str):
    return {
                '$arrayToObject': {
                    '$reduce': {
                        'input': f'${key}', 
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