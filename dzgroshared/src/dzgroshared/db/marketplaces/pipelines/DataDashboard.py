from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollateType
from dzgroshared.analytics import controller

def getPeriodPerformance(collatetype: CollateType, value: str|None):
    return [{
        '$lookup': {
            'from': 'performance_periods', 
            'let': {
                'marketplace': '$_id'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$or': [
                                {
                                    '$ne': [
                                        '$tag', 'Custom'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$lookup': {
                        'from': 'performance_period_results', 
                        'let': {
                            'queryid': '$_id', 
                            'collatetype': collatetype.value,
                            'value': value
                        }, 
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$marketplace', '$$marketplace'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$queryid', '$$queryid'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$collatetype', '$$collatetype'
                                                ]
                                            }, True if not value else {
                                                '$eq': [
                                                    '$value', '$$value'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }, {
                                '$project': {
                                    'data': 1, 
                                    '_id': 0
                                }
                            }
                        ], 
                        'as': 'performance'
                    }
                }
            ], 
            'as': 'performance'
        }
    },
    {
        '$set': {
            'performance': {
                '$map': {
                    'input': '$performance', 
                    'as': 'q', 
                    'in': {
                        '$let': {
                            'vars': {
                                'curr': {
                                    '$switch': {
                                        'branches': [
                                            {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'Last 7 Days'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateSubtract': {
                                                            'startDate': '$dates.enddate', 
                                                            'unit': 'day', 
                                                            'amount': 6
                                                        }
                                                    }, 
                                                    'enddate': '$dates.enddate'
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'Last 30 Days'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateSubtract': {
                                                            'startDate': '$dates.enddate', 
                                                            'unit': 'day', 
                                                            'amount': 29
                                                        }
                                                    }, 
                                                    'enddate': '$dates.enddate'
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'This Month vs Last Month (Till Date)'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateTrunc': {
                                                            'date': '$dates.enddate', 
                                                            'unit': 'month'
                                                        }
                                                    }, 
                                                    'enddate': '$dates.enddate'
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'This Month vs Last Month (Complete)'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateTrunc': {
                                                            'date': '$dates.enddate', 
                                                            'unit': 'month'
                                                        }
                                                    }, 
                                                    'enddate': '$dates.enddate'
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'Custom'
                                                    ]
                                                }, 
                                                'then': '$queries.curr'
                                            }
                                        ], 
                                        'default': '$dates'
                                    }
                                }, 
                                'pre': {
                                    '$switch': {
                                        'branches': [
                                            {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'Last 7 Days'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateSubtract': {
                                                            'startDate': '$dates.enddate', 
                                                            'unit': 'day', 
                                                            'amount': 13
                                                        }
                                                    }, 
                                                    'enddate': {
                                                        '$dateSubtract': {
                                                            'startDate': '$dates.enddate', 
                                                            'unit': 'day', 
                                                            'amount': 7
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'Last 30 Days'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateSubtract': {
                                                            'startDate': '$dates.enddate', 
                                                            'unit': 'day', 
                                                            'amount': 59
                                                        }
                                                    }, 
                                                    'enddate': {
                                                        '$dateSubtract': {
                                                            'startDate': '$dates.enddate', 
                                                            'unit': 'day', 
                                                            'amount': 30
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'This Month vs Last Month (Till Date)'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateTrunc': {
                                                            'date': {
                                                                '$dateSubtract': {
                                                                    'startDate': '$dates.enddate', 
                                                                    'unit': 'month', 
                                                                    'amount': 1
                                                                }
                                                            }, 
                                                            'unit': 'month'
                                                        }
                                                    }, 
                                                    'enddate': {
                                                        '$dateSubtract': {
                                                            'startDate': {
                                                                '$dateTrunc': {
                                                                    'date': '$dates.enddate', 
                                                                    'unit': 'month'
                                                                }
                                                            }, 
                                                            'unit': 'day', 
                                                            'amount': 1
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'This Month vs Last Month (Complete)'
                                                    ]
                                                }, 
                                                'then': {
                                                    'startdate': {
                                                        '$dateTrunc': {
                                                            'date': {
                                                                '$dateSubtract': {
                                                                    'startDate': '$dates.enddate', 
                                                                    'unit': 'month', 
                                                                    'amount': 1
                                                                }
                                                            }, 
                                                            'unit': 'month'
                                                        }
                                                    }, 
                                                    'enddate': {
                                                        '$dateSubtract': {
                                                            'startDate': {
                                                                '$dateTrunc': {
                                                                    'date': '$dates.enddate', 
                                                                    'unit': 'month'
                                                                }
                                                            }, 
                                                            'unit': 'day', 
                                                            'amount': 1
                                                        }
                                                    }
                                                }
                                            }, {
                                                'case': {
                                                    '$eq': [
                                                        '$$q.tag', 'Custom'
                                                    ]
                                                }, 
                                                'then': '$$q.pre'
                                            }
                                        ], 
                                        'default': '$dates'
                                    }
                                }
                            }, 
                            'in': {
                                'data': {
                                    '$first': '$$q.performance.data'
                                }, 
                                'tag': '$$q.tag', 
                                'curr': '$$curr', 
                                'pre': '$$pre', 
                                'disabled': {
                                    '$not': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$$curr.startdate', '$dates.startdate'
                                                ]
                                            }, {
                                                '$lte': [
                                                    '$$curr.enddate', '$dates.enddate'
                                                ]
                                            }, {
                                                '$gte': [
                                                    '$$pre.startdate', '$dates.startdate'
                                                ]
                                            }, {
                                                '$lte': [
                                                    '$$pre.enddate', '$dates.enddate'
                                                ]
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
    }]

def addAllDatesData(collatetype: CollateType, value: str|None):
    
    pipeline = [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$eq': [
                                        '$collatetype', '$$collatetype'
                                    ]
                                },
                                True if not value else {
                                    '$eq': [
                                        '$value', '$$value'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'date': 1, 
                        'data': 1, 
                        '_id': 0
                    }
                },
                controller.addMissingFields()
            ]
    return {
        '$lookup': {
            'from': 'date_analytics', 
            'let': {
                'marketplace': '$_id', 
                'collatetype': collatetype.value,
                'value': value
            }, 
            'pipeline': pipeline, 
            'as': 'all_dates_data'
        }
    }

def addStatesData(pp: PipelineProcessor, collatetype: CollateType, value: str|None):
    
    pipeline = [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$eq': [
                                        '$collatetype', '$$collatetype'
                                    ]
                                },
                                True if not value else {
                                    '$eq': [
                                        '$value', '$$value'
                                    ]
                                },
                                {
                                    '$in': [
                                        "$date", "$$dates"
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'date': 1, 
                        'data': 1, 
                        'state': 1,
                        '_id': 0
                    }
                },
                {
                    '$group': {
                        '_id': '$state',
                        'data': {
                            '$push': '$data'
                        }
                    }
                },
                pp.collateData(),
                {
                    "$replaceRoot": {
                        "newRoot": { 'state': '$_id', 'data': '$data' }
                    }
                },
                controller.addMissingFields(),
            ]
    pipeline.extend(controller.addDerivedMetrics())
    pipeline.append({"$sort": {"data.netrevenue": -1}})
    return {
        '$lookup': {
            'from': 'state_analytics', 
            'let': {
                'marketplace': '$_id', 
                'collatetype': collatetype.value,
                'value': value,
                'dates': {
                    "$reduce": {
                        "input": { "$slice": ["$all_dates_data", {"$subtract": [{"$size": "$all_dates_data"},30]}, 30] },
                        "initialValue": [],
                        "in": {
                            "$concatArrays": ["$$value", ["$$this.date"]]
                        }
                    }
                }
            }, 
            'pipeline': pipeline, 
            'as': 'states'
        }
    }


def setMonths(pp: PipelineProcessor):
    return [
        {
        '$addFields': {
            'months': {
                '$reduce': {
                    'input': {
                        '$range': [
                            0, {
                                '$add': [
                                    {
                                        '$multiply': [
                                            {
                                                '$subtract': [
                                                    {
                                                        '$year': '$dates.enddate'
                                                    }, {
                                                        '$year': '$dates.startdate'
                                                    }
                                                ]
                                            }, 12
                                        ]
                                    }, {
                                        '$subtract': [
                                            {
                                                '$month': '$dates.enddate'
                                            }, {
                                                '$month': '$dates.startdate'
                                            }
                                        ]
                                    }, 1
                                ]
                            }
                        ]
                    }, 
                    'initialValue': [], 
                    'in': {
                        '$concatArrays': [
                            '$$value', [
                                {
                                    '$let': {
                                        'vars': {
                                            'currentMonth': {
                                                '$add': [
                                                    {
                                                        '$month': '$dates.startdate'
                                                    }, '$$this'
                                                ]
                                            }, 
                                            'currentYear': {
                                                '$add': [
                                                    {
                                                        '$year': '$dates.startdate'
                                                    }, {
                                                        '$floor': {
                                                            '$divide': [
                                                                {
                                                                    '$add': [
                                                                        {
                                                                            '$month': '$dates.startdate'
                                                                        }, '$$this', -1
                                                                    ]
                                                                }, 12
                                                            ]
                                                        }
                                                    }
                                                ]
                                            }
                                        }, 
                                        'in': {
                                            '$let': {
                                                'vars': {
                                                    'adjustedMonth': {
                                                        '$cond': [
                                                            {
                                                                '$gt': [
                                                                    '$$currentMonth', 12
                                                                ]
                                                            }, {
                                                                '$subtract': [
                                                                    '$$currentMonth', 12
                                                                ]
                                                            }, '$$currentMonth'
                                                        ]
                                                    }, 
                                                    'adjustedYear': {
                                                        '$cond': [
                                                            {
                                                                '$gt': [
                                                                    '$$currentMonth', 12
                                                                ]
                                                            }, {
                                                                '$add': [
                                                                    '$$currentYear', 1
                                                                ]
                                                            }, '$$currentYear'
                                                        ]
                                                    }
                                                }, 
                                                'in': {
                                                    '$let': {
                                                        'vars': {
                                                            'firstDayOfMonth': {
                                                                '$dateFromParts': {
                                                                    'year': '$$adjustedYear', 
                                                                    'month': '$$adjustedMonth', 
                                                                    'day': 1
                                                                }
                                                            }, 
                                                            'lastDayOfMonth': {
                                                                '$dateSubtract': {
                                                                    'startDate': {
                                                                        '$dateAdd': {
                                                                            'startDate': {
                                                                                '$dateFromParts': {
                                                                                    'year': '$$adjustedYear', 
                                                                                    'month': '$$adjustedMonth', 
                                                                                    'day': 1
                                                                                }
                                                                            }, 
                                                                            'unit': 'month', 
                                                                            'amount': 1
                                                                        }
                                                                    }, 
                                                                    'unit': 'day', 
                                                                    'amount': 1
                                                                }
                                                            }
                                                        }, 
                                                        'in': {
                                                            '$let': {
                                                                'vars': {
                                                                    'rangeStart': {
                                                                        '$max': [
                                                                            '$$firstDayOfMonth', '$dates.startdate'
                                                                        ]
                                                                    }, 
                                                                    'rangeEnd': {
                                                                        '$min': [
                                                                            '$$lastDayOfMonth', '$dates.enddate'
                                                                        ]
                                                                    }
                                                                }, 
                                                                'in': {
                                                                    'month': {
                                                                        '$dateToString': {
                                                                            'format': '%b %Y', 
                                                                            'date': '$$firstDayOfMonth'
                                                                        }
                                                                    }, 
                                                                    'period': {
                                                                        '$concat': [
                                                                            {
                                                                                '$dateToString': {
                                                                                    'format': '%d %b', 
                                                                                    'date': '$$rangeStart'
                                                                                }
                                                                            }, ' - ', {
                                                                                '$dateToString': {
                                                                                    'format': '%d %b', 
                                                                                    'date': '$$rangeEnd'
                                                                                }
                                                                            }
                                                                        ]
                                                                    }, 
                                                                    'startdate': '$$rangeStart', 
                                                                    'enddate': '$$rangeEnd'
                                                                }
                                                            }
                                                        }
                                                    }
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
    }, {
        '$set': {
            'months': {
                '$map': {
                    'input': '$months', 
                    'as': 'm', 
                    'in': {
                        '$mergeObjects': [
                            '$$m', {
                                '$let': {
                                    'vars': {
                                        'data': {
                                            '$map': {
                                                'input': {
                                                    '$filter': {
                                                        'input': '$all_dates_data', 
                                                        'as': 'd', 
                                                        'cond': {
                                                            '$and': [
                                                                {
                                                                    '$gte': [
                                                                        '$$d.date', '$$m.startdate'
                                                                    ]
                                                                }, {
                                                                    '$lte': [
                                                                        '$$d.date', '$$m.enddate'
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    }
                                                }, 
                                                'as': 'f', 
                                                'in': '$$f.data'
                                            }
                                        }
                                    }, 
                                    'in': {
                                        'data': pp.getCollateDataReduceDef("$data")
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    },
    {
        '$set': {
            'months': {
                '$map': {
                    'input': '$months', 
                    'as': 'item', 
                    'in': {
                        '$mergeObjects': [
                            '$$item', 
                            controller.getDerivedMetricsMapExpression()
                        ]
                    }
                }
            }
        }
    }
]

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
                                    }, 
                                    'data': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$all_dates_data', 
                                                    'cond': {
                                                        '$and': [
                                                            {
                                                                '$gte': [
                                                                    '$$this.date', '$$thirtyDaysAgo'
                                                                ]
                                                            }, {
                                                                '$lte': [
                                                                    '$$this.date', '$$enddate'
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'in': '$$this.data'
                                        }
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
                                    }, 
                                    'data': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$all_dates_data', 
                                                    'cond': {
                                                        '$and': [
                                                            {
                                                                '$gte': [
                                                                    '$$this.date', '$$firstOfThisMonth'
                                                                ]
                                                            }, {
                                                                '$lte': [
                                                                    '$$this.date', '$$enddate'
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'in': '$$this.data'
                                        }
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
                                    }, 
                                    'data': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$all_dates_data', 
                                                    'cond': {
                                                        '$and': [
                                                            {
                                                                '$gte': [
                                                                    '$$this.date', '$$firstOfLastMonth'
                                                                ]
                                                            }, {
                                                                '$lte': [
                                                                    '$$this.date', '$$sameDayLastMonth'
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'in': '$$this.data'
                                        }
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
                                    }, 
                                    'data': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$all_dates_data', 
                                                    'cond': {
                                                        '$and': [
                                                            {
                                                                '$gte': [
                                                                    '$$this.date', '$$firstOfLastMonth'
                                                                ]
                                                            }, {
                                                                '$lte': [
                                                                    '$$this.date', '$$endOfLastMonth'
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'in': '$$this.data'
                                        }
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
        "$set": {
            "periods": {
                "$map": {
                    "input": "$periods",
                    "as": "p",
                    "in": {
                        "$mergeObjects": [
                            "$$p",
                            {"data": pp.getCollateDataReduceDef("$p.data")}
                        ]
                    }
                }
            }
        }
    }]

def addKeyMetrics(keys: list[str]):
    return { "$set": {
  "keys": {
    "$let": {
      "vars": {
        "dates": {
          "$slice": ["$all_dates_data", {"$subtract": [{"$size": "$all_dates_data"},30]}, 30]
        }
      },
      "in": {
    "$reduce": {
      "input": keys,
      "initialValue": [],
      "in": {
        "$let": {
          "vars": {
            "key": "$$this"
          },
          "in": {
        "$concatArrays": [
          "$$value",
          [
            {
              "key": "$$key",
              "data": {
                "last30Days": {
                  "$reduce": {
                    "input": "$$dates",
                    "initialValue": [],
                    "in": {
                      "$concatArrays": [
                        "$$value",
                        [{
                              "$ifNull": [
                                {
                          "$getField": {
                            "input": "$$this.data",
                            "field": "$$key"
                          }
                        },0
                              ]
                            }]
                      ]
                    }
                  }
                },
                "perioddata": {
                  "$reduce": {
                    "input": "$periods",
                    "initialValue": [],
                    "in": {
                      "$concatArrays": [
                        "$$value",
                        [
                          {
                            "label": "$$this.label",
                            "value": {
                              "$ifNull": [
                                {
                          "$getField": {
                            "input": "$$this.data",
                            "field": "$$key"
                          }
                        },0
                              ]
                            }
                          }
                        ]
                      ]
                    }
                  }
                },
                "months": {
                  "$reduce": {
                    "input": "$months",
                    "initialValue": [],
                    "in": {
                      "$concatArrays": [
                        "$$value",
                        [
                          {
                            "label": "$$this.month",
                            "value": {
                              "$ifNull": [
                                {
                          "$getField": {
                            "input": "$$this.data",
                            "field": "$$key"
                          }
                        },0
                              ]
                            }
                          }
                        ]
                      ]
                    }
                  }
                },
                "performance": {
                  "$reduce": {
                    "input": "$performance",
                    "initialValue": [],
                    "in": {
                      "$concatArrays": [
                        "$$value",
                        [
                          {
                            "label": "$$this.tag",
                            "value": {
                              "$ifNull": [
                                {
                          "$getField": {
                            "input": "$$this.data",
                            "field": "$$key"
                          }
                        },0
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

def pipeline(pp: PipelineProcessor,marketplace: ObjectId, collatetype: CollateType, value: str|None, keys: list[str]):
    pipeline: list[dict] = [{ '$match': { '_id': marketplace } }]
    pipeline.extend(getPeriodPerformance(collatetype, value))
    pipeline.append(addAllDatesData(collatetype, value))
    pipeline.extend(setMonths(pp))
    pipeline.extend(addPeriodData(pp))
    pipeline.append(addKeyMetrics(keys))
    pipeline.append(addStatesData(pp, collatetype, value))
    pipeline.append(pp.project(["states", "months", "periods", "keys", "performance"]))
    return pipeline