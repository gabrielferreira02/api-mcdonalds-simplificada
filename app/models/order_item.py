from app.core.database import Base
from sqlalchemy import Column, UUID, Integer, ForeignKey, Float
import uuid

class OrderItem(Base):
    __tablename__ = "order_items_db"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    order_id = Column("order_id", ForeignKey("orders_db.id"), nullable=False)
    product_id = Column("product_id", ForeignKey("products_db.id"), nullable=False)
    unit_price = Column("unit_price", Float, nullable=False)
    quantity = Column("quantity", Integer, nullable=False)