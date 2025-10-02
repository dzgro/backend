from bson import ObjectId
from dzgroshared.db.enums import CollectionType


def pipeline(marketplaceId: ObjectId):
        return [
    {
        '$match': {
            '_id': marketplaceId
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                'marketplace': '$_id', 
                'dates': '$dates'
            }
        }
    }, {
        '$lookup': {
            'from': 'performance_periods', 
            'localField': 'marketplace', 
            'foreignField': 'marketplace', 
            'as': 'tag'
        }
    }, {
        '$set': {
            'tag': {
                '$let': {
                    'vars': {
                        'tags': {
                            '$reduce': {
                                'input': [
                                    'Last 7 Days', 'Last 30 Days', 'This Month vs Last Month (Till Date)', 'This Month vs Last Month (Complete)'
                                ], 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                'tag': '$$this'
                                            }
                                        ]
                                    ]
                                }
                            }
                        }
                    }, 
                    'in': {
                        '$cond': {
                            'if': {
                                '$eq': [
                                    {
                                        '$size': '$tag'
                                    }, 0
                                ]
                            }, 
                            'then': '$$tags', 
                            'else': '$tag'
                        }
                    }
                }
            }
        }
    }, {
        '$unwind': {
            'path': '$tag'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    '$tag', {
                        '$unsetField': {
                            'input': '$$ROOT', 
                            'field': 'tag'
                        }
                    }
                ]
            }
        }
    }, {
        '$set': {
            'createdat': {
                '$cond': {
                    'if': {
                        '$in': [
                            '$tag', [
                                'Last 7 Days', 'Last 30 Days', 'This Month vs Last Month (Till Date)', 'This Month vs Last Month (Complete)'
                            ]
                        ]
                    }, 
                    'then': '$$NOW', 
                    'else': '$createdat'
                }
            }
        }
    }, {
        '$set': {
            'curr': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$eq': [
                                    '$tag', 'Last 7 Days'
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
                                    '$tag', 'Last 30 Days'
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
                                    '$tag', 'This Month vs Last Month (Till Date)'
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
                                    '$tag', 'This Month vs Last Month (Complete)'
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
                                    '$tag', 'Custom'
                                ]
                            }, 
                            'then': '$curr'
                        }
                    ], 
                    'default': '$curr'
                }
            }, 
            'pre': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$eq': [
                                    '$tag', 'Last 7 Days'
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
                                    '$tag', 'Last 30 Days'
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
                                    '$tag', 'This Month vs Last Month (Till Date)'
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
                                    '$tag', 'This Month vs Last Month (Complete)'
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
                                    '$tag', 'Custom'
                                ]
                            }, 
                            'then': '$pre'
                        }
                    ], 
                    'default': '$pre'
                }
            }
        }
    }, {
        '$match': {
            '$expr': {
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
    }, {
        '$project': {
            'dates': 0
        }
    }, {
        '$merge': CollectionType.PERFORMANCE_PERIODS
    }
]