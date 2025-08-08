def execute(hasKeys: bool):
    if hasKeys: return getFromKeys()
    return [{
        '$lookup': {
            'from': 'analytics_calculation', 
            'pipeline': [
                {
                    '$match': {
                        'isPercent': True
                    }
                }, {
                    '$project': {
                        'key': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'percentKeys'
        }
    }, {
        '$set': {
            'percentKeys': {
                '$reduce': {
                    'input': '$percentKeys', 
                    'initialValue': [], 
                    'in': {
                        '$concatArrays': [
                            '$$value', [
                                '$$this.key'
                            ]
                        ]
                    }
                }
            }
        }
    }]

def getFromKeys():
    return [{
        "$set": {
            "percentKeys": {
                "$reduce": {
                    "input": "$keys",
                    "initialValue": [],
                    "in": {
                        "$concatArrays": [
                            "$$value",
                            {
                                "$cond": [
                                    {"$eq": [{"$ifNull": ["$$this.isPercent", False]}, True]},
                                    ["$$this.key"],
                                    []
                                ]
                            }
                        ]
                    }
                }
            }
        }
    }]