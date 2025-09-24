from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollateType, CollectionType
from dzgroshared.analytics import controller
from dzgroshared.db.model import PeriodDataRequest

def addPeriodData(pp: PipelineProcessor):
    return [{
        '$addFields': {
            'periods': {
                '$let': {
                    'vars': {
                        'enddate': '$dates.enddate', 
                        'startdate': '$dates.startdate'
                    }, 
                    'in': {
                        '$let': {
                            'vars': {
                                'thirtyDaysAgo': {
                                    '$dateSubtract': {
                                        'startDate': '$$enddate', 
                                        'unit': 'day', 
                                        'amount': 30
                                    }
                                }, 
                                'firstOfThisMonth': {
                                    '$dateTrunc': {
                                        'date': '$$enddate', 
                                        'unit': 'month'
                                    }
                                }, 
                                'firstOfLastMonth': {
                                    '$dateTrunc': {
                                        'date': {
                                            '$dateSubtract': {
                                                'startDate': '$$enddate', 
                                                'unit': 'month', 
                                                'amount': 1
                                            }
                                        }, 
                                        'unit': 'month'
                                    }
                                }, 
                                'sameDayLastMonth': {
                                    '$dateSubtract': {
                                        'startDate': '$$enddate', 
                                        'unit': 'month', 
                                        'amount': 1
                                    }
                                }, 
                                'endOfLastMonth': {
                                    '$dateSubtract': {
                                        'startDate': {
                                            '$dateTrunc': {
                                                'date': '$$enddate', 
                                                'unit': 'month'
                                            }
                                        }, 
                                        'unit': 'day', 
                                        'amount': 1
                                    }
                                }
                            }, 
                            'in': [
                                {
                                    'label': 'Last 30 Days', 
                                    'startdate': '$$thirtyDaysAgo', 
                                    'enddate': '$$enddate', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$$thirtyDaysAgo', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$$enddate', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }, {
                                    'label': 'This Month', 
                                    'startdate': '$$firstOfThisMonth', 
                                    'enddate': '$$enddate', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$$firstOfThisMonth', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$$enddate', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }, {
                                    'label': 'Last Month Till Date', 
                                    'startdate': '$$firstOfLastMonth', 
                                    'enddate': '$$sameDayLastMonth', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$$firstOfLastMonth', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$$sameDayLastMonth', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }, {
                                    'label': 'Last Month (Complete)', 
                                    'startdate': '$$firstOfLastMonth', 
                                    'enddate': '$$endOfLastMonth', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$$firstOfLastMonth', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$$endOfLastMonth', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
    {
        "$unwind": {
            "path": "$periods"
        }
    },
    ]

def pipeline(marketplace: ObjectId, req: PeriodDataRequest):
    pp = PipelineProcessor(None, marketplace)
    pipeline: list[dict] = [{ '$match': { '_id': marketplace } }]
    pipeline.extend(addPeriodData(pp))
    lookuppipelineQueries = [ { '$eq': [ '$marketplace', '$$marketplace' ] }, {'$eq': ["$collatetype", "$$collatetype"]} ]
    if req.value is not None: lookuppipelineQueries.append( { '$eq': [ "$value", "$$value" ] } )
    lookuppipelineQueries.extend([ { '$gte': [ '$date', '$$startdate' ] }, { '$lte': [ '$date', '$$enddate' ] } ])
    matchStage = { '$match': { '$expr': { '$and': lookuppipelineQueries } } }
    lookuppipeline = [matchStage, {"$replaceRoot": { "newRoot": "$data" }}]
    lookupdata = {
        '$lookup': {
            'from': CollectionType.DATE_ANALYTICS.value,
            'let': { 'marketplace': '$_id', 'startdate': '$periods.startdate', 'enddate': '$periods.enddate', "value": req.value, "collatetype": req.collatetype.value },
            'pipeline': lookuppipeline,
            'as': 'data'
        }
    }
    pipeline.extend([lookupdata, pp.collateData(), controller.addMissingFields()]+controller.addDerivedMetrics())
    pipeline.append({
        "$replaceRoot": {
            "newRoot": {
                "label": "$periods.label",
                "dateSpan": "$periods.dateSpan",
                "data": "$data"
            }
        }
    })
    return pipeline