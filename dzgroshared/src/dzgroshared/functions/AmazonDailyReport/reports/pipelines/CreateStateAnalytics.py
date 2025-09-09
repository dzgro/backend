from bson import ObjectId
from dzgroshared.models.model import StartEndDate


def pipeline(uid:str, marketplace: ObjectId, dates: StartEndDate):
    setdates = dates.model_dump()
    return [
    {
        '$match': {
            '_id': marketplace, 
            'uid': uid
        }
    }, {
        '$set': {
            'dates': setdates
        }
    }, {
        '$set': {
            'date': {
                '$map': {
                    'input': {
                        '$range': [
                            0, {
                                '$sum': [
                                    {
                                        '$dateDiff': {
                                            'startDate': '$dates.startdate', 
                                            'endDate': '$dates.enddate', 
                                            'unit': 'day'
                                        }
                                    }, 1
                                ]
                            }, 1
                        ]
                    }, 
                    'as': 'day', 
                    'in': {
                        '$dateAdd': {
                            'startDate': '$dates.startdate', 
                            'unit': 'day', 
                            'amount': '$$day'
                        }
                    }
                }
            }
        }
    }, {
        '$unwind': '$date'
    }, {
        '$lookup': {
            'from': 'orders', 
            'let': {
                'marketplace': '$_id', 
                'date': '$date'
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
                                        '$date', '$$date'
                                    ]
                                },
                            ]
                        }
                    }
                }, {
                    '$lookup': {
                        'from': 'settlements', 
                        'let': {
                            'marketplace': '$marketplace', 
                            'orderid': '$orderid'
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
                                                    '$orderid', '$$orderid'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        ], 
                        'as': 'settlement'
                    }
                }, {
                    '$lookup': {
                        'from': 'order_items', 
                        'localField': '_id', 
                        'foreignField': 'order', 
                        'pipeline': [
                            {
                                '$lookup': {
                                    'from': 'products', 
                                    'let': {
                                        'marketplace': '$marketplace', 
                                        'sku': '$sku'
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
                                                                '$sku', '$$sku'
                                                            ]
                                                        }
                                                    ]
                                                }
                                            }
                                        }, {
                                            '$project': {
                                                'parent': '$parentsku', 
                                                'category': '$producttype', 
                                                '_id': 0
                                            }
                                        }
                                    ], 
                                    'as': 'product'
                                }
                            }, {
                                '$set': {
                                    'parentsku': {
                                        '$first': '$product.parent'
                                    }, 
                                    'category': {
                                        '$first': '$product.category'
                                    }
                                }
                            }, {
                                '$project': {
                                    'product': 0
                                }
                            }
                        ], 
                        'as': 'orderitem'
                    }
                }, {
                    '$set': {
                        'orderValue': {
                            '$reduce': {
                                'input': '$orderitem', 
                                'initialValue': 0, 
                                'in': {
                                    '$sum': [
                                        '$$value', '$$this.revenue'
                                    ]
                                }
                            }
                        }
                    }
                }, {
                    '$set': {
                        'orderitem': {
                            '$map': {
                                'input': '$orderitem', 
                                'as': 'oi', 
                                'in': {
                                    '$mergeObjects': [
                                        '$$oi', {
                                            '$let': {
                                                'vars': {
                                                    'skuvalues': {
                                                        '$reduce': {
                                                            'input': {
                                                                '$filter': {
                                                                    'input': '$settlement', 
                                                                    'as': 's', 
                                                                    'cond': {
                                                                        '$and': [
                                                                            {
                                                                                '$eq': [
                                                                                    '$$s.amounttype', 'ItemPrice'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$s.sku', '$$oi.sku'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$s.transactiontype', 'Refund'
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            }, 
                                                            'initialValue': {
                                                                'returnvalue': 0, 
                                                                'returntax': 0
                                                            }, 
                                                            'in': {
                                                                '$mergeObjects': [
                                                                    '$$value', {
                                                                        'returnvalue': {
                                                                            '$sum': [
                                                                                '$$value.returnvalue', '$$this.amount'
                                                                            ]
                                                                        }
                                                                    }, {
                                                                        '$cond': {
                                                                            'if': {
                                                                                '$eq': [
                                                                                    '$$this.amountdescription', 'Principal'
                                                                                ]
                                                                            }, 
                                                                            'then': {}, 
                                                                            'else': {
                                                                                'returntax': {
                                                                                    '$sum': [
                                                                                        '$$value.returntax', '$$this.amount'
                                                                                    ]
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
                                                    '$mergeObjects': [
                                                        '$$skuvalues', {
                                                            'skuratio': {
                                                                '$cond': {
                                                                    'if': {
                                                                        '$eq': [
                                                                            '$orderValue', 0
                                                                        ]
                                                                    }, 
                                                                    'then': 0, 
                                                                    'else': {
                                                                        '$divide': [
                                                                            '$$oi.revenue', '$orderValue'
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }, {
                    '$set': {
                        'orderitem': {
                            '$map': {
                                'input': '$orderitem', 
                                'as': 'oi', 
                                'in': {
                                    '$mergeObjects': [
                                        '$$oi', {
                                            '$let': {
                                                'vars': {
                                                    'settlements': {
                                                        '$filter': {
                                                            'input': '$settlement', 
                                                            'as': 's', 
                                                            'cond': {
                                                                '$and': [
                                                                    {
                                                                        '$not': {
                                                                            '$in': [
                                                                                '$$s.amounttype', [
                                                                                    'ItemPrice', 'ItemTax'
                                                                                ]
                                                                            ]
                                                                        }
                                                                    }, {
                                                                        '$or': [
                                                                            {
                                                                                '$eq': [
                                                                                    {
                                                                                        '$ifNull': [
                                                                                            '$$s.sku', None
                                                                                        ]
                                                                                    }, None
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$s.sku', '$$oi.sku'
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }, 
                                                'in': {
                                                    '$reduce': {
                                                        'input': '$$settlements', 
                                                        'initialValue': {
                                                            'fees': 0, 
                                                            'otherexpenses': 0
                                                        }, 
                                                        'in': {
                                                            '$mergeObjects': [
                                                                '$$value', {
                                                                    '$cond': {
                                                                        'if': {
                                                                            '$ifNull': [
                                                                                '$$this.sku', False
                                                                            ]
                                                                        }, 
                                                                        'then': {
                                                                            'otherexpenses': {
                                                                                '$sum': [
                                                                                    '$$value.otherexpenses', '$$this.amount'
                                                                                ]
                                                                            }
                                                                        }, 
                                                                        'else': {
                                                                            'fees': {
                                                                                '$sum': [
                                                                                    '$$value.fees', '$$this.amount'
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
                                    ]
                                }
                            }
                        }
                    }
                }, {
                    '$set': {
                        'orderitem': {
                            '$map': {
                                'input': '$orderitem', 
                                'as': 'oi', 
                                'in': {
                                    '$mergeObjects': [
                                        '$$oi', {
                                            'orders': 1, 
                                            'cancelledorders': {
                                                '$cond': {
                                                    'if': {
                                                        '$eq': [
                                                            '$orderstatus', 'Cancelled'
                                                        ]
                                                    }, 
                                                    'then': 1, 
                                                    'else': 0
                                                }
                                            }, 
                                            'otherexpenses': {
                                                '$round': [
                                                    {
                                                        '$multiply': [
                                                            '$$oi.otherexpenses', '$$oi.skuratio'
                                                        ]
                                                    }, 2
                                                ]
                                            }, 
                                            'quantity': '$$oi.quantity', 
                                            'returnquantity': {
                                                '$cond': {
                                                    'if': {
                                                        '$eq': [
                                                            '$$oi.revenue', 0
                                                        ]
                                                    }, 
                                                    'then': 0, 
                                                    'else': {
                                                        '$round': [
                                                            {
                                                                '$multiply': [
                                                                    '$$oi.quantity', {
                                                                        '$divide': [
                                                                            {
                                                                                '$abs': '$$oi.returnvalue'
                                                                            }, '$$oi.revenue'
                                                                        ]
                                                                    }
                                                                ]
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
                }, {
                    '$set': {
                        'orderitem': {
                            '$map': {
                                'input': '$orderitem', 
                                'as': 'oi', 
                                'in': {
                                    '$mergeObjects': [
                                        '$$oi', {
                                            'fbaorders': 0, 
                                            'fbacancelledorders': 0, 
                                            'fbarevenue': 0, 
                                            'fbatax': 0, 
                                            'fbareturntax': 0, 
                                            'fbareturnvalue': 0, 
                                            'fbaquantity': 0, 
                                            'fbareturnquantity': 0, 
                                            'fbafees': 0, 
                                            'fbaotherexpenses': 0, 
                                            'fbanetproceeds': 0, 
                                            'fbmorders': 0, 
                                            'fbmcancelledorders': 0, 
                                            'fbmrevenue': 0, 
                                            'fbmtax': 0, 
                                            'fbareturntax': 0, 
                                            'fbmreturnvalue': 0, 
                                            'fbmquantity': 0, 
                                            'fbmreturnquantity': 0, 
                                            'fbmfees': 0, 
                                            'fbmotherexpenses': 0, 
                                            'fbmnetproceeds': 0
                                        }, {
                                            '$let': {
                                                'vars': {
                                                    'netproceeds': {
                                                        '$cond': {
                                                            'if': {
                                                                '$eq': [
                                                                    {
                                                                        '$size': '$settlement'
                                                                    }, 0
                                                                ]
                                                            }, 
                                                            'then': 0, 
                                                            'else': {
                                                                '$add': [
                                                                    '$$oi.revenue', '$$oi.returnvalue', '$$oi.fees', '$$oi.otherexpenses'
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }, 
                                                'in': {
                                                    '$mergeObjects': [
                                                        {
                                                            'netproceeds': '$$netproceeds'
                                                        }, {
                                                            '$cond': {
                                                                'if': {
                                                                    '$ne': [
                                                                        '$fulfillment', 'Merchant'
                                                                    ]
                                                                }, 
                                                                'then': {
                                                                    'fbarevenue': '$$oi.revenue', 
                                                                    'fbatax': '$$oi.tax', 
                                                                    'fbareturntax': '$$oi.returntax', 
                                                                    'fbaorders': '$$oi.orders', 
                                                                    'fbacancelledorders': '$$oi.cancelledorders', 
                                                                    'fbareturnvalue': '$$oi.returnvalue', 
                                                                    'fbaquantity': '$$oi.quantity', 
                                                                    'fbareturnquantity': '$$oi.returnquantity', 
                                                                    'fbafees': '$$oi.fees', 
                                                                    'fbaotherexpenses': '$$oi.otherexpenses', 
                                                                    'fbanetproceeds': '$$netproceeds'
                                                                }, 
                                                                'else': {
                                                                    'fbmrevenue': '$$oi.revenue', 
                                                                    'fbmreturntax': '$$oi.returntax', 
                                                                    'fbmtax': '$$oi.tax', 
                                                                    'fbmorders': '$$oi.orders', 
                                                                    'fbmcancelledorders': '$$oi.cancelledorders', 
                                                                    'fbmreturnvalue': '$$oi.returnvalue', 
                                                                    'fbmquantity': '$$oi.quantity', 
                                                                    'fbmreturnquantity': '$$oi.returnquantity', 
                                                                    'fbmfees': '$$oi.fees', 
                                                                    'fbmotherexpenses': '$$oi.otherexpenses', 
                                                                    'fbmnetproceeds': '$$netproceeds'
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }, {
                    '$set': {
                        'orderitem': {
                            '$map': {
                                'input': '$orderitem', 
                                'as': 'oi', 
                                'in': {
                                    'value': '$$oi.sku', 
                                    'parent': '$$oi.asin', 
                                    'parentsku': '$$oi.parentsku', 
                                    'category': '$$oi.category', 
                                    'collatetype': 'sku', 
                                    'data': {
                                        'fbanetproceeds': '$$oi.fbanetproceeds', 
                                        'fbmnetproceeds': '$$oi.fmanetproceeds', 
                                        'fbarevenue': '$$oi.fbarevenue', 
                                        'fbmrevenue': '$$oi.fbmrevenue', 
                                        'fbareturntax': '$$oi.fbareturntax', 
                                        'fbmreturntax': '$$oi.fbmreturntax', 
                                        'fbatax': '$$oi.fbatax', 
                                        'fbmtax': '$$oi.fbmtax', 
                                        'fbaorders': '$$oi.fbaorders', 
                                        'fbmorders': '$$oi.fbmorders', 
                                        'fbacancelledorders': '$$oi.fbacancelledorders', 
                                        'fbmcancelledorders': '$$oi.fbmcancelledorders', 
                                        'fbareturnvalue': '$$oi.fbareturnvalue', 
                                        'fbmreturnvalue': '$$oi.fbmreturnvalue', 
                                        'fbaquantity': '$$oi.fbaquantity', 
                                        'fbmquantity': '$$oi.fbmquantity', 
                                        'fbareturnquantity': '$$oi.fbareturnquantity', 
                                        'fbmreturnquantity': '$$oi.fbmreturnquantity', 
                                        'fbafees': '$$oi.fbafees', 
                                        'fbmfees': '$$oi.fbmfees', 
                                        'fbaotherexpenses': '$$oi.fbaotherexpenses', 
                                        'fbmotherexpenses': '$$oi.fbmotherexpenses'
                                    }
                                }
                            }
                        }
                    }
                }, {
                    '$project': {
                        'orderitem': 1, 
                        'state': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'order'
        }
    }, {
        '$set': {
            'order': {
                '$reduce': {
                    'input': '$order', 
                    'initialValue': [], 
                    'in': {
                        '$let': {
                            'vars': {
                                'idx': {
                                    '$indexOfArray': [
                                        '$$value.state', '$$this.state'
                                    ]
                                }
                            }, 
                            'in': {
                                '$cond': {
                                    'if': {
                                        '$eq': [
                                            '$$idx', -1
                                        ]
                                    }, 
                                    'then': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this'
                                            ]
                                        ]
                                    }, 
                                    'else': {
                                        '$map': {
                                            'input': '$$value', 
                                            'as': 'v', 
                                            'in': {
                                                '$cond': {
                                                    'if': {
                                                        '$ne': [
                                                            '$$v.state', '$$this.state'
                                                        ]
                                                    }, 
                                                    'then': '$$v', 
                                                    'else': {
                                                        '$mergeObjects': [
                                                            '$$v', {
                                                                'orderitem': {
                                                                    '$concatArrays': [
                                                                        '$$v.orderitem', '$$this.orderitem'
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
                            }
                        }
                    }
                }
            }
        }
    }, {
        '$set': {
            'order': {
                '$map': {
                    'input': '$order', 
                    'as': 'order', 
                    'in': {
                        '$mergeObjects': [
                            '$$order', {
                                'orderitem': {
                                    '$map': {
                                        'input': {
                                            '$reduce': {
                                                'input': '$$order.orderitem', 
                                                'initialValue': [], 
                                                'in': {
                                                    '$let': {
                                                        'vars': {
                                                            'thisItem': '$$this', 
                                                            'dataDoc': {
                                                                '$cond': [
                                                                    {
                                                                        '$eq': [
                                                                            {
                                                                                '$type': '$$this.data'
                                                                            }, 'object'
                                                                        ]
                                                                    }, '$$this.data', {}
                                                                ]
                                                            }, 
                                                            'existing': {
                                                                '$first': {
                                                                    '$filter': {
                                                                        'input': '$$value', 
                                                                        'as': 'g', 
                                                                        'cond': {
                                                                            '$eq': [
                                                                                '$$g.value', '$$this.value'
                                                                            ]
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'in': {
                                                            '$cond': [
                                                                {
                                                                    '$ifNull': [
                                                                        '$$existing', False
                                                                    ]
                                                                }, {
                                                                    '$map': {
                                                                        'input': '$$value', 
                                                                        'as': 'g', 
                                                                        'in': {
                                                                            '$cond': [
                                                                                {
                                                                                    '$eq': [
                                                                                        '$$g.value', '$$thisItem.value'
                                                                                    ]
                                                                                }, {
                                                                                    '$mergeObjects': [
                                                                                        '$$g', {
                                                                                            'data': {
                                                                                                '$reduce': {
                                                                                                    'input': {
                                                                                                        '$objectToArray': '$$dataDoc'
                                                                                                    }, 
                                                                                                    'initialValue': '$$g.data', 
                                                                                                    'in': {
                                                                                                        '$let': {
                                                                                                            'vars': {
                                                                                                                'key': '$$this.k', 
                                                                                                                'addVal': '$$this.v', 
                                                                                                                'prev': {
                                                                                                                    '$ifNull': [
                                                                                                                        {
                                                                                                                            '$getField': {
                                                                                                                                'field': '$$this.k', 
                                                                                                                                'input': '$$value'
                                                                                                                            }
                                                                                                                        }, 0
                                                                                                                    ]
                                                                                                                }
                                                                                                            }, 
                                                                                                            'in': {
                                                                                                                '$mergeObjects': [
                                                                                                                    '$$value', {
                                                                                                                        '$arrayToObject': [
                                                                                                                            [
                                                                                                                                {
                                                                                                                                    'k': '$$key', 
                                                                                                                                    'v': {
                                                                                                                                        '$add': [
                                                                                                                                            '$$prev', '$$addVal'
                                                                                                                                        ]
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            ]
                                                                                                                        ]
                                                                                                                    }
                                                                                                                ]
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    ]
                                                                                }, '$$g'
                                                                            ]
                                                                        }
                                                                    }
                                                                }, {
                                                                    '$concatArrays': [
                                                                        '$$value', [
                                                                            '$$thisItem'
                                                                        ]
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    }
                                                }
                                            }
                                        }, 
                                        'as': 'g', 
                                        'in': '$$g'
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$unwind': {
            'path': '$order', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    {
                        'marketplace': '$_id', 
                        'date': '$date'
                    }, '$order'
                ]
            }
        }
    }, {
        '$set': {
            'orderitem': {
                '$concatArrays': [
                    '$orderitem', {
                        '$let': {
                            'vars': {
                                'skuItems': {
                                    '$filter': {
                                        'input': '$orderitem', 
                                        'as': 'it', 
                                        'cond': {
                                            '$eq': [
                                                '$$it.collatetype', 'sku'
                                            ]
                                        }
                                    }
                                }
                            }, 
                            'in': {
                                '$map': {
                                    'input': {
                                        '$reduce': {
                                            'input': '$$skuItems', 
                                            'initialValue': [], 
                                            'in': {
                                                '$let': {
                                                    'vars': {
                                                        'asin': '$$this.parent', 
                                                        'sku': '$$this.value', 
                                                        'dataDoc': {
                                                            '$cond': [
                                                                {
                                                                    '$eq': [
                                                                        {
                                                                            '$type': '$$this.data'
                                                                        }, 'object'
                                                                    ]
                                                                }, '$$this.data', {}
                                                            ]
                                                        }, 
                                                        'existing': {
                                                            '$first': {
                                                                '$filter': {
                                                                    'input': '$$value', 
                                                                    'as': 'g', 
                                                                    'cond': {
                                                                        '$eq': [
                                                                            '$$g.value', '$$this.parent'
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }, 
                                                    'in': {
                                                        '$cond': [
                                                            {
                                                                '$ifNull': [
                                                                    '$$existing', False
                                                                ]
                                                            }, {
                                                                '$map': {
                                                                    'input': '$$value', 
                                                                    'as': 'g', 
                                                                    'in': {
                                                                        '$cond': [
                                                                            {
                                                                                '$eq': [
                                                                                    '$$g.value', '$$asin'
                                                                                ]
                                                                            }, {
                                                                                'value': '$$g.value', 
                                                                                'parent': '$$sku', 
                                                                                'collatetype': 'asin', 
                                                                                'data': {
                                                                                    '$reduce': {
                                                                                        'input': {
                                                                                            '$objectToArray': '$$dataDoc'
                                                                                        }, 
                                                                                        'initialValue': '$$g.data', 
                                                                                        'in': {
                                                                                            '$let': {
                                                                                                'vars': {
                                                                                                    'key': '$$this.k', 
                                                                                                    'addVal': '$$this.v', 
                                                                                                    'prev': {
                                                                                                        '$ifNull': [
                                                                                                            {
                                                                                                                '$getField': {
                                                                                                                    'field': '$$this.k', 
                                                                                                                    'input': '$$value'
                                                                                                                }
                                                                                                            }, 0
                                                                                                        ]
                                                                                                    }
                                                                                                }, 
                                                                                                'in': {
                                                                                                    '$mergeObjects': [
                                                                                                        '$$value', {
                                                                                                            '$arrayToObject': [
                                                                                                                [
                                                                                                                    {
                                                                                                                        'k': '$$key', 
                                                                                                                        'v': {
                                                                                                                            '$add': [
                                                                                                                                '$$prev', '$$addVal'
                                                                                                                            ]
                                                                                                                        }
                                                                                                                    }
                                                                                                                ]
                                                                                                            ]
                                                                                                        }
                                                                                                    ]
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }, '$$g'
                                                                        ]
                                                                    }
                                                                }
                                                            }, {
                                                                '$concatArrays': [
                                                                    '$$value', [
                                                                        {
                                                                            'value': '$$asin', 
                                                                            'parent': '$$sku', 
                                                                            'collatetype': 'asin', 
                                                                            'data': '$$dataDoc'
                                                                        }
                                                                    ]
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        }
                                    }, 
                                    'as': 'g', 
                                    'in': '$$g'
                                }
                            }
                        }
                    }
                ]
            }
        }
    }, {
        '$set': {
            'orderitem': {
                '$concatArrays': [
                    '$orderitem', {
                        '$let': {
                            'vars': {
                                'skuItems': {
                                    '$filter': {
                                        'input': '$orderitem', 
                                        'as': 'it', 
                                        'cond': {
                                            '$and': [
                                                {
                                                    '$eq': [
                                                        '$$it.collatetype', 'sku'
                                                    ]
                                                }, {
                                                    '$ne': [
                                                        '$$it.parentsku', None
                                                    ]
                                                }, {
                                                    '$ne': [
                                                        '$$it.parentsku', ''
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }
                            }, 
                            'in': {
                                '$reduce': {
                                    'input': '$$skuItems', 
                                    'initialValue': [], 
                                    'in': {
                                        '$let': {
                                            'vars': {
                                                'cat': '$$this.parentsku', 
                                                'dataDoc': {
                                                    '$cond': [
                                                        {
                                                            '$eq': [
                                                                {
                                                                    '$type': '$$this.data'
                                                                }, 'object'
                                                            ]
                                                        }, '$$this.data', {}
                                                    ]
                                                }, 
                                                'existing': {
                                                    '$first': {
                                                        '$filter': {
                                                            'input': '$$value', 
                                                            'as': 'g', 
                                                            'cond': {
                                                                '$eq': [
                                                                    '$$g.value', '$$this.parentsku'
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }
                                            }, 
                                            'in': {
                                                '$cond': [
                                                    {
                                                        '$ifNull': [
                                                            '$$existing', False
                                                        ]
                                                    }, {
                                                        '$map': {
                                                            'input': '$$value', 
                                                            'as': 'g', 
                                                            'in': {
                                                                '$cond': [
                                                                    {
                                                                        '$eq': [
                                                                            '$$g.value', '$$cat'
                                                                        ]
                                                                    }, {
                                                                        'value': '$$g.value', 
                                                                        'collatetype': 'parentsku', 
                                                                        'data': {
                                                                            '$reduce': {
                                                                                'input': {
                                                                                    '$objectToArray': '$$dataDoc'
                                                                                }, 
                                                                                'initialValue': {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$eq': [
                                                                                                {
                                                                                                    '$type': '$$g.data'
                                                                                                }, 'object'
                                                                                            ]
                                                                                        }, '$$g.data', {}
                                                                                    ]
                                                                                }, 
                                                                                'in': {
                                                                                    '$let': {
                                                                                        'vars': {
                                                                                            'key': '$$this.k', 
                                                                                            'addVal': '$$this.v', 
                                                                                            'prev': {
                                                                                                '$ifNull': [
                                                                                                    {
                                                                                                        '$getField': {
                                                                                                            'field': '$$this.k', 
                                                                                                            'input': '$$value'
                                                                                                        }
                                                                                                    }, 0
                                                                                                ]
                                                                                            }
                                                                                        }, 
                                                                                        'in': {
                                                                                            '$mergeObjects': [
                                                                                                '$$value', {
                                                                                                    '$arrayToObject': [
                                                                                                        [
                                                                                                            {
                                                                                                                'k': '$$key', 
                                                                                                                'v': {
                                                                                                                    '$add': [
                                                                                                                        '$$prev', '$$addVal'
                                                                                                                    ]
                                                                                                                }
                                                                                                            }
                                                                                                        ]
                                                                                                    ]
                                                                                                }
                                                                                            ]
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }, '$$g'
                                                                ]
                                                            }
                                                        }
                                                    }, {
                                                        '$concatArrays': [
                                                            '$$value', {
                                                                '$cond': {
                                                                    'if': {
                                                                        '$ifNull': [
                                                                            '$$cat', False
                                                                        ]
                                                                    }, 
                                                                    'then': [
                                                                        {
                                                                            'value': '$$cat', 
                                                                            'collatetype': 'parentsku', 
                                                                            'data': '$$dataDoc'
                                                                        }
                                                                    ], 
                                                                    'else': []
                                                                }
                                                            }
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
                ]
            }
        }
    }, {
        '$set': {
            'orderitem': {
                '$concatArrays': [
                    '$orderitem', {
                        '$let': {
                            'vars': {
                                'skuItems': {
                                    '$filter': {
                                        'input': '$orderitem', 
                                        'as': 'it', 
                                        'cond': {
                                            '$and': [
                                                {
                                                    '$eq': [
                                                        '$$it.collatetype', 'sku'
                                                    ]
                                                }, {
                                                    '$ne': [
                                                        '$$it.category', None
                                                    ]
                                                }, {
                                                    '$ne': [
                                                        '$$it.category', ''
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }
                            }, 
                            'in': {
                                '$reduce': {
                                    'input': '$$skuItems', 
                                    'initialValue': [], 
                                    'in': {
                                        '$let': {
                                            'vars': {
                                                'cat': '$$this.category', 
                                                'dataDoc': {
                                                    '$cond': [
                                                        {
                                                            '$eq': [
                                                                {
                                                                    '$type': '$$this.data'
                                                                }, 'object'
                                                            ]
                                                        }, '$$this.data', {}
                                                    ]
                                                }, 
                                                'existing': {
                                                    '$first': {
                                                        '$filter': {
                                                            'input': '$$value', 
                                                            'as': 'g', 
                                                            'cond': {
                                                                '$eq': [
                                                                    '$$g.value', '$$this.category'
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }
                                            }, 
                                            'in': {
                                                '$cond': [
                                                    {
                                                        '$ifNull': [
                                                            '$$existing', False
                                                        ]
                                                    }, {
                                                        '$map': {
                                                            'input': '$$value', 
                                                            'as': 'g', 
                                                            'in': {
                                                                '$cond': [
                                                                    {
                                                                        '$eq': [
                                                                            '$$g.value', '$$cat'
                                                                        ]
                                                                    }, {
                                                                        'value': '$$g.value', 
                                                                        'collatetype': 'category', 
                                                                        'data': {
                                                                            '$reduce': {
                                                                                'input': {
                                                                                    '$objectToArray': '$$dataDoc'
                                                                                }, 
                                                                                'initialValue': {
                                                                                    '$cond': [
                                                                                        {
                                                                                            '$eq': [
                                                                                                {
                                                                                                    '$type': '$$g.data'
                                                                                                }, 'object'
                                                                                            ]
                                                                                        }, '$$g.data', {}
                                                                                    ]
                                                                                }, 
                                                                                'in': {
                                                                                    '$let': {
                                                                                        'vars': {
                                                                                            'key': '$$this.k', 
                                                                                            'addVal': '$$this.v', 
                                                                                            'prev': {
                                                                                                '$ifNull': [
                                                                                                    {
                                                                                                        '$getField': {
                                                                                                            'field': '$$this.k', 
                                                                                                            'input': '$$value'
                                                                                                        }
                                                                                                    }, 0
                                                                                                ]
                                                                                            }
                                                                                        }, 
                                                                                        'in': {
                                                                                            '$mergeObjects': [
                                                                                                '$$value', {
                                                                                                    '$arrayToObject': [
                                                                                                        [
                                                                                                            {
                                                                                                                'k': '$$key', 
                                                                                                                'v': {
                                                                                                                    '$add': [
                                                                                                                        '$$prev', '$$addVal'
                                                                                                                    ]
                                                                                                                }
                                                                                                            }
                                                                                                        ]
                                                                                                    ]
                                                                                                }
                                                                                            ]
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }, '$$g'
                                                                ]
                                                            }
                                                        }
                                                    }, {
                                                        '$concatArrays': [
                                                            '$$value', {
                                                                '$cond': {
                                                                    'if': {
                                                                        '$ifNull': [
                                                                            '$$cat', False
                                                                        ]
                                                                    }, 
                                                                    'then': [
                                                                        {
                                                                            'value': '$$cat', 
                                                                            'collatetype': 'category', 
                                                                            'data': '$$dataDoc'
                                                                        }
                                                                    ], 
                                                                    'else': []
                                                                }
                                                            }
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
                ]
            }
        }
    }, {
        '$set': {
            'orderitem': {
                '$concatArrays': [
                    '$orderitem', [
                        {
                            'collatetype': 'marketplace', 
                            'data': {
                                '$reduce': {
                                    'input': {
                                        '$map': {
                                            'input': {
                                                '$filter': {
                                                    'input': '$orderitem', 
                                                    'as': 'it', 
                                                    'cond': {
                                                        '$eq': [
                                                            '$$it.collatetype', 'sku'
                                                        ]
                                                    }
                                                }
                                            }, 
                                            'as': 'sku', 
                                            'in': {
                                                '$cond': [
                                                    {
                                                        '$eq': [
                                                            {
                                                                '$type': '$$sku.data'
                                                            }, 'object'
                                                        ]
                                                    }, '$$sku.data', {}
                                                ]
                                            }
                                        }
                                    }, 
                                    'initialValue': {}, 
                                    'in': {
                                        '$reduce': {
                                            'input': {
                                                '$objectToArray': '$$this'
                                            }, 
                                            'initialValue': '$$value', 
                                            'in': {
                                                '$let': {
                                                    'vars': {
                                                        'key': '$$this.k', 
                                                        'addVal': '$$this.v', 
                                                        'prev': {
                                                            '$ifNull': [
                                                                {
                                                                    '$getField': {
                                                                        'field': '$$this.k', 
                                                                        'input': '$$value'
                                                                    }
                                                                }, 0
                                                            ]
                                                        }
                                                    }, 
                                                    'in': {
                                                        '$mergeObjects': [
                                                            '$$value', {
                                                                '$arrayToObject': [
                                                                    [
                                                                        {
                                                                            'k': '$$key', 
                                                                            'v': {
                                                                                '$add': [
                                                                                    '$$prev', '$$addVal'
                                                                                ]
                                                                            }
                                                                        }
                                                                    ]
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
                    ]
                ]
            }
        }
    }, {
        '$unwind': {
            'path': '$orderitem', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    {
                        '$unsetField': {
                            'input': '$$ROOT', 
                            'field': 'orderitem'
                        }
                    }, '$orderitem'
                ]
            }
        }
    }, {
        '$set': {
            'data': {
                '$arrayToObject': {
                    '$filter': {
                        'input': {
                            '$objectToArray': '$data'
                        }, 
                        'as': 'kv', 
                        'cond': {
                            '$ne': [
                                '$$kv.v', 0
                            ]
                        }
                    }
                }
            }
        }
    }, {
        '$match': {
            '$expr': {
                '$gt': [
                    {
                        '$sum': {
                            '$map': {
                                'input': {
                                    '$objectToArray': '$data'
                                }, 
                                'as': 'kv', 
                                'in': {
                                    '$abs': '$$kv.v'
                                }
                            }
                        }
                    }, 0
                ]
            }
        }
    }, {
        '$set': {
            '_id': {
                '$concat': [
                    {
                        '$toString': '$marketplace'
                    }, '_', {
                        '$cond': [
                            {
                                '$ifNull': [
                                    '$value', False
                                ]
                            }, {
                                '$concat': [
                                    '$value', '_'
                                ]
                            }, ''
                        ]
                    }, '$state', '_', {
                        '$dateToString': {
                            'date': '$date', 
                            'format': '%Y-%m-%d'
                        }
                    }
                ]
            }
        }
    }, {
        '$merge': {
            'into': 'state_analytics'
        }
    }
]