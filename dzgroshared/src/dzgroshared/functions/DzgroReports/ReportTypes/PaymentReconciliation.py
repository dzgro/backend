from datetime import datetime, timezone
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.dzgro_reports import DzroReportPaymentReconRequest
from dzgroshared.models.enums import Operator,CollectionType
from dzgroshared.db.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor
from dzgroshared.models.model import PyObjectId

class PaymentReconReportCreator:
    client: DzgroSharedClient
    reportId: PyObjectId
    options: DzroReportPaymentReconRequest

    def __init__(self, client: DzgroSharedClient, reportId: PyObjectId, options: DzroReportPaymentReconRequest ) -> None:
        self.client = client
        self.reportId = reportId
        self.options = options

    def getProjection(self)->dict:
        return {"_id": 0}

    async def execute(self):
        orders = self.client.db.orders
        pipeline = self.pipeline()
        await orders.db.aggregate(pipeline)
        count = await self.client.db.dzgro_reports_data.count(self.reportId)
        return count, self.getProjection()

    def pipeline(self):
        return [
    {
        '$set': {
            'dates': {
                '$let': {
                    'vars': {
                        'startDate': datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc), 
                        'endDate': datetime(2025, 7, 31, 0, 0, 0, tzinfo=timezone.utc)
                    }, 
                    'in': {
                        '$reduce': {
                            'input': {
                                '$range': [
                                    0, {
                                        '$sum': [
                                            {
                                                '$dateDiff': {
                                                    'startDate': '$$startDate', 
                                                    'endDate': '$$endDate', 
                                                    'unit': 'day'
                                                }
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
                                            '$dateAdd': {
                                                'startDate': '$$startDate', 
                                                'unit': 'day', 
                                                'amount': '$$this'
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
    }, {
        '$match': {
            '$expr': {
                '$and': [
                    {
                        '$eq': [
                            '$uid', '41e34d1a-6031-70d2-9ff3-d1a704240921'
                        ]
                    }, {
                        '$eq': [
                            '$marketplace', ObjectId('6895638c452dc4315750e826')
                        ]
                    }, {
                        '$in': [
                            '$date', '$dates'
                        ]
                    }
                ]
            }
        }
    }, {
        '$lookup': {
            'from': 'order_items', 
            'localField': '_id', 
            'foreignField': 'order', 
            'pipeline': [
                {
                    '$group': {
                        '_id': {
                            'sku': '$sku', 
                            'asin': '$asin'
                        }, 
                        'price': {
                            '$sum': '$price'
                        }, 
                        'tax': {
                            '$sum': '$tax'
                        }, 
                        'shippingprice': {
                            '$sum': '$shippingprice'
                        }, 
                        'shippingtax': {
                            '$sum': '$shippingtax'
                        }, 
                        'giftwrapprice': {
                            '$sum': '$giftwrapprice'
                        }, 
                        'giftwraptax': {
                            '$sum': '$giftwraptax'
                        }, 
                        'itempromotiondiscount': {
                            '$sum': '$itempromotiondiscount'
                        }, 
                        'shippromotiondiscount': {
                            '$sum': '$shippromotiondiscount'
                        }
                    }
                }, {
                    '$replaceRoot': {
                        'newRoot': {
                            '$mergeObjects': [
                                '$$ROOT', '$_id'
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0
                    }
                }
            ], 
            'as': 'item'
        }
    }, {
        '$lookup': {
            'from': 'settlements', 
            'let': {
                'uid': '$uid', 
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
                                        '$uid', '$$uid'
                                    ]
                                }, {
                                    '$eq': [
                                        '$marketplace', '$$marketplace'
                                    ]
                                }, {
                                    '$eq': [
                                        '$orderid', '$$orderid'
                                    ]
                                }, {
                                    '$ne': [
                                        '$amounttype', 'ItemPrice'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0
                    }
                }
            ], 
            'as': 'settlements'
        }
    }, {
        '$set': {
            'products': {
                '$reduce': {
                    'input': '$item', 
                    'initialValue': [
                        {
                            'expense': {
                                '$reduce': {
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
                                    'initialValue': 0, 
                                    'in': {
                                        '$sum': [
                                            '$$value', '$$this.amount'
                                        ]
                                    }
                                }
                            }
                        }
                    ], 
                    'in': {
                        '$concatArrays': [
                            '$$value', [
                                {
                                    '$mergeObjects': [
                                        '$$this', {
                                            'expense': {
                                                '$reduce': {
                                                    'input': {
                                                        '$filter': {
                                                            'input': '$settlements', 
                                                            'as': 's', 
                                                            'cond': {
                                                                '$eq': [
                                                                    '$$this.sku', '$$s.sku'
                                                                ]
                                                            }
                                                        }
                                                    }, 
                                                    'initialValue': 0, 
                                                    'in': {
                                                        '$sum': [
                                                            '$$value', '$$this.amount'
                                                        ]
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
    }, {
        '$project': {
            'orderid': 1, 
            'orderdate': 1, 
            'products': 1, 
            '_id': 0
        }
    }, {
        '$unwind': {
            'path': '$products'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    {
                        '$unsetField': {
                            'input': '$$ROOT', 
                            'field': 'products'
                        }
                    }, '$products'
                ]
            }
        }
    }, {
        '$set': {
            'netprice': {
                '$subtract': [
                    {
                        '$sum': [
                            '$price', '$shippingprice', '$giftwrapprice'
                        ]
                    }, {
                        '$sum': [
                            '$itempromotiondiscount', '$shippromotiondiscount'
                        ]
                    }
                ]
            }, 
            'nettax': {
                '$sum': [
                    '$tax', '$shippingtax', '$giftwraptax'
                ]
            }, 
            'reportid': ObjectId('6895638c452dc4315750e826')
        }
    }, {
        '$set': {
            'netproceeds': {
                '$round': [
                    {
                        '$add': [
                            '$netprice', '$expense'
                        ]
                    }, 2
                ]
            }
        }
    }, {
        '$merge': {
            'into': 'dzgro_report_data'
        }
    }
]

    def getPipeline(self, pp: PipelineProcessor):

        def lookupOrderItems():
            groupOrderItems = pp.group(None, groupings={'price': { '$sum': '$price' }, 'tax': { '$sum': '$tax' }, 'shippingprice': { '$sum': '$shippingprice' }, 'shippingtax': { '$sum': '$shippingtax' }, 'giftwrapprice': { '$sum': '$giftwrapprice' }, 'giftwraptax': { '$sum': '$giftwraptax' }, 'itempromotiondiscount': { '$sum': '$itempromotiondiscount' }, 'shippromotiondiscount': { '$sum': '$shippromotiondiscount' } })
            innerpipeline = [pp.matchAllExpressions(matchExprs), groupOrderItems, pp.project([],["_id"])]
            return pp.lookup(CollectionType.ORDER_ITEMS, 'price', letkeys=letkeys, pipeline=innerpipeline)

        def lookupSettlements():
            matchExprs.append(LookUpPipelineMatchExpression(key='amounttype', value='ItemPrice', operator=Operator.NE))
            groupOrderItems = pp.group(None, groupings={"expense": { "$sum": "$amount" }})
            innerpipeline = [pp.matchAllExpressions(matchExprs), groupOrderItems, pp.project([],["_id"])]
            return pp.lookup(CollectionType.SETTLEMENTS, 'expense', letkeys=letkeys, pipeline=innerpipeline)
        matchStage = pp.matchMarketplace()
        letkeys=['uid','marketplace','orderid']
        matchExprs = [LookUpPipelineMatchExpression(key=x) for x in letkeys]
        lookup1 = lookupOrderItems()
        lookup2 = lookupSettlements()
        setExpense = pp.set({ "expense": { "$cond": [ { "$eq": [ {"$size": "$expense"}, 0 ] }, 0, { "$first": "$expense.expense" } ] }})
        setPrice = pp.set({"price": { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': { '$first': '$price' } }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this.k', 'v': { '$cond': [ { '$in': [ '$orderstatus', [ 'Cancelled', 'Shipped - Returned to Seller', 'Shipped - Returning to Seller' ] ] }, 0, '$$this.v' ] } } ] ] } } } } })
        mergePrice = pp.replaceRoot(pp.mergeObjects(['$$ROOT', '$price']))
        setNetPrice = pp.set({ 'netprice': { '$subtract': [ { '$sum': [ '$price', '$shippingprice', '$giftwrapprice' ] }, { '$sum': [ '$itempromotiondiscount', '$shippromotiondiscount' ] } ] }, 'nettax': { '$sum': [ '$tax', '$shippingtax', '$giftwraptax' ] } })
        setNetProceeds = pp.set({ 'netproceeds': { '$round': [ { '$sum': [ '$netprice', '$expense' ] }, 2 ] }, 'reportid': self.reportId })
        unsetFields = pp.unset([ '_id', 'date', 'country', 'city', 'code', 'uid', 'marketplace' ])
        convertDate = pp.set({ 'orderdate': { '$dateToString': { 'date': '$orderdate' } } })
        convertIntToDouble = pp.convertIntToDouble()
        merge = pp.merge(CollectionType.DZGRO_REPORT_DATA)
        pipeline = [matchStage, lookup1, lookup2, setExpense,setPrice,mergePrice, setNetPrice, setNetProceeds, unsetFields, convertDate, convertIntToDouble,merge]
        return pipeline
    
