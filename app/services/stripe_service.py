from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.core.vars import STRIPE_ENDPOINT_SECRET
import stripe
from uuid import UUID
from app.models.order import Order, OrderStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class StripeService:
    async def payment_webhook(request: Request, session: Session):
        payload = await request.body()
        event = None
        
        if STRIPE_ENDPOINT_SECRET:
            sig_header = request.headers.get("stripe-signature")
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
            except stripe.error.SignatureVerificationError as e:
                logger.warning(f"Invalid signature for webhook event: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        
        if event["type"] == "checkout.session.completed":
            order_id = UUID(event['data']['object']['metadata']['order_id'])

            order = session.query(Order).filter(Order.id == order_id).first()

            if not order:
                logger.warning(f"Order with ID {order_id} not found when trying to update status")
                raise HTTPException(status_code=404, detail="Order not found")
            order.status = OrderStatus.preparing

        if event["type"] == "checkout.session.expired":
            order_id = str(event['data']['object']['metadata']['order_id'])

            order = session.query(Order).filter(Order.id == order_id).first()

            if not order:
                logger.warning(f"Order with ID {order_id} not found when trying to update status")
                raise HTTPException(status_code=404, detail="Order not found")

            order.status = OrderStatus.canceled
            
        logger.info(f"Updating order {order_id} status to {order.status}")
        order.updated_at = datetime.now()
        session.commit()
        logger.info(f"Order {order_id} status updated successfully")
