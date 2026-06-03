import pytest
from app.services.auth_service import AuthService  
from app.models.user import User
from app.schemas.auth_schemas import LoginRequestSchema, RegisterRequestSchema, LoginResponseSchema
from fastapi import HTTPException

def test_login_success(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    monkeypatch.setattr("app.services.auth_service.pwd_context.verify", lambda plain, hashed: True)
    body = LoginRequestSchema(email=user.email, password=user.password)
    response = AuthService.login(body, db_session)
    assert response is not None

def test_login_failure_with_wrong_password(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    monkeypatch.setattr("app.services.auth_service.pwd_context.verify", lambda plain, hashed: False)
    body = LoginRequestSchema(email=user.email, password="wrongpassword")
    with pytest.raises(HTTPException) as exc_info:
        AuthService.login(body, db_session)
    assert exc_info.value.detail == "Invalid email or password"

def test_register_success(db_session, monkeypatch):
    monkeypatch.setattr("app.services.auth_service.is_valid_cep", lambda cep: {"logradouro": "Test Street", "bairro": "Test Neighborhood", "localidade": "Test City"})
    monkeypatch.setattr("app.services.auth_service.is_valid_cpf", lambda cpf: True)
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="12345-678",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    response = AuthService.user_register(body, db_session)
    assert response.email == "john.doe@example.com"
    assert response.first_name == "John"
    assert response.last_name == "Doe"

def test_register_failure_with_invalid_cep(db_session, monkeypatch):
    monkeypatch.setattr("app.services.auth_service.is_valid_cep", lambda cep: False)
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="invalid-cep",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Invalid CEP"   

def test_register_failure_with_invalid_cpf(db_session, monkeypatch):
    monkeypatch.setattr("app.services.auth_service.is_valid_cep", lambda cep: {"logradouro": "Test Street", "bairro": "Test Neighborhood", "localidade": "Test City"})
    monkeypatch.setattr("app.services.auth_service.is_valid_cpf", lambda cpf: False)
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="12345-678",
        cpf="invalid-cpf",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Invalid CPF"

def test_register_failure_with_empty_fields(db_session):
    body = RegisterRequestSchema(
        first_name="",
        last_name="",
        email="",
        password="",
        cep="",
        cpf="",
        complement=""
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Empty first name"

def test_register_failure_with_short_password(db_session):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="short",
        cep="12345-678",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Invalid password"

def test_register_failure_with_invalid_email(db_session, monkeypatch):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="",
        password="password123",
        cep="12345-678",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Invalid email"

def test_register_failure_with_empty_complement(db_session):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="12345-678",
        cpf="123.456.789-00",
        complement=""
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Empty complement"

def test_register_failure_with_empty_cpf(db_session):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="12345-678",
        cpf="",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Empty cpf"

def test_register_failure_with_empty_cep(db_session):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Empty cep"

def test_register_failure_with_empty_last_name(db_session):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="",
        email="john.doe@example.com",
        password="password123",
        cep="12345-678",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Empty last name"

def test_register_failure_with_empty_email(db_session):
    body = RegisterRequestSchema(
        first_name="John",
        last_name="Doe",
        email="",
        password="password123",
        cep="12345-678",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Invalid email"

def test_register_failure_with_empty_first_name(db_session):
    body = RegisterRequestSchema(
        first_name="",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        cep="12345-678",
        cpf="123.456.789-00",
        complement="Apt 101"
    )
    with pytest.raises(HTTPException) as exc_info:
        AuthService.user_register(body, db_session)
    assert exc_info.value.detail == "Empty first name"