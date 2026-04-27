from app.core.database import Base
from sqlalchemy import Column, UUID, String, DateTime, Boolean
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users_db"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column("first_name", String, nullable=False)
    last_name = Column("last_name", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True)
    password = Column("password", String, nullable=False)
    cpf = Column("cpf", String, nullable=False)
    cep = Column("cep", String, nullable=False)
    address = Column("address", String, nullable=False)
    complement = Column("complement", String, nullable=False)
    is_admin = Column("is_admin", Boolean, default=False, nullable=False)
    created_at = Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now())