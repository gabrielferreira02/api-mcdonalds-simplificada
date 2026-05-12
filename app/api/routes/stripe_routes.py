from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.deps import get_session
from sqlalchemy.orm import Session
from app.services.stripe_service import StripeService                    

stripe_router = APIRouter(prefix="/stripe", tags=["Stripe Integrations"])

@stripe_router.post("/webhook")
async def stripe_payments_webhook(request: Request, session: Session = Depends(get_session)):
    await StripeService.payment_webhook(request, session)            