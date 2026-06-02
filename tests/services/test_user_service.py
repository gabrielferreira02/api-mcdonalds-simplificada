import pytest
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user_schemas import UpdateAddressSchema, UpdateUsernameSchema, UpdateEmailSchema, UpdatePasswordSchema
from fastapi import HTTPException

def mock_is_valid_cep(cep):
    return {
        "logradouro": "Mock Street",
        "bairro": "Mock Neighborhood",
        "localidade": "Mock City",
    }

def test_update_username_success(db_session, create_user):
    user = create_user(db_session)
    data = UpdateUsernameSchema(first_name="NewFirstName", last_name="NewLastName")
    updated_user = UserService.update_username(user, data, db_session)
    assert updated_user.first_name == "NewFirstName"
    assert updated_user.last_name == "NewLastName"

def test_update_username_with_invalid_first_name(db_session, create_user):
    user = create_user(db_session)
    data = UpdateUsernameSchema(first_name="", last_name="NewLastName")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_username(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "First name and last name cannot be empty"

def test_update_username_with_invalid_last_name(db_session, create_user):
    user = create_user(db_session)
    data = UpdateUsernameSchema(first_name="NewFirstName", last_name="")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_username(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "First name and last name cannot be empty"

def test_update_username_with_nonexistent_user(db_session):
    data = UpdateUsernameSchema(first_name="NewFirstName", last_name="NewLastName")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_username(None, data, db_session)
    assert exc_info.value.status_code == 404 
    assert exc_info.value.detail == "User not found"

def test_update_user_email_success(db_session, create_user):
    user = create_user(db_session)
    data = UpdateEmailSchema(email="newemail@example.com")
    updated_user = UserService.update_email(user, data, db_session)
    assert updated_user.email == "newemail@example.com"

def test_update_user_email_with_invalid_email(db_session, create_user):
    user = create_user(db_session)
    data = UpdateEmailSchema(email="")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_email(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email cannot be empty"

def test_update_user_email_with_existing_email(db_session, create_user):
    user1 = create_user(db_session)
    user1.email = "existing@example.com"
    user2 = create_user(db_session)
    db_session.commit()
    data = UpdateEmailSchema(email="existing@example.com")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_email(user2, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already in use"

def test_update_user_email_with_nonexistent_user(db_session):
    data = UpdateEmailSchema(email="newemail@example.com")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_email(None, data, db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

def test_update_user_password_success(db_session, create_user):
    user = create_user(db_session)
    data = UpdatePasswordSchema(password="newpassword123")
    updated_user = UserService.update_password(user, data, db_session)
    assert updated_user.password != "newpassword123"

def test_update_user_password_with_invalid_password(db_session, create_user):
    user = create_user(db_session)
    data = UpdatePasswordSchema(password="")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_password(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password cannot be empty"

def test_update_user_password_with_short_password(db_session, create_user):
    user = create_user(db_session)
    data = UpdatePasswordSchema(password="short")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_password(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must be at least 8 characters long"

def test_update_user_password_with_nonexistent_user(db_session):
    data = UpdatePasswordSchema(password="newpassword123")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_password(None, data, db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

def test_update_user_address_success(db_session, create_user, monkeypatch):
    monkeypatch.setattr("app.services.user_service.is_valid_cep", mock_is_valid_cep)
    user = create_user(db_session)
    data = UpdateAddressSchema(cep="12345-678", complement="Apt 1")
    updated_user = UserService.update_address(user, data, db_session)
    assert updated_user.cep == "".join(filter(str.isdigit, data.cep))
    assert updated_user.address == "Mock Street, Mock Neighborhood, Mock City"
    assert updated_user.complement == "Apt 1"

def test_update_user_address_with_invalid_cep(db_session, create_user, monkeypatch):
    monkeypatch.setattr("app.services.user_service.is_valid_cep", lambda cep: False)
    user = create_user(db_session)
    data = UpdateAddressSchema(cep="invalid-cep", complement="Apt 1")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_address(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid CEP"

def test_update_user_address_with_empty_complement(db_session, create_user):
    user = create_user(db_session)
    data = UpdateAddressSchema(cep="12345-678", complement="")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_address(user, data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Complement cannot be empty"

def test_update_user_address_with_nonexistent_user(db_session, monkeypatch):
    monkeypatch.setattr("app.services.user_service.is_valid_cep", mock_is_valid_cep)
    data = UpdateAddressSchema(cep="12345-678", complement="Apt 1")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_address(None, data, db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"