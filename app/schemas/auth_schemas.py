from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class RegisterRequestSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    cep: str
    cpf: str
    complement: str

class RegisterResponseSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    cep: str
    address: str
    cpf: str
    complement: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

class LoginRequestSchema(BaseModel):
    email: str
    password: str

class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str