def execute():
    return {
        "$set": {
            'keys': {
                '$reduce': {
                    'input': '$keys', 
                    'initialValue': [], 
                    'in': {
                        '$cond': [
                            {
                                '$eq': [
                                    {
                                        '$indexOfArray': [
                                            '$$value.label', '$$this.group'
                                        ]
                                    }, -1
                                ]
                            }, {
                                '$concatArrays': [
                                    '$$value', [
                                        {
                                            'label': '$$this.group', 
                                            'items': [
                                                {
                                                    'label': '$$this.label', 
                                                    'value': '$$this.key'
                                                }
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
                                                    '$$v.label', '$$this.group'
                                                ]
                                            }, '$$v', {
                                                '$mergeObjects': [
                                                    '$$v', {
                                                        'items': {
                                                            '$concatArrays': [
                                                                '$$v.items', [
                                                                    {
                                                                        'label': '$$this.label', 
                                                                        'value': '$$this.key'
                                                                    }
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