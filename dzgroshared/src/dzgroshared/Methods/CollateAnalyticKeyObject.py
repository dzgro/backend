def collate(objectKey:str = "data"):
    return {
        '$set': {
            objectKey: {
                "$arrayToObject": {
                    '$reduce': {
                        'input': f'${objectKey}', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', {
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
                                                                'k': "$$this.k", 
                                                                'v': {
                                                                    '$sum': [
                                                                        '$$this.v', {
                                                                            '$ifNull': [
                                                                                {
                                                                                    '$getField': {
                                                                                        'input': {"$arrayToObject":'$$curr'}, 
                                                                                        'field': "$$this.k"
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
                            ]
                        }
                    }
                }
            }
        }
    }