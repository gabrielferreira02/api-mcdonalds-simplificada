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

class OrderService:
    def create_order(body: CreateOrderSchema, session: Session):
        if len(body.items) == 0:
            raise HTTPException(status_code=400, detail="There are no items in cart")

        total_items = sum(item.quantity for item in body.items)
        if total_items > 15:
            raise HTTPException(status_code=400, detail="Cart limit exceeded. Max 15 items permited" )

        user = session.query(User).filter(User.id == body.user).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.address or not user.complement:
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
                raise HTTPException(status_code=400, detail="Products quantity must be greater than 0")

            product = session.query(Product).filter(Product.slug == item.slug).first()
            if not product or not product.is_active:
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
            
            session_checkout = client.v1.checkout.sessions.create(
                params={
                    'success_url': 'http://localhost:8000/orders/success',
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
            
            return {"payment_url": session_checkout.url}
        except Exception as e:
            session.rollback()
            print(str(e))
            raise HTTPException(status_code=500, detail="Error processing payment")

    def get_user_orders(id: UUID, page: int, session: Session):
        if page <= 0:
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
        
        return OrdersSchema(
            orders = orders,
            page = page,
            total_pages = ceil(total / limit)
        )
    
    def get_order_by_id(id: UUID, session: Session):
        order = session.query(Order).filter(Order.id == id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
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
        return OrderByIdSchema(
            order = order,
            items = items_schema
        )

    def cancel_order(id: UUID, session: Session):
        order = session.query(Order).filter(Order.id == id).first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status == OrderStatus.pending or order.status == OrderStatus.preparing:
            order.status = OrderStatus.canceled
            order.updated_at = datetime.now()
            session.commit()
            return
        else:
            raise HTTPException(status_code=400, detail="Order cannot be canceled")
        