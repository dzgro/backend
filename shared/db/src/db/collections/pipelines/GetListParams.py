from db.PipelineProcessor import PipelineProcessor

def execute(pp: PipelineProcessor):

    return [
    {
        '$match': {
            'uid': pp.uid, 
            '_id': pp.marketplace
        }
    }, 
    # {
    #     '$set': {
    #         'startDate': {
    #             '$dateFromString': {
    #                 'dateString': {
    #                     '$dateToString': {
    #                         'date': '$startDate', 
    #                         'timezone': timezone
    #                     }
    #                 }
    #             }
    #         }, 
    #         'endDate': {
    #             '$dateFromString': {
    #                 'dateString': {
    #                     '$dateToString': {
    #                         'date': '$endDate', 
    #                         'timezone': timezone
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # },
    {
        '$lookup': {
            'from': 'analytics_calculation', 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$eq': [
                                '$value', 'ad'
                            ]
                        }
                    }
                }, {
                    '$replaceWith': {
                        'items': '$items'
                    }
                }, {
                    '$unwind': '$items'
                }, {
                    '$replaceWith': '$items'
                }, {
                    '$project': {
                        'querygroup': 0
                    }
                }
            ], 
            'as': 'columns'
        }
    }, {
        '$set': {
            'minmaxDates': {
                'start': '$startdate', 
                'end': '$enddate'
            }
        }
    }, {
        '$set': {
            'querydates': {
                'pre': {
                    'start': {
                        '$dateSubtract': {
                            'startDate': '$enddate', 
                            'unit': 'day', 
                            'amount': 15
                        }
                    }, 
                    'end': {
                        '$dateSubtract': {
                            'startDate': '$enddate', 
                            'unit': 'day', 
                            'amount': 8
                        }
                    }
                }, 
                'curr': {
                    'start': {
                        '$dateSubtract': {
                            'startDate': '$enddate', 
                            'unit': 'day', 
                            'amount': 7
                        }
                    }, 
                    'end': '$enddate'
                }
            }
        }
    }, {
        '$project': {
            'columns': 1, 
            'minmaxDates': 1, 
            'querydates': 1, 
            '_id': 0
        }
    }, {
        '$set': {
            'columns': {
                '$reduce': {
                    'input': '$columns', 
                    'initialValue': [], 
                    'in': {
                        '$concatArrays': [
                            '$$value', {
                                '$let': {
                                    'vars': {
                                        'val': {
                                            '$replaceOne': {
                                                'input': '$$this.label', 
                                                'find': 'Ad ', 
                                                'replacement': ''
                                            }
                                        }, 
                                        'leftparenthesesPos': {
                                            '$indexOfBytes': [
                                                '$$this.label', '('
                                            ]
                                        }, 
                                        'rightparenthesesPos': {
                                            '$indexOfBytes': [
                                                '$$this.label', ')'
                                            ]
                                        }
                                    }, 
                                    'in': [
                                        {
                                            '$mergeObjects': [
                                                '$$this', {
                                                    'label': {
                                                        '$cond': [
                                                            {
                                                                '$eq': [
                                                                    '$$leftparenthesesPos', -1
                                                                ]
                                                            }, '$$val', {
                                                                '$substr': [
                                                                    '$$val', {
                                                                        '$sum': [
                                                                            '$$leftparenthesesPos', 1
                                                                        ]
                                                                    }, {
                                                                        '$subtract': [
                                                                            {
                                                                                '$subtract': [
                                                                                    '$$rightparenthesesPos', '$$leftparenthesesPos'
                                                                                ]
                                                                            }, 1
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                }
                                            ]
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
]