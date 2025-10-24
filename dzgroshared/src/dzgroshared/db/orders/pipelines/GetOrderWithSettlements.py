from datetime import datetime
from dzgroshared.db.marketplaces.model import UserMarketplace
from dzgroshared.db.model import PyObjectId
from dzgroshared.db.orders.model import OrderPaymentRequest, OrderPaymentStatus, OrderShippingStatus, OrderShippingStatusFacet

def projectOrderAttributes(marketplace: UserMarketplace):
    return [{
        '$project': {
            'orderid': 1, 
            'orderdate': 1, 
            'fulfillment': 1, 
            'orderstatus': 1, 
            'marketplace': 1
        }
    },
    {
        '$set': {
            'settlementdate': marketplace.settlementdate
        }
    }, {
        '$lookup': {
            'from': 'order_items', 
            'foreignField': 'order', 
            'localField': '_id', 
            'pipeline': [
                {
                    '$project': {
                        'sku': 1, 
                        'asin': 1, 
                        'quantity': 1, 
                        'revenue': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'orderitems'
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
                }, {
                    '$project': {
                        'amounttype': 1, 
                        'transactiontype': 1, 
                        'amountdescription': 1, 
                        'amount': 1, 
                        'sku': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'settlements'
        }
    }, {
        '$set': {
            'settlements': {
                '$map': {
                    'input': '$settlements', 
                    'as': 's', 
                    'in': {
                        '$mergeObjects': [
                            '$$s', {
                                'amounttype': {
                                    '$let': {
                                        'vars': {
                                            'allWords': {
                                                '$regexFindAll': {
                                                    'input': '$$s.amounttype', 
                                                    'regex': '[A-Z]?[a-z]+|[A-Z]+(?![a-z])'
                                                }
                                            }
                                        }, 
                                        'in': {
                                            '$reduce': {
                                                'input': '$$allWords', 
                                                'initialValue': '', 
                                                'in': {
                                                    '$concat': [
                                                        '$$value', {
                                                            '$cond': {
                                                                'if': {
                                                                    '$eq': [
                                                                        '$$value', ''
                                                                    ]
                                                                }, 
                                                                'then': '', 
                                                                'else': ' '
                                                            }
                                                        }, {
                                                            '$toUpper': {
                                                                '$substrCP': [
                                                                    '$$this.match', 0, 1
                                                                ]
                                                            }
                                                        }, {
                                                            '$substrCP': [
                                                                '$$this.match', 1, {
                                                                    '$strLenCP': '$$this.match'
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                }, 
                                'amountdescription': {
                                    '$let': {
                                        'vars': {
                                            'allWords': {
                                                '$regexFindAll': {
                                                    'input': '$$s.amountdescription', 
                                                    'regex': '[A-Z]?[a-z]+|[A-Z]+(?![a-z])'
                                                }
                                            }
                                        }, 
                                        'in': {
                                            '$reduce': {
                                                'input': '$$allWords', 
                                                'initialValue': '', 
                                                'in': {
                                                    '$concat': [
                                                        '$$value', {
                                                            '$cond': {
                                                                'if': {
                                                                    '$eq': [
                                                                        '$$value', ''
                                                                    ]
                                                                }, 
                                                                'then': '', 
                                                                'else': ' '
                                                            }
                                                        }, {
                                                            '$toUpper': {
                                                                '$substrCP': [
                                                                    '$$this.match', 0, 1
                                                                ]
                                                            }
                                                        }, {
                                                            '$substrCP': [
                                                                '$$this.match', 1, {
                                                                    '$strLenCP': '$$this.match'
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
                        ]
                    }
                }
            }
        }
    }, {
        '$set': {
            'orderitems': {
                '$map': {
                    'input': '$orderitems', 
                    'as': 'o', 
                    'in': {
                        '$mergeObjects': [
                            '$$o', {
                                '$let': {
                                    'vars': {
                                        'settlements': {
                                            '$filter': {
                                                'input': '$settlements', 
                                                'as': 's', 
                                                'cond': {
                                                    '$eq': [
                                                        '$$s.sku', '$$o.sku'
                                                    ]
                                                }
                                            }
                                        }
                                    }, 
                                    'in': {
                                        'settlements': {
                                            '$map': {
                                                'input': '$$settlements', 
                                                'as': 's', 
                                                'in': {
                                                    'amounttype': '$$s.amounttype', 
                                                    'transactiontype': '$$s.transactiontype', 
                                                    'amountdescription': '$$s.amountdescription', 
                                                    'amount': '$$s.amount'
                                                }
                                            }
                                        }, 
                                        'hasRefund': {
                                            '$anyElementTrue': {
                                                '$map': {
                                                    'input': '$$settlements', 
                                                    'as': 's', 
                                                    'in': {
                                                        '$eq': [
                                                            '$$s.transactiontype', 'Refund'
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
            }
        }
    }, {
        '$set': {
            'revenue': {
                '$reduce': {
                    'input': '$orderitems', 
                    'initialValue': 0, 
                    'in': {
                        '$sum': [
                            '$$value', '$$this.revenue'
                        ]
                    }
                }
            }, 
            'settlement': {
                '$round': [
                    {
                        '$reduce': {
                            'input': '$settlements', 
                            'initialValue': 0, 
                            'in': {
                                '$sum': [
                                    '$$value', '$$this.amount'
                                ]
                            }
                        }
                    }, 2
                ]
            }
        }
    }, {
        '$set': {
            'payoutPercent': {
                '$cond': {
                    'if': {
                        '$and': [
                            {
                                '$gt': [
                                    '$settlement', 0
                                ]
                            }, {
                                '$gt': [
                                    '$revenue', 0
                                ]
                            }
                        ]
                    }, 
                    'then': {
                        '$concat': [
                            {
                                '$toString': {
                                    '$round': [
                                        {
                                            '$multiply': [
                                                {
                                                    '$divide': [
                                                        '$settlement', '$revenue'
                                                    ]
                                                }, 100
                                            ]
                                        }, 2
                                    ]
                                }
                            }, '%'
                        ]
                    }, 
                    'else': '-'
                }
            }
        }
    }, {
        '$set': {
            'shippingStatus': {
                '$let': {
                    'vars': {
                        'itemStatuses': {
                            '$map': {
                                'input': '$orderitems', 
                                'as': 'o', 
                                'in': '$$o.hasRefund'
                            }
                        }
                    }, 
                    'in': {
                        '$cond': {
                            'if': {
                                '$eq': [
                                    '$orderstatus', 'CANCELLED'
                                ]
                            }, 
                            'then': 'Cancelled', 
                            'else': {
                                '$cond': {
                                    'if': {
                                        '$allElementsTrue': '$$itemStatuses'
                                    }, 
                                    'then': 'Returned', 
                                    'else': {
                                        '$cond': {
                                            'if': {
                                                '$anyElementTrue': '$$itemStatuses'
                                            }, 
                                            'then': 'Partial Returned', 
                                            'else': 'Delivered'
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
            'paymentStatus': {
                '$cond': {
                    'if': {
                        '$eq': [
                            '$orderstatus', 'CANCELLED'
                        ]
                    }, 
                    'then': 'Cancelled', 
                    'else': {
                        '$cond': {
                            'if': {
                                '$gt': [
                                    {
                                        '$size': '$settlements'
                                    }, 0
                                ]
                            }, 
                            'then': 'Paid', 
                            'else': {
                                '$cond': {
                                    'if': {
                                        '$gt': [
                                            '$orderdate', '$settlementdate'
                                        ]
                                    }, 
                                    'then': 'Pending Settlement', 
                                    'else': {
                                        '$cond': {
                                            'if': {
                                                '$gt': [
                                                    {
                                                        '$dateAdd': {
                                                            'startDate': '$orderdate', 
                                                            'amount': 60, 
                                                            'unit': 'day'
                                                        }
                                                    }, '$$NOW'
                                                ]
                                            }, 
                                            'then': 'Overdue', 
                                            'else': 'Unpaid'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }]
    
def setSettlementItems():
    return [
        {
        '$set': {
            'items': {
                'columns': {
                    '$concatArrays': [
                        [
                            'Product', 'Amount Type', 'Amount Description', 'Order Amount'
                        ], {
                            '$cond': {
                                'if': {
                                    '$ne': [
                                        '$shippingStatus', 'Delivered'
                                    ]
                                }, 
                                'then': [
                                    'Refund Amount'
                                ], 
                                'else': []
                            }
                        }
                    ]
                }, 
                'rows': {
                    '$concatArrays': [
                        {
                            '$reduce': {
                                'input': '$orderitems', 
                                'initialValue': [], 
                                'in': {
                                    '$concatArrays': [
                                        '$$value', [
                                            {
                                                'product': {
                                                    'sku': '$$this.sku', 
                                                    'asin': '$$this.asin'
                                                }, 
                                                'settlements': {
                                                    '$let': {
                                                        'vars': {
                                                            'settlements': {
                                                                '$sortArray': {
                                                                    'input': '$$this.settlements', 
                                                                    'sortBy': {
                                                                        'amount': -1
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'in': {
                                                            '$reduce': {
                                                                'input': '$$settlements', 
                                                                'initialValue': [], 
                                                                'in': {
                                                                    '$cond': {
                                                                        'if': {
                                                                            '$eq': [
                                                                                {
                                                                                    '$indexOfArray': [
                                                                                        '$$value.amounttype', '$$this.amounttype'
                                                                                    ]
                                                                                }, -1
                                                                            ]
                                                                        }, 
                                                                        'then': {
                                                                            '$concatArrays': [
                                                                                '$$value', [
                                                                                    {
                                                                                        'amounttype': '$$this.amounttype', 
                                                                                        'descriptions': {
                                                                                            '$reduce': {
                                                                                                'input': {
                                                                                                    '$filter': {
                                                                                                        'input': '$$settlements', 
                                                                                                        'as': 's', 
                                                                                                        'cond': {
                                                                                                            '$eq': [
                                                                                                                '$$s.amounttype', '$$this.amounttype'
                                                                                                            ]
                                                                                                        }
                                                                                                    }
                                                                                                }, 
                                                                                                'initialValue': [], 
                                                                                                'in': {
                                                                                                    '$cond': {
                                                                                                        'if': {
                                                                                                            '$eq': [
                                                                                                                {
                                                                                                                    '$indexOfArray': [
                                                                                                                        '$$value', '$$this.amountdescription'
                                                                                                                    ]
                                                                                                                }, -1
                                                                                                            ]
                                                                                                        }, 
                                                                                                        'then': {
                                                                                                            '$concatArrays': [
                                                                                                                '$$value', [
                                                                                                                    '$$this.amountdescription'
                                                                                                                ]
                                                                                                            ]
                                                                                                        }, 
                                                                                                        'else': '$$value'
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                ]
                                                                            ]
                                                                        }, 
                                                                        'else': '$$value'
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
                        }, []
                    ]
                }
            }
        }
    }, {
        '$set': {
            'rows': {
                '$map': {
                    'input': {
                        '$ifNull': [
                            '$items.rows', []
                        ]
                    }, 
                    'as': 'r', 
                    'in': {
                        'product': '$$r.product', 
                        'rowSpan': {
                            '$reduce': {
                                'input': '$$r.settlements', 
                                'initialValue': 0, 
                                'in': {
                                    '$sum': [
                                        '$$value', {
                                            '$size': '$$this.descriptions'
                                        }
                                    ]
                                }
                            }
                        },
                        'settlements': {
                            '$map': {
                                'input': '$$r.settlements', 
                                'as': 's', 
                                'in': {
                                    'title': '$$s.amounttype', 
                                    'rowSpan': {
                                        '$size': '$$s.descriptions'
                                    }, 
                                    'items': {
                                        '$map': {
                                            'input': '$$s.descriptions', 
                                            'as': 'd', 
                                            'in': {
                                                'title': '$$d', 
                                                'orderAmount': {
                                                    '$getField': {
                                                        'input': {
                                                            '$first': {
                                                                '$filter': {
                                                                    'input': '$settlements', 
                                                                    'as': 'f', 
                                                                    'cond': {
                                                                        '$and': [
                                                                            {
                                                                                '$eq': [
                                                                                    '$$f.sku', '$$r.product.sku'
                                                                                ]
                                                                            }, {
                                                                                '$ne': [
                                                                                    '$$f.transactiontype', 'Refund'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$f.amounttype', '$$s.amounttype'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$f.amountdescription', '$$d'
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'field': 'amount'
                                                    }
                                                }, 
                                                'refundAmount': {
                                                    '$getField': {
                                                        'input': {
                                                            '$first': {
                                                                '$filter': {
                                                                    'input': '$settlements', 
                                                                    'as': 'f', 
                                                                    'cond': {
                                                                        '$and': [
                                                                            {
                                                                                '$eq': [
                                                                                    '$$f.sku', '$$r.product.sku'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$f.transactiontype', 'Refund'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$f.amounttype', '$$s.amounttype'
                                                                                ]
                                                                            }, {
                                                                                '$eq': [
                                                                                    '$$f.amountdescription', '$$d'
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            }
                                                        }, 
                                                        'field': 'amount'
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
            'nonskurows': {
                '$let': {
                    'vars': {
                        'settlements': {
                            '$sortArray': {
                                'input': {
                                    '$filter': {
                                        'input': '$settlements', 
                                        'as': 's', 
                                        'cond': {
                                            '$eq': [
                                                {
                                                    '$ifNull': [
                                                        '$$s.sku', None
                                                    ]
                                                }, None
                                            ]
                                        }
                                    }
                                }, 
                                'sortBy': {
                                    'amount': -1
                                }
                            }
                        }
                    }, 
                    'in': {
                        '$reduce': {
                            'input': '$$settlements', 
                            'initialValue': [], 
                            'in': {
                                '$cond': {
                                    'if': {
                                        '$eq': [
                                            {
                                                '$indexOfArray': [
                                                    '$$value.amounttype', '$$this.amounttype'
                                                ]
                                            }, -1
                                        ]
                                    }, 
                                    'then': {
                                        '$concatArrays': [
                                            '$$value', [
                                                {
                                                    'amounttype': '$$this.amounttype', 
                                                    'descriptions': {
                                                        '$reduce': {
                                                            'input': {
                                                                '$filter': {
                                                                    'input': '$$settlements', 
                                                                    'as': 's', 
                                                                    'cond': {
                                                                        '$eq': [
                                                                            '$$s.amounttype', '$$this.amounttype'
                                                                        ]
                                                                    }
                                                                }
                                                            }, 
                                                            'initialValue': [], 
                                                            'in': {
                                                                '$cond': {
                                                                    'if': {
                                                                        '$eq': [
                                                                            {
                                                                                '$indexOfArray': [
                                                                                    '$$value', '$$this.amountdescription'
                                                                                ]
                                                                            }, -1
                                                                        ]
                                                                    }, 
                                                                    'then': {
                                                                        '$concatArrays': [
                                                                            '$$value', [
                                                                                '$$this.amountdescription'
                                                                            ]
                                                                        ]
                                                                    }, 
                                                                    'else': '$$value'
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        ]
                                    }, 
                                    'else': '$$value'
                                }
                            }
                        }
                    }
                }
            }
        }
    }, {
        '$set': {
            'items.rows': {
                '$concatArrays': [
                    '$rows', {
                        '$let': {
                            'vars': {
                                'settlements': {
                                    '$filter': {
                                        'input': '$settlements', 
                                        'as': 's', 
                                        'cond': {
                                            '$eq': [
                                                {
                                                    '$ifNull': [
                                                        '$$s.sku', None
                                                    ]
                                                }, None
                                            ]
                                        }
                                    }
                                }
                            }, 
                            'in': {
                                '$map': {
                                    'input': '$nonskurows', 
                                    'as': 'r', 
                                    'in': {
                                        'rowSpan': {
                                            '$size': '$$r.descriptions'
                                        }, 
                                        'settlements': [{
                                            'title': '$$r.amounttype', 
                                            'rowSpan': {
                                                '$size': '$$r.descriptions'
                                            }, 
                                            'items': {
                                                '$map': {
                                                    'input': '$$r.descriptions', 
                                                    'as': 'd', 
                                                    'in': {
                                                        'title': '$$d', 
                                                        'orderAmount': {
                                                            '$getField': {
                                                                'input': {
                                                                    '$first': {
                                                                        '$filter': {
                                                                            'input': '$$settlements', 
                                                                            'as': 'f', 
                                                                            'cond': {
                                                                                '$and': [
                                                                                    {
                                                                                        '$ne': [
                                                                                            '$$f.transactiontype', 'Refund'
                                                                                        ]
                                                                                    }, {
                                                                                        '$eq': [
                                                                                            '$$f.amounttype', '$$r.amounttype'
                                                                                        ]
                                                                                    }, {
                                                                                        '$eq': [
                                                                                            '$$f.amountdescription', '$$d'
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        }
                                                                    }
                                                                }, 
                                                                'field': 'amount'
                                                            }
                                                        }, 
                                                        'refundAmount': {
                                                            '$getField': {
                                                                'input': {
                                                                    '$first': {
                                                                        '$filter': {
                                                                            'input': '$$settlements', 
                                                                            'as': 'f', 
                                                                            'cond': {
                                                                                '$and': [
                                                                                    {
                                                                                        '$eq': [
                                                                                            '$$f.transactiontype', 'Refund'
                                                                                        ]
                                                                                    }, {
                                                                                        '$eq': [
                                                                                            '$$f.amounttype', '$$r.amounttype'
                                                                                        ]
                                                                                    }, {
                                                                                        '$eq': [
                                                                                            '$$f.amountdescription', '$$d'
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        }
                                                                    }
                                                                }, 
                                                                'field': 'amount'
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }]
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }, {
        '$project': {
            'orderid': 1, 
            'orderdate': 1, 
            'fulfillment': 1, 
            'revenue': 1, 
            'settlement': 1, 
            'payoutPercent': 1, 
            'shippingStatus': 1, 
            'paymentStatus': 1, 
            'items': 1, 
            'marketplace': 1, 
            '_id': 0
        }
    }
    ]
    
def addImage():
    return {
        '$set': {
            'skus': {
                '$setUnion': {
                    '$reduce': {
                        'input': '$items.rows', 
                        'initialValue': [], 
                        'in': {
                            '$concatArrays': [
                                '$$value', {
                                    '$ifNull': [
                                        [
                                            '$$this.product.sku'
                                        ], []
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'products', 
            'let': {
                'marketplace': '$marketplace', 
                'skus': '$skus'
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
                                    '$in': [
                                        '$sku', '$$skus'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'image': {
                            '$first': '$images'
                        }, 
                        'sku': '$sku', 
                        '_id': 0
                    }
                }
            ], 
            'as': 'skus'
        }
    }, {
        '$set': {
            'items.rows': {
                '$map': {
                    'input': '$items.rows', 
                    'as': 'r', 
                    'in': {
                        '$mergeObjects': [
                            '$$r', {
                                '$cond': {
                                    'if': {
                                        '$ifNull': [
                                            '$$r.product', False
                                        ]
                                    }, 
                                    'then': {
                                        'product': {
                                            '$mergeObjects': [
                                                '$$r.product', {
                                                    'image': {
                                                        '$getField': {
                                                            'input': {
                                                                '$first': {
                                                                    '$filter': {
                                                                        'input': '$skus', 
                                                                        'as': 'f', 
                                                                        'cond': {
                                                                            '$eq': [
                                                                                '$$f.sku', '$$r.product.sku'
                                                                            ]
                                                                        }
                                                                    }
                                                                }
                                                            }, 
                                                            'field': 'image'
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }, 
                                    'else': {}
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    
def project():
    return [
        {
        '$group': {
            '_id': None, 
            'data': {
                '$push': {
                    'orderid': '$$ROOT.orderid', 
                    'orderdate': '$$ROOT.orderdate', 
                    'fulfillment': '$$ROOT.fulfillment', 
                    'revenue': '$$ROOT.revenue', 
                    'settlement': '$$ROOT.settlement', 
                    'payoutPercent': '$$ROOT.payoutPercent', 
                    'shippingStatus': '$$ROOT.shippingStatus', 
                    'paymentStatus': '$$ROOT.paymentStatus', 
                    'items': '$$ROOT.items'
                }
            }
        }
    }, {
        '$project': {
            '_id': 0
        }
    }
    ]

def pipelineForList(marketplace: UserMarketplace, req: OrderPaymentRequest):
    dates = req.dates or marketplace.dates
    if not dates or not marketplace.settlementdate: raise ValueError("Date Range not configured")
    pipeline = [ { '$match': { 'marketplace': marketplace.id, 'date': {"$gte": dates.startdate, "$lte": dates.enddate} } }, { '$sort': { 'orderdate': -1 } }]
    pipeline.extend(projectOrderAttributes(marketplace))
    pipeline.append({ "$match": { "paymentStatus": req.paymentStatus if req.paymentStatus else {"$in": OrderPaymentStatus.list()} } })
    pipeline.append({ "$match": { "shippingStatus": req.shippingStatus if req.shippingStatus else {"$in": OrderShippingStatus.list()} } })
    pipeline.extend(setSettlementItems())
    pipeline.extend([{ '$skip': req.paginator.skip }, { '$limit': req.paginator.limit }])
    pipeline.extend(addImage())
    pipeline.extend(project())
    return pipeline, dates
        
def pipelineForOrderId(marketplace: UserMarketplace, orderid: str):
    if not marketplace.settlementdate: raise ValueError("Date Range not configured")
    pipeline = [ { '$match': { 'marketplace': marketplace.id, 'orderid': orderid } }]
    pipeline.extend(projectOrderAttributes(marketplace))
    pipeline.extend(setSettlementItems())
    pipeline.extend(addImage())
    return pipeline
    
    