def execute(objectKey:str, datesKey: str):
    return {
        '$set': {
            objectKey: {
                '$let': {
                    'vars': {
                        'currData': {
                            '$filter': {
                                'input': f'${objectKey}', 
                                'as': 'f', 
                                'cond': {
                                    '$in': [
                                        '$$f.date', f'${datesKey}.curr'
                                    ]
                                }
                            }
                        }, 
                        'preData': {
                            '$filter': {
                                'input': f'${objectKey}', 
                                'as': 'f', 
                                'cond': {
                                    '$in': [
                                        '$$f.date', f'${datesKey}.pre'
                                    ]
                                }
                            }
                        }
                    }, 
                    'in': {
                        '$arrayToObject': {
                            '$reduce': {
                                'input': [
                                    {
                                        'key': 'sales', 
                                        'subkeys': [
                                            'revenue', 'tax', 'quantity', 'returnQuantity', 'netOrders', 'expenses'
                                        ]
                                    }, {
                                        'key': 'ad', 
                                        'subkeys': [
                                            'impressions', 'clicks', 'sales', 'cost', 'orders', 'units'
                                        ]
                                    }, {
                                        'key': 'traffic', 
                                        'subkeys': [
                                            'pageViews', 'sessions', 'unitSessions', 'buyBoxViews'
                                        ]
                                    }
                                ], 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', {
                                            '$let': {
                                                'vars': {
                                                    'key': '$$this.key'
                                                }, 
                                                'in': {
                                                    '$reduce': {
                                                        'input': '$$this.subkeys', 
                                                        'initialValue': [], 
                                                        'in': {
                                                            '$concatArrays': [
                                                                '$$value', {
                                                                    '$let': {
                                                                        'vars': {
                                                                            'subkey': '$$this'
                                                                        }, 
                                                                        'in': {
                                                                            '$let': {
                                                                                'vars': {
                                                                                    'currData': {
                                                                                        '$reduce': {
                                                                                            'input': '$$currData', 
                                                                                            'initialValue': 0, 
                                                                                            'in': {
                                                                                                '$sum': [
                                                                                                    '$$value', {
                                                                                                        '$ifNull': [
                                                                                                            {
                                                                                                                '$getField': {
                                                                                                                    'input': {
                                                                                                                        '$getField': {
                                                                                                                            'input': '$$this', 
                                                                                                                            'field': '$$key'
                                                                                                                        }
                                                                                                                    }, 
                                                                                                                    'field': '$$subkey'
                                                                                                                }
                                                                                                            }, 0
                                                                                                        ]
                                                                                                    }
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    }, 
                                                                                    'preData': {
                                                                                        '$reduce': {
                                                                                            'input': '$$preData', 
                                                                                            'initialValue': 0, 
                                                                                            'in': {
                                                                                                '$sum': [
                                                                                                    '$$value', {
                                                                                                        '$ifNull': [
                                                                                                            {
                                                                                                                '$getField': {
                                                                                                                    'input': {
                                                                                                                        '$getField': {
                                                                                                                            'input': '$$this', 
                                                                                                                            'field': '$$key'
                                                                                                                        }
                                                                                                                    }, 
                                                                                                                    'field': '$$subkey'
                                                                                                                }
                                                                                                            }, 0
                                                                                                        ]
                                                                                                    }
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }, 
                                                                                'in': {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$eq': [
                                                                                                {
                                                                                                    '$sum': [
                                                                                                        '$$currData', '$$preData'
                                                                                                    ]
                                                                                                }, 0
                                                                                            ]
                                                                                        }, [], [
                                                                                            {
                                                                                                'k': '$$subkey', 
                                                                                                'v': {
                                                                                                    'curr': '$$currData', 
                                                                                                    'pre': '$$preData'
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
                                                        }
                                                    }
                                                }
                                            }
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