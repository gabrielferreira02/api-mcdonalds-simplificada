from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_session, verify_token
from app.services.order_service import OrderService
from app.schemas.order_schemas import CreateOrderSchema, OrdersSchema
from uuid import UUID
from app.models.user import User

order_router = APIRouter(prefix="/orders", tags=["Orders"])

@order_router.post("", status_code=201)
async def create_order(body: CreateOrderSchema,
                       session: Session = Depends(get_session),
                       user: User = Depends(verify_token)):
    return OrderService.create_order(body, session, user)

@order_router.get("/user/{id}")
async def get_user_orders(id: UUID,
                          page: int = Query(1),
                          session: Session = Depends(get_session),
                          user: User = Depends(verify_token)):
    return OrderService.get_user_orders(id, page, session, user)

@order_router.get("/{id}")
async def get_order_by_id(id: UUID,
                          session: Session = Depends(get_session),
                          user: User = Depends(verify_token)):
    return OrderService.get_order_by_id(id, session, user)

@order_router.put("/{id}/cancel", status_code=204)
async def cancel_order(id: UUID,
                       session: Session = Depends(get_session),
                       user: User = Depends(verify_token)):
    return OrderService.cancel_order(id, session, user) 