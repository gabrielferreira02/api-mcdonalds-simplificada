from app.schemas.order_schemas import CreateOrderSchema, CartStripeSchema, OrdersSchema, OrderItemSchema, OrderByIdSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.user import User
from app.core.stripe import client
from math import ceil
from uuid import UUID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class OrderService:
    def create_order(body: CreateOrderSchema, session: Session, user: User):
        if user.id != body.user:
            logger.warning(f"User {user.id} is not authorized to create order for user {body.user}")
            raise HTTPException(status_code=403, detail="You are not authorized to create order for this user")
        if len(body.items) == 0:
            logger.warning("No items in cart")
            raise HTTPException(status_code=400, detail="There are no items in cart")

        total_items = sum(item.quantity for item in body.items)
        if total_items > 15:
            logger.warning("Cart limit exceeded. Max 15 items permited")
            raise HTTPException(status_code=400, detail="Cart limit exceeded. Max 15 items permited" )

        user = session.query(User).filter(User.id == body.user).first()

        if not user:
            logger.warning(f"User not found with id: {body.user}")
            raise HTTPException(status_code=404, detail="User not found")

        if not user.address or not user.complement:
            logger.warning("Invalid address or complement. Please verify them")
            raise HTTPException(status_code=400, detail="Invalid address or complement. Please verify them")

        order = Order(
            user_id = user.id,
            address = user.address,
            complement = user.complement
        )

        session.add(order)
        session.flush()
        cart_items: list[CartStripeSchema] = []
        for item in body.items:
            if item.quantity <= 0:
                logger.warning("Invalid product quantity. Please verify them")
                raise HTTPException(status_code=400, detail="Products quantity must be greater than 0")

            product = session.query(Product).filter(Product.slug == item.slug).first()
            if not product or not product.is_active:
                logger.warning("Invalid product in cart")
                raise HTTPException(status_code=400, detail="There are invalid product in cart")
            
            order_item = OrderItem(
                order_id = order.id,
                product_id = product.id,
                quantity = item.quantity,
                unit_price = product.price
            )
            session.add(order_item)
            stripe_item = CartStripeSchema(
                name = product.name,
                image = product.image_url,
                quantity = item.quantity,
                price = product.price
            )
            cart_items.append(stripe_item)
        
        order.calculate_total()

        try:    
            logger.info("Creating checkout session")
            session_checkout = client.v1.checkout.sessions.create(
                params={
                    'success_url': 'http://localhost:4200/pagamentos/sucesso',
                    'cancel_url': 'http://localhost:8000/cancel',
                    'mode': 'payment',
                    'line_items': [
                        {
                            'price_data': {
                                'currency': 'brl',
                                'product_data': {
                                    'name': i.name,
                                    'images': [i.image],
                                },
                                'unit_amount': int(i.price * 100),
                            },
                            'quantity': i.quantity,
                        }
                        for i in cart_items
                    ],
                    "metadata": {"order_id": str(order.id)}
                },
            )
            
            order.payment_link = session_checkout.url
            session.commit()
            
            logger.info(f"Checkout session created for order: {order.id}")
            return {"payment_url": session_checkout.url}
        except Exception as e:
            session.rollback()
            logger.error(f"Error occurred while processing payment for order: {order.id}")
            print(str(e))
            raise HTTPException(status_code=500, detail="Error processing payment")

    def get_user_orders(id: UUID, page: int, session: Session, user: User):
        logger.info(f"Fetching orders for user: {user.id}")
        if user.id != id:
            logger.warning(f"User {user.id} is not authorized to view orders for user {id}")
            raise HTTPException(status_code=403, detail="You are not authorized to view orders for this user")
        if page <= 0:
            logger.warning(f"Invalid page provided: {page}")
            raise HTTPException(status_code=400, detail="Invalid page")
        limit = 10
        offset = (page - 1) * limit
        total = session.query(User).count()

        orders = (
            session.query(Order)
            .filter(Order.user_id == id)
            .order_by(Order.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all())
        
        logger.info(f"Fetched {len(orders)} orders for user: {user.id}")
        return OrdersSchema(
            orders = orders,
            page = page,
            total_pages = ceil(total / limit)
        )
    
    def get_order_by_id(id: UUID, session: Session, user: User):
        logger.info(f"Fetching order with id: {id}")
        order = session.query(Order).filter(Order.id == id).first()
        if not order:
            logger.warning(f"Order not found with id: {id}")
            raise HTTPException(status_code=404, detail="Order not found")
        if user.id != order.user_id and not user.is_admin:
            logger.warning(f"User {user.id} is not authorized to view order: {id}")
            raise HTTPException(status_code=403, detail="You are not authorized to view this order")
        items = (
            session.query(OrderItem, Product)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(OrderItem.order_id == id)
            .all())
        
        items_schema = [
            OrderItemSchema(
                name = product.name,
                quantity = item.quantity,
                price = item.unit_price,
                image = product.image_url
            )
            for item, product in items
        ]
        logger.info(f"Fetched order with id: {id} for user: {user.id}")
        return OrderByIdSchema(
            order = order,
            items = items_schema
        )

    def cancel_order(id: UUID, session: Session, user: User):
        order = session.query(Order).filter(Order.id == id).first()

        if not order:
            logger.warning(f"Order not found with id: {id}")
            raise HTTPException(status_code=404, detail="Order not found")
        if user.id != order.user_id and not user.is_admin:
            logger.warning(f"User {user.id} is not authorized to cancel order: {id}")
            raise HTTPException(status_code=403, detail="You are not authorized to cancel this order")
        
        if order.status == OrderStatus.pending or order.status == OrderStatus.preparing:
            order.status = OrderStatus.canceled
            order.updated_at = datetime.now()
            session.commit()
            logger.info(f"Order canceled: {id}")
            return
        else:
            logger.warning(f"Order {id} cannot be canceled")
            raise HTTPException(status_code=400, detail="Order cannot be canceled")
        