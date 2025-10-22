from bson import ObjectId
from datetime import datetime, timedelta
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.model import Sort, Paginator
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.orders.model import (
    OrderPaymentRequest, OrderPaymentList, OrderPaymentFacets,
    PaymentStatus, PaymentStatusFacet, ShippingStatus, OrderItemSettlement,
    SettlementAmountType, NonSkuSettlement, OrderPaymentDetail
)
from dzgroshared.db.orders.pipelines.OrderSettlement import pipeline

class OrdersHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ORDERS), marketplace=client.marketplaceId)

    async def getOrderPayments(self, req: OrderPaymentRequest) -> OrderPaymentList:
        """Get orders with payment/settlement details"""

        # Run aggregation pipeline
        results = await self.db.aggregate(
            pipeline(self.client.marketplaceId, req)
        )

        # Get last settlement date for marketplace
        last_settlement_date = await self._getLastSettlementDate()

        # Process results and calculate statuses
        processed_orders = []
        for order in results:
            # Calculate payment status
            payment_status = self._calculatePaymentStatus(
                order, last_settlement_date
            )

            # Calculate shipping status
            shipping_status = self._calculateShippingStatus(order)

            # Process SKU-level settlements
            items = self._processOrderItems(order)

            # Process non-SKU settlements
            non_sku_settlements = self._processNonSkuSettlements(order)

            processed_orders.append(OrderPaymentDetail(
                _id=str(order['_id']),
                orderid=order['orderid'],
                orderdate=order['orderdate'],
                orderstatus=order['orderstatus'],
                paymentStatus=payment_status,
                shippingStatus=shipping_status,
                orderTotal=order['orderTotal'],
                settlementTotal=order['settlementTotal'],
                payoutPercentage=round(order['payoutPercentage'], 2),
                items=items,
                nonSkuSettlements=non_sku_settlements
            ))

        # Get count on first page only
        count = None
        if req.paginator.skip == 0:
            count = await self._getOrderPaymentsCount(req)

        return OrderPaymentList(count=count, data=processed_orders)

    async def getOrderPaymentFacets(self, req: OrderPaymentRequest) -> OrderPaymentFacets:
        """Get facet counts by payment status"""

        # Get all orders (no pagination for facets)
        temp_req = OrderPaymentRequest(
            dates=req.dates,
            paginator=Paginator(skip=0, limit=999999)
        )

        results = await self.db.aggregate(
            pipeline(self.client.marketplaceId, temp_req)
        )

        last_settlement_date = await self._getLastSettlementDate()

        # Calculate statuses and count
        status_counts = {
            PaymentStatus.PAID: 0,
            PaymentStatus.UNPAID: 0,
            PaymentStatus.PENDING_SETTLEMENT: 0,
            PaymentStatus.OVERDUE: 0
        }

        for order in results:
            status = self._calculatePaymentStatus(order, last_settlement_date)
            if status:
                status_counts[status] += 1

        # Build response
        by_status: list[PaymentStatusFacet] = [
            PaymentStatusFacet(status=status, count=count)
            for status, count in status_counts.items()
        ]

        total = sum(status_counts.values())

        return OrderPaymentFacets(total=total, byStatus=by_status)

    def _calculatePaymentStatus(self, order: dict, last_settlement_date: datetime | None) -> PaymentStatus | None:
        """Calculate payment status based on business rules"""

        # None if order is cancelled
        if order['orderstatus'].upper() == 'CANCELLED':
            return None

        # PAID if settlements exist for this order
        if order.get('settlements') and len(order['settlements']) > 0:
            return PaymentStatus.PAID

        order_date = order['orderdate']
        current_date = datetime.utcnow()

        # PENDING_SETTLEMENT if order date is after last settlement date
        if last_settlement_date and order_date > last_settlement_date:
            return PaymentStatus.PENDING_SETTLEMENT

        # OVERDUE if order date is before 60 days of current date
        sixty_days_ago = current_date - timedelta(days=60)
        if order_date < sixty_days_ago:
            return PaymentStatus.OVERDUE

        # UNPAID if none of above fits
        return PaymentStatus.UNPAID

    def _calculateShippingStatus(self, order: dict) -> ShippingStatus | None:
        """Calculate shipping status based on refunds"""

        # None if order is cancelled
        if order['orderstatus'].upper() == 'CANCELLED':
            return None

        settlements = order.get('settlements', [])

        # Get unique SKUs that have refunds
        skus_with_refunds = set()
        total_skus = set()

        for settlement in settlements:
            if settlement.get('sku'):
                total_skus.add(settlement['sku'])
                if settlement.get('transactiontype') == 'Refund':
                    skus_with_refunds.add(settlement['sku'])

        # If no SKUs, consider as DELIVERED
        if len(total_skus) == 0:
            return ShippingStatus.DELIVERED

        # If all SKUs have refunds
        if len(skus_with_refunds) == len(total_skus):
            return ShippingStatus.RETURNED

        # If some SKUs have refunds
        if len(skus_with_refunds) > 0:
            return ShippingStatus.PARTIAL_RETURNED

        # No refunds
        return ShippingStatus.DELIVERED

    def _processOrderItems(self, order: dict) -> list[OrderItemSettlement]:
        """Process order items with SKU-level settlements"""

        items = []
        order_items = order.get('orderItems', [])
        settlements = order.get('settlements', [])
        products = order.get('products', [])

        for item in order_items:
            sku = item.get('sku')

            # Get product image
            image = None
            for product in products:
                if product.get('sku') == sku:
                    images = product.get('images', [])
                    if images and len(images) > 0:
                        image = images[0]
                    break

            # Get settlements for this SKU
            sku_settlements = [
                s for s in settlements
                if s.get('sku') == sku and s.get('orderid') == order['orderid']
            ]

            # Group by amountdescription
            amount_types_map = {}
            for settlement in sku_settlements:
                desc = settlement.get('amountdescription', 'Unknown')
                trans_type = settlement.get('transactiontype', 'Order')

                if desc not in amount_types_map:
                    amount_types_map[desc] = {
                        'amountdescription': desc,
                        'orderAmount': 0,
                        'refundAmount': 0
                    }

                if trans_type == 'Refund':
                    amount_types_map[desc]['refundAmount'] += settlement.get('amount', 0)
                else:
                    amount_types_map[desc]['orderAmount'] += settlement.get('amount', 0)

            # Convert to list
            amount_types = [SettlementAmountType(**amt) for amt in amount_types_map.values()]

            items.append(OrderItemSettlement(
                sku=sku,
                asin=item.get('asin'),
                image=image,
                amountTypes=amount_types
            ))

        return items

    def _processNonSkuSettlements(self, order: dict) -> NonSkuSettlement | None:
        """Process non-SKU settlements (shipping, fees, etc.)"""

        settlements = order.get('settlements', [])

        # Get settlements without SKU
        non_sku_settlements = [
            s for s in settlements
            if not s.get('sku') and s.get('orderid') == order['orderid']
        ]

        if len(non_sku_settlements) == 0:
            return None

        # Group by amountdescription
        amount_types_map = {}
        for settlement in non_sku_settlements:
            desc = settlement.get('amountdescription', 'Unknown')
            trans_type = settlement.get('transactiontype', 'Order')

            if desc not in amount_types_map:
                amount_types_map[desc] = {
                    'amountdescription': desc,
                    'orderAmount': 0,
                    'refundAmount': 0
                }

            if trans_type == 'Refund':
                amount_types_map[desc]['refundAmount'] += settlement.get('amount', 0)
            else:
                amount_types_map[desc]['orderAmount'] += settlement.get('amount', 0)

        # Convert to list
        amount_types = [SettlementAmountType(**amt) for amt in amount_types_map.values()]

        return NonSkuSettlement(amountTypes=amount_types)

    async def _getLastSettlementDate(self) -> datetime | None:
        """Get the last settlement date for the marketplace"""

        settlements_db = DbManager(
            self.client.db.database.get_collection(CollectionType.SETTLEMENTS),
            marketplace=self.client.marketplaceId
        )

        results = await settlements_db.find(
            filterDict={},
            sort=Sort(field='depositdate', order=-1),
            limit=1
        )

        if results and len(results) > 0:
            return results[0].get('depositdate')

        return None

    async def _getOrderPaymentsCount(self, req: OrderPaymentRequest) -> int:
        """Get total count of orders matching filters"""

        filter_dict: dict = {'orderstatus': {'$ne': 'Cancelled'}}

        if req.dates:
            filter_dict['orderdate'] = {
                '$gte': req.dates.startdate,
                '$lte': req.dates.enddate
            }

        return await self.db.count(filter_dict)


