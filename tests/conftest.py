from app.models.user import User
from app.core.database import Base
from tests.test_database import engine, TestingSessionLocal
from uuid import uuid4
import pytest

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def create_user():
    def _create_user(session):
        user = User(
            first_name=f"first_name_{uuid4()}",
            last_name=f"last_name_{uuid4()}",
            email=f"{uuid4()}@email.com",
            cpf=f"cpf-{uuid4()}",
            cep=f"cep-{uuid4()}",
            address=f"address_{uuid4()}",
            complement=f"complement_{uuid4()}",
            password=f"12345678",
            is_admin=False
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    return _create_user