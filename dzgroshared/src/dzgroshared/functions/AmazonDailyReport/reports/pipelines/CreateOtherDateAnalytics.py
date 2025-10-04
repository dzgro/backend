from bson import ObjectId
from dzgroshared.db.model import StartEndDate


def pipeline(marketplace: ObjectId, dates: StartEndDate):
    setdates = dates.model_dump()
    return [
    {
        '$match': {
            '_id': marketplace,
        }
    }, {
        '$set': {
            'dates': setdates
        }
    },{
        "$set": {
            "date": {
                "$map": {
                    "input": {
                        "$range": [
                            0, {
                                "$sum": [
                                    {
                                        "$dateDiff": {
                                            "startDate": "$dates.startdate", 
                                            "endDate": "$dates.enddate", 
                                            "unit": "day"
                                        }
                                    }, 1
                                ]
                            }, 1
                        ]
                    }, 
                    "as": "day", 
                    "in": {
                        "$dateAdd": {
                            "startDate": "$dates.startdate", 
                            "unit": "day", 
                            "amount": "$$day"
                        }
                    }
                }
            }
        }
    }, {
        "$unwind": "$date"
    }, {
        "$lookup": {
            "from": "date_analytics", 
            "let": {
                "marketplace": "$_id", 
                "collatetype": "asin", 
                "date": "$date"
            }, 
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {
                                    "$eq": [
                                        "$marketplace", "$$marketplace"
                                    ]
                                }, {
                                    "$eq": [
                                        "$collatetype", "$$collatetype"
                                    ]
                                }, {
                                    "$eq": [
                                        "$date", "$$date"
                                    ]
                                }
                            ]
                        }
                    }
                }
            ], 
            "as": "data"
        }
    }, {
        "$addFields": {
            "data": {
                "$let": {
                    "vars": {
                        "summary": {
                            "$reduce": {
                                "input": "$data", 
                                "initialValue": {
                                    "marketplace": {}, 
                                    "parentsku": {}, 
                                    "category": {}
                                }, 
                                "in": {
                                    "marketplace": {
                                        "$mergeObjects": [
                                            "$$value.marketplace", {
                                                "$arrayToObject": {
                                                    "$map": {
                                                        "input": {
                                                            "$objectToArray": "$$this.data"
                                                        }, 
                                                        "as": "kv", 
                                                        "in": {
                                                            "k": "$$kv.k", 
                                                            "v": {
                                                                "$add": [
                                                                    {
                                                                        "$ifNull": [
                                                                            {
                                                                                "$getField": {
                                                                                    "field": "$$kv.k", 
                                                                                    "input": "$$value.marketplace"
                                                                                }
                                                                            }, 0
                                                                        ]
                                                                    }, "$$kv.v"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }, 
                                    "parentsku": {
                                        "$cond": [
                                            {
                                                "$ifNull": [
                                                    "$$this.parentsku", False
                                                ]
                                            }, {
                                                "$mergeObjects": [
                                                    "$$value.parentsku", {
                                                        "$arrayToObject": [
                                                            [
                                                                {
                                                                    "k": "$$this.parentsku", 
                                                                    "v": {
                                                                        "$mergeObjects": [
                                                                            {
                                                                                "$ifNull": [
                                                                                    {
                                                                                        "$getField": {
                                                                                            "field": "$$this.parentsku", 
                                                                                            "input": "$$value.parentsku"
                                                                                        }
                                                                                    }, {}
                                                                                ]
                                                                            }, {
                                                                                "$arrayToObject": {
                                                                                    "$map": {
                                                                                        "input": {
                                                                                            "$objectToArray": "$$this.data"
                                                                                        }, 
                                                                                        "as": "kv", 
                                                                                        "in": {
                                                                                            "k": "$$kv.k", 
                                                                                            "v": {
                                                                                                "$add": [
                                                                                                    {
                                                                                                        "$ifNull": [
                                                                                                            {
                                                                                                                "$getField": {
                                                                                                                    "field": "$$kv.k", 
                                                                                                                    "input": {
                                                                                                                        "$getField": {
                                                                                                                            "field": "$$this.parentsku", 
                                                                                                                            "input": "$$value.parentsku"
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }, 0
                                                                                                        ]
                                                                                                    }, "$$kv.v"
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            ]
                                                        ]
                                                    }
                                                ]
                                            }, "$$value.parentsku"
                                        ]
                                    }, 
                                    "category": {
                                        "$cond": [
                                            {
                                                "$ifNull": [
                                                    "$$this.category", False
                                                ]
                                            }, {
                                                "$mergeObjects": [
                                                    "$$value.category", {
                                                        "$arrayToObject": [
                                                            [
                                                                {
                                                                    "k": "$$this.category", 
                                                                    "v": {
                                                                        "$mergeObjects": [
                                                                            {
                                                                                "$ifNull": [
                                                                                    {
                                                                                        "$getField": {
                                                                                            "field": "$$this.category", 
                                                                                            "input": "$$value.category"
                                                                                        }
                                                                                    }, {}
                                                                                ]
                                                                            }, {
                                                                                "$arrayToObject": {
                                                                                    "$map": {
                                                                                        "input": {
                                                                                            "$objectToArray": "$$this.data"
                                                                                        }, 
                                                                                        "as": "kv", 
                                                                                        "in": {
                                                                                            "k": "$$kv.k", 
                                                                                            "v": {
                                                                                                "$add": [
                                                                                                    {
                                                                                                        "$ifNull": [
                                                                                                            {
                                                                                                                "$getField": {
                                                                                                                    "field": "$$kv.k", 
                                                                                                                    "input": {
                                                                                                                        "$getField": {
                                                                                                                            "field": "$$this.category", 
                                                                                                                            "input": "$$value.category"
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }, 0
                                                                                                        ]
                                                                                                    }, "$$kv.v"
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            ]
                                                        ]
                                                    }
                                                ]
                                            }, "$$value.category"
                                        ]
                                    }
                                }
                            }
                        }
                    }, 
                    "in": {
                        "$concatArrays": [
                            [
                                {
                                    "collatetype": "marketplace", 
                                    "data": "$$summary.marketplace"
                                }
                            ], {
                                "$map": {
                                    "input": {
                                        "$objectToArray": "$$summary.parentsku"
                                    }, 
                                    "as": "p", 
                                    "in": {
                                        "collatetype": "parentsku", 
                                        "value": "$$p.k", 
                                        "data": "$$p.v"
                                    }
                                }
                            }, {
                                "$map": {
                                    "input": {
                                        "$objectToArray": "$$summary.category"
                                    }, 
                                    "as": "c", 
                                    "in": {
                                        "collatetype": "category", 
                                        "value": "$$c.k", 
                                        "data": "$$c.v"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }, {
        "$unwind": {
            "path": "$data", 
            "preserveNullAndEmptyArrays": False
        }
    }, {
        "$replaceRoot": {
            "newRoot": {
                "$mergeObjects": [
                    {
                        "marketplace": "$_id", 
                        "date": "$date"
                    }, "$data"
                ]
            }
        }
    }, {
        "$merge": {
            "into": "date_analytics"
        }
    }
]