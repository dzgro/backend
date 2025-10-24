from dzgroshared.db.marketplaces.model import UserMarketplace
from dzgroshared.db.orders.model import OrderPaymentFacetRequest, OrderPaymentStatus, OrderShippingStatus
from dzgroshared.db.orders.pipelines import GetOrderWithSettlements


def addFacets():
    return [
        {
        '$facet': {
            'paymentStatuses': [
                {
                    '$sortByCount': '$paymentStatus'
                }
            ],
            'shippingStatuses': [
                {
                    '$sortByCount': '$shippingStatus'
                }
            ]
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$let': {
                    'vars': {
                        'count': {
                            'title': 'Total Orders', 
                            'count': {
                                '$reduce': {
                                    'input': '$paymentStatuses', 
                                    'initialValue': 0, 
                                    'in': {
                                        '$sum': [
                                            '$$value', '$$this.count'
                                        ]
                                    }
                                }
                            }
                        }
                    }, 
                    'in': {
                        '$mergeObjects': [
                            {
                                'count': '$$count.count'
                            }, {
                                'paymentStatuses': {
                                    '$reduce': {
                                        'input': [
                                            'Paid', 'Unpaid', 'Pending Settlement', 'Overdue', 'Cancelled'
                                        ], 
                                        'initialValue': [
                                            '$$count'
                                        ], 
                                        'in': {
                                            '$concatArrays': [
                                                '$$value', [
                                                    {
                                                        'title': '$$this', 
                                                        'count': {
                                                            '$ifNull': [
                                                                {
                                                                    '$getField': {
                                                                        'input': {
                                                                            '$first': {
                                                                                '$filter': {
                                                                                    'input': '$paymentStatuses', 
                                                                                    'as': 's', 
                                                                                    'cond': {
                                                                                        '$eq': [
                                                                                            '$$s._id', '$$this'
                                                                                        ]
                                                                                    }
                                                                                }
                                                                            }
                                                                        }, 
                                                                        'field': 'count'
                                                                    }
                                                                }, 0
                                                            ]
                                                        }
                                                    }
                                                ]
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                'shippingStatuses': {
                                    '$reduce': {
                                        'input': [
                                            'Delivered','Returned','Partial Returned','Cancelled'
                                        ], 
                                        'initialValue': ["$$count"],
                                        'in': {
                                            '$concatArrays': [
                                                '$$value', [
                                                    {
                                                        'title': '$$this', 
                                                        'count': {
                                                            '$ifNull': [
                                                                {
                                                                    '$getField': {
                                                                        'input': {
                                                                            '$first': {
                                                                                '$filter': {
                                                                                    'input': '$shippingStatuses', 
                                                                                    'as': 's', 
                                                                                    'cond': {
                                                                                        '$eq': [
                                                                                            '$$s._id', '$$this'
                                                                                        ]
                                                                                    }
                                                                                }
                                                                            }
                                                                        }, 
                                                                        'field': 'count'
                                                                    }
                                                                }, 0
                                                            ]
                                                        }
                                                    }
                                                ]
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

def pipeline(marketplace: UserMarketplace, req: OrderPaymentFacetRequest):
    dates = req.dates or marketplace.dates
    if not dates or not marketplace.settlementdate: raise ValueError("Date Range not configured")
    pipeline = [{ '$match': { 'marketplace': marketplace.id, 'date': { '$gte': dates.startdate, '$lte': dates.enddate } } }]
    pipeline.extend(GetOrderWithSettlements.projectOrderAttributes(marketplace))
    pipeline.append({ "$match": { "paymentStatus": req.paymentStatus if req.paymentStatus else {"$in": OrderPaymentStatus.list()} } })
    pipeline.append({ "$match": { "shippingStatus": req.shippingStatus if req.shippingStatus else {"$in": OrderShippingStatus.list()} } })
    pipeline.extend(addFacets())
    return pipeline
    