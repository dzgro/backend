from bson import ObjectId
from dzgroshared.models.model import StartEndDate


def pipeline(marketplace:ObjectId, dates: StartEndDate|None=None):
    hasdates = dates is not None
    datesObj = dates.model_dump() if dates else None
    return [
    {
        '$match': {
            '_id': marketplace
        }
    },
    {
        '$set': {
            'dates': {
                '$cond': {
                    'if': hasdates,
                    'then': datesObj,
                    'else': "$dates"
                }
            }
        }
    },
    {
        '$lookup': {
            'from': 'queries', 
            'let': {
                'uid': '$uid', 
                'marketplace': '$marketplace'
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
                                    '$and': [
                                        {
                                            '$eq': [
                                                '$uid', '$$uid'
                                            ]
                                        }, {
                                            '$eq': [
                                                '$marketplace', '$$marketplace'
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            ], 
            'as': 'queries'
        }
    }, {
        '$unwind': '$queries'
    }, {
        '$project': {
            "_id": "$queries._id",
            'tag': '$queries.tag', 
            'dates': '$dates', 
            'curr': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$eq': [
                                    '$queries.tag', 'Last 7 Days'
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
                                    '$queries.tag', 'Last 30 Days'
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
                                    '$queries.tag', 'This Month vs Last Month (Till Date)'
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
                                    '$queries.tag', 'This Month vs Last Month (Complete)'
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
                                    '$queries.tag', 'Custom'
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
                                    '$queries.tag', 'Last 7 Days'
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
                                    '$queries.tag', 'Last 30 Days'
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
                                    '$queries.tag', 'This Month vs Last Month (Till Date)'
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
                                    '$queries.tag', 'This Month vs Last Month (Complete)'
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
                                    '$queries.tag', 'Custom'
                                ]
                            }, 
                            'then': '$queries.pre'
                        }
                    ], 
                    'default': '$dates'
                }
            }
        }
    }, {
        '$set': {
            'disabled': {
                '$not': {
                    '$and': [
                        {
                            '$gte': [
                                '$curr.startdate', '$dates.startdate'
                            ]
                        }, {
                            '$lte': [
                                '$curr.enddate', '$dates.enddate'
                            ]
                        }, {
                            '$gte': [
                                '$pre.startdate', '$dates.startdate'
                            ]
                        }, {
                            '$lte': [
                                '$pre.enddate', '$dates.enddate'
                            ]
                        }
                    ]
                }
            }
        }
    },
    {
        "$project": {
            "dates": 0
        }
    }
]