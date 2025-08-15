def execute(objectKey:str):
    return {
        '$set': {
            objectKey: {
                '$arrayToObject': {
                    '$reduce': {
                        'input': {
                            '$objectToArray': f'${objectKey}'
                        }, 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', [
                                    {
                                        'k': '$$this.k', 
                                        'v': {
                                            "curr": {"$round": ["$$this.v.curr",2]},
                                            "pre": {"$round": ["$$this.v.pre",2]},
                                            "growth": {
                                            '$let': {
                                                'vars': {
                                                    'isPercent': {
                                                        '$ifNull': [
                                                            {
                                                                '$getField': {
                                                                    'input': {
                                                                        '$ifNull': [
                                                                            {
                                                                                '$first': {
                                                                                    '$filter': {
                                                                                        'input': '$keys', 
                                                                                        'as': 'k', 
                                                                                        'cond': {
                                                                                            '$eq': [
                                                                                                '$$this.k', '$$k.key'
                                                                                            ]
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }, {
                                                                                'isPercent': False
                                                                            }
                                                                        ]
                                                                    }, 
                                                                    'field': 'isPercent'
                                                                }
                                                            }, False
                                                        ]
                                                    }
                                                }, 
                                                'in': {
                                                    '$cond': [
                                                        '$$isPercent', {
                                                                        '$round': [
                                                                            {
                                                                                '$subtract': [
                                                                                    '$$this.v.curr', '$$this.v.pre'
                                                                                ]
                                                                            }, 2
                                                                        ]
                                                                    }, {
                                                                        '$cond': [
                                                                            {
                                                                                '$eq': [
                                                                                    '$$this.v.pre', 0
                                                                                ]
                                                                            }, 0, {
                                                                                '$round': [
                                                                                    {
                                                                                        '$multiply': [
                                                                                            {
                                                                                                '$subtract': [
                                                                                                    {
                                                                                                        '$divide': [
                                                                                                            '$$this.v.curr', '$$this.v.pre'
                                                                                                        ]
                                                                                                    }, 1
                                                                                                ]
                                                                                            }, 100
                                                                                        ]
                                                                                    }, 2
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                    ]
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
        }
    }