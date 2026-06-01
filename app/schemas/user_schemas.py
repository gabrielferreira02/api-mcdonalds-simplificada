from pydantic import BaseModel
from uuid import UUID

class UpdateUsernameSchema(BaseModel):
    first_name: str
    last_name: str

class UpdateEmailSchema(BaseModel):    
    email: str

class UpdatePasswordSchema(BaseModel):
    password: str 

class UpdateAddressSchema(BaseModel):
    cep: str
    complement: str

class UserResponseSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    cpf: str
    cep: str
    address: str
    complement: str
    is_admin: bool