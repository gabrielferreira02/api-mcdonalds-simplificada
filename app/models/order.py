from app.core.database import Base
from sqlalchemy import Column, UUID, Float, String, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

class OrderStatus(str, Enum):
    pending = "Pendente"
    preparing = "Preparando"
    in_transit = "A caminho"
    canceled = "Cancelado"
    delivered = "Entregue"


class Order(Base):
    __tablename__ = "orders_db"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column("user_id", ForeignKey("users_db.id"), nullable=False)
    total = Column("total", Float, default=0, nullable=False)
    status = Column("status", SqlEnum(OrderStatus), default=OrderStatus.pending)
    address = Column("address", String, nullable=False)
    complement = Column("complement", String, nullable=False)
    payment_link = Column("payment_link", String, nullable=False, default="")
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
    items = relationship("OrderItem", cascade="all, delete")

    def calculate_total(self):
        self.total = sum(item.quantity * item.unit_price for item in self.items)