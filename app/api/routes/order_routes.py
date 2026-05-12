from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_session
from app.services.order_service import OrderService
from app.schemas.order_schemas import CreateOrderSchema, OrdersSchema
from uuid import UUID
order_router = APIRouter(prefix="/orders", tags=["Orders"])

@order_router.post("", status_code=201)
async def create_order(body: CreateOrderSchema, session: Session = Depends(get_session)):
    return OrderService.create_order(body, session)

@order_router.get("/user/{id}")
async def get_user_orders(id: UUID, page: int = Query(1) , session: Session = Depends(get_session)):
    return OrderService.get_user_orders(id, page, session)

@order_router.get("/{id}")
async def get_order_by_id(id: UUID, session: Session = Depends(get_session)):
    return OrderService.get_order_by_id(id, session)

@order_router.put("/{id}/cancel", status_code=204)
async def cancel_order(id: UUID, session: Session = Depends(get_session)):
    return OrderService.cancel_order(id, session)

# Only for tests
@order_router.get("/success")
async def order_success():
    return "Compra efetuada com sucesso"   