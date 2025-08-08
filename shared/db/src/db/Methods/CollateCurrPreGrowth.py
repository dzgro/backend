def collate(objectKey:str):
    return {
        '$set': {
            objectKey: {
                '$reduce': {
                    'input': f'${objectKey}', 
                    'initialValue': {}, 
                    'in': {
                        '$mergeObjects': [
                            '$$value', {
                                '$let': {
                                    'vars': {
                                        'val': '$$value'
                                    }, 
                                    'in': {
                                        '$reduce': {
                                            'input': {
                                                '$objectToArray': '$$this'
                                            }, 
                                            'initialValue': {}, 
                                            'in': {
                                                '$cond': [
                                                    {
                                                        '$ne': [
                                                            {
                                                                '$type': '$$this.v'
                                                            }, 'object'
                                                        ]
                                                    }, '$$value', {
                                                        '$let': {
                                                            'vars': {
                                                                'data': {
                                                                    '$ifNull': [
                                                                        {
                                                                            '$getField': {
                                                                                'input': '$$val', 
                                                                                'field': '$$this.k'
                                                                            }
                                                                        }, {
                                                                            'curr': 0, 
                                                                            'pre': 0
                                                                        }
                                                                    ]
                                                                }
                                                            }, 
                                                            'in': {
                                                                '$mergeObjects': [
                                                                    '$$value', {
                                                                        '$arrayToObject': [
                                                                            [
                                                                                {
                                                                                    'k': '$$this.k', 
                                                                                    'v': {
                                                                                        'curr': {
                                                                                            '$sum': [
                                                                                                '$$this.v.curr', '$$data.curr'
                                                                                            ]
                                                                                        }, 
                                                                                        'pre': {
                                                                                            '$sum': [
                                                                                                '$$this.v.pre', '$$data.pre'
                                                                                            ]
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
    }