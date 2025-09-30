def pipeline():
    return [{
        '$group': {
            '_id': None, 
            'data': {
                '$push': '$$ROOT'
            }
        }
    }, {
        '$set': {
            'data': {
                '$reduce': {
                    'input': '$data', 
                    'initialValue': {
                        'cols': [], 
                        'rows': None
                    }, 
                    'in': {
                        '$mergeObjects': [
                            {
                                'cols': {
                                    '$concatArrays': [
                                        '$$value.cols', [
                                            {
                                                '$unsetField': {
                                                    'input': '$$this', 
                                                    'field': 'data'
                                                }
                                            }
                                        ]
                                    ]
                                }, 
                                'rows': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                {
                                                    '$ifNull': [
                                                        '$$value.rows', False
                                                    ]
                                                }, False
                                            ]
                                        }, 
                                        'then': {
                                            '$reduce': {
                                                'input': '$$this.data', 
                                                'initialValue': [], 
                                                'in': {
                                                    '$concatArrays': [
                                                        '$$value', [
                                                            {
                                                                'label': '$$this.label', 
                                                                'items': {
                                                                    '$reduce': {
                                                                        'input': '$$this.items', 
                                                                        'initialValue': [], 
                                                                        'in': {
                                                                            '$concatArrays': [
                                                                                '$$value', [
                                                                                    {
                                                                                        '$mergeObjects': [
                                                                                            {
                                                                                                'label': '$$this.label', 
                                                                                                'values': [
                                                                                                    {
                                                                                                        'value': '$$this.value', 
                                                                                                        'valueString': '$$this.valueString', 
                                                                                                        'growth': '$$this.growth', 
                                                                                                        'growing': '$$this.growing'
                                                                                                    }
                                                                                                ]
                                                                                            }, {
                                                                                                '$cond': {
                                                                                                    'if': {
                                                                                                        '$eq': [
                                                                                                            {
                                                                                                                '$ifNull': [
                                                                                                                    '$$this.items', False
                                                                                                                ]
                                                                                                            }, False
                                                                                                        ]
                                                                                                    }, 
                                                                                                    'then': {}, 
                                                                                                    'else': {
                                                                                                        'items': {
                                                                                                            '$reduce': {
                                                                                                                'input': '$$this.items', 
                                                                                                                'initialValue': [], 
                                                                                                                'in': {
                                                                                                                    '$concatArrays': [
                                                                                                                        '$$value', [
                                                                                                                            {
                                                                                                                                'label': '$$this.label', 
                                                                                                                                'values': [
                                                                                                                                    {
                                                                                                                                        'value': '$$this.value', 
                                                                                                                                        'valueString': '$$this.valueString', 
                                                                                                                                        'growth': '$$this.growth', 
                                                                                                                                        'growing': '$$this.growing'
                                                                                                                                    }
                                                                                                                                ]
                                                                                                                            }
                                                                                                                        ]
                                                                                                                    ]
                                                                                                                }
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            ]
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        ]
                                                    ]
                                                }
                                            }
                                        }, 
                                        'else': {
                                            '$let': {
                                                'vars': {
                                                    'items': {
                                                        '$reduce': {
                                                            'input': {
                                                                '$reduce': {
                                                                    'input': '$$this.data', 
                                                                    'initialValue': [], 
                                                                    'in': {
                                                                        '$concatArrays': [
                                                                            '$$value', '$$this.items'
                                                                        ]
                                                                    }
                                                                }
                                                            }, 
                                                            'initialValue': [], 
                                                            'in': {
                                                                '$concatArrays': [
                                                                    '$$value', [
                                                                        {
                                                                            'label': '$$this.label', 
                                                                            'value': {
                                                                                'value': '$$this.value', 
                                                                                'valueString': '$$this.valueString', 
                                                                                'growth': '$$this.growth', 
                                                                                'growing': '$$this.growing'
                                                                            }
                                                                        }
                                                                    ], {
                                                                        '$cond': {
                                                                            'if': {
                                                                                '$eq': [
                                                                                    {
                                                                                        '$ifNull': [
                                                                                            '$$this.items', False
                                                                                        ]
                                                                                    }, False
                                                                                ]
                                                                            }, 
                                                                            'then': [], 
                                                                            'else': {
                                                                                '$reduce': {
                                                                                    'input': '$$this.items', 
                                                                                    'initialValue': [], 
                                                                                    'in': {
                                                                                        '$concatArrays': [
                                                                                            '$$value', [
                                                                                                {
                                                                                                    'label': '$$this.label', 
                                                                                                    'value': {
                                                                                                        'value': '$$this.value', 
                                                                                                        'valueString': '$$this.valueString', 
                                                                                                        'growth': '$$this.growth', 
                                                                                                        'growing': '$$this.growing'
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
                                                }, 
                                                'in': {
                                                    '$map': {
                                                        'input': '$$value.rows', 
                                                        'as': 'r', 
                                                        'in': {
                                                            '$mergeObjects': [
                                                                {
                                                                    'label': '$$r.label'
                                                                }, {
                                                                    'items': {
                                                                        '$map': {
                                                                            'input': '$$r.items', 
                                                                            'as': 'i', 
                                                                            'in': {
                                                                                '$mergeObjects': [
                                                                                    '$$i', {
                                                                                        'values': {
                                                                                            '$concatArrays': [
                                                                                                '$$i.values', [
                                                                                                    {
                                                                                                        '$getField': {
                                                                                                            'input': {
                                                                                                                '$first': {
                                                                                                                    '$filter': {
                                                                                                                        'input': '$$items', 
                                                                                                                        'as': 'f', 
                                                                                                                        'cond': {
                                                                                                                            '$eq': [
                                                                                                                                '$$f.label', '$$i.label'
                                                                                                                            ]
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }, 
                                                                                                            'field': 'value'
                                                                                                        }
                                                                                                    }
                                                                                                ]
                                                                                            ]
                                                                                        }
                                                                                    }, {
                                                                                        '$cond': {
                                                                                            'if': {
                                                                                                '$eq': [
                                                                                                    {
                                                                                                        '$ifNull': [
                                                                                                            '$$i.items', False
                                                                                                        ]
                                                                                                    }, False
                                                                                                ]
                                                                                            }, 
                                                                                            'then': {}, 
                                                                                            'else': {
                                                                                                'items': {
                                                                                                    '$map': {
                                                                                                        'input': '$$i.items', 
                                                                                                        'as': 'i2', 
                                                                                                        'in': {
                                                                                                            '$mergeObjects': [
                                                                                                                '$$i2', {
                                                                                                                    'values': {
                                                                                                                        '$concatArrays': [
                                                                                                                            '$$i2.values', [
                                                                                                                                {
                                                                                                                                    '$getField': {
                                                                                                                                        'input': {
                                                                                                                                            '$first': {
                                                                                                                                                '$filter': {
                                                                                                                                                    'input': '$$items', 
                                                                                                                                                    'as': 'f', 
                                                                                                                                                    'cond': {
                                                                                                                                                        '$eq': [
                                                                                                                                                            '$$f.label', '$$i2.label'
                                                                                                                                                        ]
                                                                                                                                                    }
                                                                                                                                                }
                                                                                                                                            }
                                                                                                                                        }, 
                                                                                                                                        'field': 'value'
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            ]
                                                                                                                        ]
                                                                                                                    }
                                                                                                                }
                                                                                                            ]
                                                                                                        }
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
                                                            ]
                                                        }
                                                    }
                                                }
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
    }, {
        '$replaceRoot': {
            'newRoot': '$data'
        }
    }, {
        '$addFields': {
            'columns': {
                'columns1': {
            "$concatArrays": [
              [
                {
                    "header": "Metrics",
                    "colSpan": 1,
                    "rowSpan": 3,
                    "frozen": True
                  }
              ],
              {
              "$reduce": {
                "input": "$cols",
                "initialValue": [],
                "in": {
                  "$concatArrays": [
                    "$$value",
                    [
                      {
                        "header": "$$this.tag",
                        "colSpan": 2
                      }
                    ]
                  ]
                }
              }
            }]
          }, 
                'columns2': {
                    '$reduce': {
                        'input': '$cols', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', [
                                    {
                                        'header': {
                                            '$concat': [
                                                {
                                                    '$dateToString': {
                                                        'format': '%b %d, %Y', 
                                                        'date': '$$this.curr.startdate'
                                                    }
                                                }, ' - ', {
                                                    '$dateToString': {
                                                        'format': '%b %d, %Y', 
                                                        'date': '$$this.curr.enddate'
                                                    }
                                                }
                                            ]
                                        }
                                    }, {
                                        'header': {
                                            '$concat': [
                                                {
                                                    '$dateToString': {
                                                        'format': '%b %d, %Y', 
                                                        'date': '$$this.pre.startdate'
                                                    }
                                                }, ' - ', {
                                                    '$dateToString': {
                                                        'format': '%b %d, %Y', 
                                                        'date': '$$this.pre.enddate'
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            ]
                        }
                    }
                }, 
                'columns3': {
                    '$reduce': {
                        'input': '$cols', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', [
                                    {
                                        'header': 'Value'
                                    }, {
                                        'header': 'Growth'
                                    }
                                ]
                            ]
                        }
                    }
                }
            }
        }
    }, {
        '$project': {
            'cols': 0
        }
    }
]