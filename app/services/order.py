from enum import Enum
from typing import Tuple, List
from app.dependencies import BaseService
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.orders import OrderCreateSchema, OrderFilter
from app.utils.constants import (
    CUSTOMER_NOT_FOUND,
    ERROR_MESSAGE,
    PRODUCT_NOT_FOUND,
)
from app.utils.logger import logger


class OrderStatus(str, Enum):
    """A status enum for orders"""

    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELED = "Canceled"


class OrderService(BaseService):
    """Order service"""

    def create_order(self, order: OrderCreateSchema) -> tuple[bool, str, int]:
        """Create a new order with proper validation and optimized queries."""
        try:
            with self.db.begin():  # Ensures atomic transaction
                # Check if customer exists
                customer = (
                    self.db.query(Customer)
                    .filter_by(id=order.customer_id)
                    .first()
                )
                if not customer:
                    return False, CUSTOMER_NOT_FOUND, 404

                # Fetch all product details in a single query
                product_ids = [item.product_id for item in order.items]
                products = (
                    self.db.query(Product)
                    .filter(Product.id.in_(product_ids))
                    .all()
                )
                product_map = {product.id: product for product in products}

                # Validate product and stock availability before creating order
                total_amount = 0
                for item in order.items:
                    product = product_map.get(item.product_id)
                    if not product:
                        return False, PRODUCT_NOT_FOUND, 404

                    if product.stock_quantity < item.quantity:
                        return (
                            False,
                            f"Insufficient stock for {product.name}",
                            400,
                        )
                    total_amount += item.quantity * item.price

                # Create new order
                new_order = Order(
                    customer_id=order.customer_id,
                    date=order.order_date,
                    total_amount=total_amount,
                    status=OrderStatus.PENDING,
                )
                self.db.add(new_order)
                self.db.flush()

                # Prepare order items and update stock
                order_items = [
                    OrderItem(
                        order_id=new_order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        price=item.price,
                    )
                    for item in order.items
                ]

                for item in order.items:
                    product_map[
                        item.product_id
                    ].stock_quantity -= item.quantity  # Deduct stock

                # Bulk insert order items
                self.db.bulk_save_objects(order_items)

                logger.info(
                    "Order created successfully with ID: %s", new_order.id
                )
                return True, "Order created successfully.", 201

        except Exception as e:
            self.db.rollback()
            logger.error(
                "Unexpected error creating order: %s", e, exc_info=True
            )
            return False, ERROR_MESSAGE, 500

    def get_orders(
        self, filters: OrderFilter
    ) -> Tuple[bool, str, List[Order]]:
        """Retrieve orders with filtering"""
        try:
            orders = self.db.query(Order)

            if filters.status is not None:
                orders = orders.filter(Order.status == filters.status)

            if filters.customer_id is not None:
                orders = orders.filter(
                    Order.customer_id == filters.customer_id
                )

            if filters.min_price is not None:
                orders = orders.filter(Order.total_amount >= filters.min_price)

            if filters.max_price is not None:
                orders = orders.filter(Order.total_amount <= filters.max_price)

            logger.info("Order list retrieved successfully")
            return True, "Order list retrieved successfully", orders
        except Exception as e:
            logger.error("Error retrieving order list : %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def get_order(self, order_id: int):
        """Retrieve a specific order"""
        try:
            if order_id <= 0:
                return False, "Invalid order ID", 400
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False, "Order not found", 404
            return True, "Order retrieved successfully", order
        except Exception as e:
            logger.error("Error retrieving order: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def delete_order(self, order_id: int) -> tuple[bool, str, int]:
        """
        Deletes an order, restores stock,
        and ensures product completion state is respected.
        """
        try:
            if order_id <= 0:
                return False, "Invalid order ID", 400

            order = self.db.query(Order).filter_by(id=order_id).first()
            if not order:
                return False, "Order not found", 404

            # Restore product stock before deleting order
            for item in order.order_items:
                product = (
                    self.db.query(Product)
                    .filter_by(id=item.product_id)
                    .first()
                )
                if product:
                    product.stock_quantity += item.quantity

            # Delete order (OrderItems will be auto-deleted due to cascade)
            self.db.delete(order)
            self.db.flush()

            logger.info("Order deleted successfully")
            return True, "Order deleted successfully", 200

        except Exception as e:
            self.db.rollback()
            logger.error("Error deleting order: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def get_customer_orders(self, customer_id: int):
        """Get customer orders"""
        try:
            orders = (
                self.db.query(Order)
                .filter(Order.customer_id == customer_id)
                .all()
            )
            return True, "Customer orders retrieved successfully", orders
        except Exception as e:
            logger.error(
                "Error retrieving customer orders: %s", e, exc_info=True
            )
            return False, ERROR_MESSAGE, 500
