def execute():
    return {
        "$lookup": {
            "from": "analytics_calculation",
            "pipeline": [
                {
                "$project": {
                    "_id": 0
                }
                }
            ],
            "as": "keys"
            }
    }