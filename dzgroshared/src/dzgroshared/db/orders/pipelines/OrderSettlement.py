from bson import ObjectId
from dzgroshared.db.orders.model import OrderPaymentRequest


def pipeline(marketplace: ObjectId, req: OrderPaymentRequest) -> list[dict]:
    """
    Aggregation pipeline to get orders with settlement details
    """
    pipeline_stages: list[dict] = []

    # 1. Match orders by marketplace
    match_stage = {
        '$match': {
            'marketplace': marketplace,
            'orderstatus': {'$ne': 'Cancelled'}
        }
    }

    # Add date filter if provided
    if req.dates:
        match_stage['$match']['orderdate'] = {
            '$gte': req.dates.startdate,
            '$lte': req.dates.enddate
        }

    pipeline_stages.append(match_stage)

    # 2. Sort by order date descending
    pipeline_stages.append({
        '$sort': {'orderdate': -1}
    })

    # 3. Apply pagination
    pipeline_stages.extend([
        {'$skip': req.paginator.skip},
        {'$limit': req.paginator.limit}
    ])

    # 4. Lookup settlements
    pipeline_stages.append({
        '$lookup': {
            'from': 'settlements',
            'let': {'orderId': '$orderid'},
            'pipeline': [
                {
                    '$match': {
                        '$expr': {'$eq': ['$orderid', '$$orderId']},
                        'marketplace': marketplace
                    }
                }
            ],
            'as': 'settlements'
        }
    })

    # 5. Lookup order items
    pipeline_stages.append({
        '$lookup': {
            'from': 'order_items',
            'let': {'orderId': '$_id'},
            'pipeline': [
                {
                    '$match': {
                        '$expr': {'$eq': ['$order', '$$orderId']},
                        'marketplace': marketplace
                    }
                }
            ],
            'as': 'orderItems'
        }
    })

    # 6. Lookup product images
    pipeline_stages.append({
        '$lookup': {
            'from': 'products',
            'localField': 'orderItems.sku',
            'foreignField': 'sku',
            'as': 'products'
        }
    })

    # 7. Add computed fields
    pipeline_stages.append({
        '$addFields': {
            # Calculate order total from order items
            'orderTotal': {'$sum': '$orderItems.revenue'},

            # Calculate settlement total
            'settlementTotal': {'$sum': '$settlements.amount'},

            # Calculate payout percentage
            'payoutPercentage': {
                '$cond': [
                    {'$gt': [{'$sum': '$orderItems.revenue'}, 0]},
                    {
                        '$multiply': [
                            {
                                '$divide': [
                                    {'$sum': '$settlements.amount'},
                                    {'$sum': '$orderItems.revenue'}
                                ]
                            },
                            100
                        ]
                    },
                    0
                ]
            }
        }
    })

    # 8. Project final structure (will be enhanced with status logic in controller)
    pipeline_stages.append({
        '$project': {
            'orderid': 1,
            'orderdate': 1,
            'orderstatus': 1,
            'orderTotal': 1,
            'settlementTotal': 1,
            'payoutPercentage': 1,
            'settlements': 1,
            'orderItems': 1,
            'products': 1
        }
    })

    return pipeline_stages
