from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.core.vars import STRIPE_ENDPOINT_SECRET
import stripe
from uuid import UUID
from app.models.order import Order, OrderStatus

class StripeService:
    async def payment_webhook(request: Request, session: Session):
        payload = await request.body()
        event = None
        
        if STRIPE_ENDPOINT_SECRET:
            sig_header = request.headers.get("stripe-signature")
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
            except stripe.error.SignatureVerificationError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        if event["type"] == "checkout.session.completed":
            order_id = UUID(event['data']['object']['metadata']['order_id'])

            order = session.query(Order).filter(Order.id == order_id).first()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            order.status = OrderStatus.preparing
            session.commit()
