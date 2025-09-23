from bson import ObjectId
from dzgroshared.db.model import Paginator


def pipeline(uid:str, paginator: Paginator, marketplace: ObjectId|None = None) -> list[dict]:
    pipeline: list[dict] = [{'$match': {'_id': marketplace, 'uid': uid} if marketplace else {'uid': uid}}]
    if not marketplace: pipeline.extend([{ "$sort": { "_id": -1 } },{ "$skip": paginator.skip }, { "$limit": paginator.limit }])
    pipeline.extend([{
        '$lookup': {
            'from': 'spapi_accounts', 
            'localField': 'seller', 
            'foreignField': '_id', 
            'pipeline': [
                {
                    '$project': {
                        'name': 1, 
                        '_id': 0
                    }
                }
            ], 
            'as': 'seller'
        }
    }, {
        '$lookup': {
            'from': 'advertising_accounts', 
            'localField': 'ad', 
            'foreignField': '_id', 
            'as': 'ad', 
            'pipeline': [
                {
                    '$project': {
                        'name': 1, 
                        '_id': 0
                    }
                }
            ]
        }
    }, {
        '$lookup': {
            'from': 'health', 
            'localField': '_id', 
            'foreignField': '_id', 
            'as': 'health', 
            'pipeline': [
                {
                    '$replaceRoot': {
                        'newRoot': {
                            'ahr': '$health.ahr', 
                            'violations': '$health.violation.value'
                        }
                    }
                }
            ]
        }
    }, {
        '$lookup': {
            'from': 'query_results', 
            'let': {
                'queryid': ObjectId('686750af5ec9b6bf57fe9060'), 
                'marketplace': '$_id'
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
                                        '$queryid', '$$queryid'
                                    ]
                                }, {
                                    '$eq': [
                                        '$collatetype', 'marketplace'
                                    ]
                                }
                            ]
                        }
                    }
                }, {
                    '$replaceRoot': {
                        'newRoot': {
                            'orders': '$data.orders.curr', 
                            'units': '$data.quantity.curr', 
                            'revenue': {
                                '$round': [
                                    '$data.revenue.curr', 0
                                ]
                            }, 
                            'roas': '$data.roas.curr'
                        }
                    }
                }
            ], 
            'as': 'sales'
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '_id': '$_id', 
                'countrycode': '$countrycode', 
                'marketplaceid': '$marketplaceid', 
                'createdat': '$createdat', 
                'storename': '$storename', 
                'status': '$status', 
                'plantype': '$plantype', 
                'dates': '$dates', 
                'lastrefresh': '$lastrefresh', 
                'createdat': '$createdat', 
                'seller': {
                    '$first': '$seller.name'
                }, 
                'ad': {
                    '$first': '$ad.name'
                }, 
                'health': {
                    '$first': '$health'
                }, 
                'sales': {
                    '$first': '$sales'
                }
            }
        }
    }])
    return pipeline