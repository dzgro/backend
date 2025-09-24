from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollateType
from dzgroshared.analytics import controller
from dzgroshared.db.model import PeriodDataRequest

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
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
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
                        'as': 'data'
                    }
                }
            ], 
            'as': 'data'
        }
    },
    {
        '$set': {
            'data': {
                '$map': {
                    'input': '$data', 
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

def pipeline(marketplace: ObjectId, req: PeriodDataRequest):
    pipeline: list[dict] = [{ '$match': { '_id': marketplace } }]
    pipeline.extend(getPeriodPerformance(req.collatetype, req.value))
    return pipeline