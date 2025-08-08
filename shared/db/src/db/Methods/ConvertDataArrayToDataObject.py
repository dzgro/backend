def execute():
    return {
            'data': {
                '$arrayToObject': {
                    '$reduce': {
                        'input': '$data', 
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