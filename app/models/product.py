from app.core.database import Base
from sqlalchemy import Column, UUID, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

class Product(Base):
    __tablename__ = "products_db"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column("name", String, nullable=False)
    slug = Column("slug", String, nullable=False, unique=True)
    description = Column("description", Text, nullable=False)
    category_id = Column("category_id", ForeignKey("categories_db.id"), nullable=True)
    category = relationship("Category")
    price = Column("price", Float, nullable=False)
    image_url = Column("image_url", String, nullable=True)
    image_path = Column("image_path", String, nullable=True)
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False)