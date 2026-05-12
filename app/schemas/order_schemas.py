from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.order import OrderStatus

class OrderItems(BaseModel):
    slug: str
    quantity: int

class CreateOrderSchema(BaseModel):
    items: list[OrderItems]
    user: UUID

class CartStripeSchema(BaseModel):
    name: str
    quantity: int
    price: float
    image: str

class OrderResponseSchema(BaseModel):
    id: UUID
    total: float
    updated_at: datetime
    status: OrderStatus
    address: str
    complement: str
    payment_link: str

    class Config:
        from_attributes = True

class OrdersSchema(BaseModel):
    orders: list[OrderResponseSchema]
    page: int
    total_pages: int

    class Config:
        from_attributes = True

class OrderItemSchema(BaseModel):
    name: str
    quantity: int
    price: float
    image: str

class OrderByIdSchema(BaseModel):
    order: OrderResponseSchema
    items: list[OrderItemSchema]
    class Config:
        from_attributes = True