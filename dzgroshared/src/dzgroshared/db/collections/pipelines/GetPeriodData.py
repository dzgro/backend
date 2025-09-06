
from dzgroshared.models.collections.analytics import PeriodDataRequest
from dzgroshared.db.PipelineProcessor import PipelineProcessor


def pipeline(pp: PipelineProcessor, req: PeriodDataRequest):
    match = { '$match': { '_id': pp.marketplace, 'uid': pp.uid } }
    lookuplet= { 'uid': '$uid', 'marketplace': '$_id', 'collatetype': req.collatetype.value, 'startdate': '$dates.startdate', 'enddate': '$dates.enddate' }
    if req.value: lookuplet.update({ 'value': req.value })
    lookupmatch = { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] } ] } } }
    if req.value: lookupmatch['$match']['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
    pipeline = [
        match
    , {
        '$lookup': {
            'from': 'date_analytics', 
            'let': lookuplet, 
            'pipeline': [
                lookupmatch, {
                    '$set': {
                        'dataArray': {
                            '$objectToArray': '$data'
                        }
                    }
                }, {
                    '$addFields': {
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
                    }
                }, {
                    '$facet': {
                        'last30Days': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$date', '$thirtyDaysAgo'
                                                ]
                                            }, {
                                                '$lte': [
                                                    '$date', '$$enddate'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }, {
                                '$unwind': '$dataArray'
                            }, {
                                '$group': {
                                    '_id': '$dataArray.k', 
                                    'value': {
                                        '$sum': '$dataArray.v'
                                    }, 
                                    'start': {
                                        '$min': '$date'
                                    }, 
                                    'end': {
                                        '$max': '$date'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': None, 
                                    'kv': {
                                        '$push': {
                                            'k': '$_id', 
                                            'v': '$value'
                                        }
                                    }, 
                                    'start': {
                                        '$min': '$start'
                                    }, 
                                    'end': {
                                        '$max': '$end'
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0, 
                                    'data': {
                                        '$arrayToObject': '$kv'
                                    }, 
                                    'label': 'Last 30 Days', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$start', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$end', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ], 
                        'thisMonth': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$date', '$firstOfThisMonth'
                                                ]
                                            }, {
                                                '$lte': [
                                                    '$date', '$$enddate'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }, {
                                '$unwind': '$dataArray'
                            }, {
                                '$group': {
                                    '_id': '$dataArray.k', 
                                    'value': {
                                        '$sum': '$dataArray.v'
                                    }, 
                                    'start': {
                                        '$min': '$date'
                                    }, 
                                    'end': {
                                        '$max': '$date'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': None, 
                                    'kv': {
                                        '$push': {
                                            'k': '$_id', 
                                            'v': '$value'
                                        }
                                    }, 
                                    'start': {
                                        '$min': '$start'
                                    }, 
                                    'end': {
                                        '$max': '$end'
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0, 
                                    'data': {
                                        '$arrayToObject': '$kv'
                                    }, 
                                    'label': 'This Month', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$start', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$end', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ], 
                        'lastMonthTillDate': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$date', '$firstOfLastMonth'
                                                ]
                                            }, {
                                                '$lte': [
                                                    '$date', '$sameDayLastMonth'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }, {
                                '$unwind': '$dataArray'
                            }, {
                                '$group': {
                                    '_id': '$dataArray.k', 
                                    'value': {
                                        '$sum': '$dataArray.v'
                                    }, 
                                    'start': {
                                        '$min': '$date'
                                    }, 
                                    'end': {
                                        '$max': '$date'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': None, 
                                    'kv': {
                                        '$push': {
                                            'k': '$_id', 
                                            'v': '$value'
                                        }
                                    }, 
                                    'start': {
                                        '$min': '$start'
                                    }, 
                                    'end': {
                                        '$max': '$end'
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0, 
                                    'data': {
                                        '$arrayToObject': '$kv'
                                    }, 
                                    'label': 'Last Month Till Date', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$start', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$end', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ], 
                        'lastMonthComplete': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$date', '$firstOfLastMonth'
                                                ]
                                            }, {
                                                '$lte': [
                                                    '$date', '$endOfLastMonth'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }, {
                                '$unwind': '$dataArray'
                            }, {
                                '$group': {
                                    '_id': '$dataArray.k', 
                                    'value': {
                                        '$sum': '$dataArray.v'
                                    }, 
                                    'start': {
                                        '$min': '$date'
                                    }, 
                                    'end': {
                                        '$max': '$date'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': None, 
                                    'kv': {
                                        '$push': {
                                            'k': '$_id', 
                                            'v': '$value'
                                        }
                                    }, 
                                    'start': {
                                        '$min': '$start'
                                    }, 
                                    'end': {
                                        '$max': '$end'
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0, 
                                    'data': {
                                        '$arrayToObject': '$kv'
                                    }, 
                                    'label': 'Last Month (Complete)', 
                                    'dateSpan': {
                                        '$concat': [
                                            {
                                                '$dateToString': {
                                                    'date': '$start', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }, ' → ', {
                                                '$dateToString': {
                                                    'date': '$end', 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }, {
                    '$project': {
                        'results': {
                            '$concatArrays': [
                                '$last30Days', '$thisMonth', '$lastMonthTillDate', '$lastMonthComplete'
                            ]
                        }
                    }
                }, {
                    '$unwind': '$results'
                }, {
                    '$replaceRoot': {
                        'newRoot': '$results'
                    }
                }
            ], 
            'as': 'analytics'
        }
    }, {
        '$unwind': '$analytics'
    }, {
        '$replaceRoot': {
            'newRoot': '$analytics'
        }
    }
]
    from dzgroshared.db.extras import Analytics
    from dzgroshared.models.extras import Analytics as AnalyticsModel
    missingkeys = Analytics.addMissingFields("data")
    derivedmetrics = Analytics.addDerivedMetrics("data")
    pipeline.append(missingkeys)
    pipeline.extend(derivedmetrics)
    pipeline.append(AnalyticsModel.getProjectionStage('Period', req.collatetype))
    from dzgroshared.utils import mongo_pipeline_print
    mongo_pipeline_print.copy_pipeline(pipeline)
    return pipeline
