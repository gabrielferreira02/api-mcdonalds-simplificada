from app.core.database import Base
from sqlalchemy import Column, UUID, String
import uuid

class Category(Base):
    __tablename__ = "categories_db"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column("name", String, nullable=False)
    slug = Column("slug", String, nullable=False, unique=True)
    image_url = Column("image_url", String, nullable=True)
    image_path = Column("image_path", String, nullable=True)