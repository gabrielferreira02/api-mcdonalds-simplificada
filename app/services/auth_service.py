from sqlalchemy.orm import Session
from app.schemas.auth_schemas import RegisterRequestSchema
from fastapi import HTTPException
from app.helpers.validate_cep import is_valid_cep
from app.helpers.validate_cpf import is_valid_cpf
from app.models.user import User
from app.core.security import pwd_context

class AuthService:
    def user_register(body: RegisterRequestSchema, session: Session):
        if not body.first_name:
            raise HTTPException(status_code=400, detail="Empty first name")
        if not body.last_name:
            raise HTTPException(status_code=400, detail="Empty last name")
        if not body.email:
            raise HTTPException(status_code=400, detail="Invalid email")
        if len(body.password) < 8:
            raise HTTPException(status_code=400, detail="Invalid password")
        if not body.cep:
            raise HTTPException(status_code=400, detail="Empty cep")
        if not body.complement:
            raise HTTPException(status_code=400, detail="Empty complement")
        if not body.cpf:
            raise HTTPException(status_code=400, detail="Empty first cpf")
        
        formated_cep = "".join(filter(str.isdigit, body.cep))
        formated_cpf = "".join(filter(str.isdigit, body.cpf))
        data = is_valid_cep(formated_cep)

        if data is False:
            raise HTTPException(status_code=400, detail="Invalid CEP")
        
        address = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}"
        
        if not is_valid_cpf(formated_cpf):
            raise HTTPException(status_code=400, detail="Invalid CPF")
        
        user = User(
            first_name = body.first_name,
            last_name = body.last_name,
            email = body.email,
            password = pwd_context.hash(body.password),
            cpf = formated_cpf,
            cep = formated_cep,
            address = address,
            complement = body.complement
        )

        session.add(user)
        session.commit()
        return user
        
