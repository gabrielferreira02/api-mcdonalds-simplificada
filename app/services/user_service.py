from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UpdateUsernameSchema, UpdateEmailSchema, UpdatePasswordSchema, UpdateAddressSchema
from fastapi import HTTPException
from app.core.security import pwd_context
from app.helpers.validate_cep import is_valid_cep

class UserService:
    def update_username(user: User, data: UpdateUsernameSchema, session: Session):
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.first_name = data.first_name
        user.last_name = data.last_name
        session.commit()
        return user
    
    def update_email(user: User, data: UpdateEmailSchema, session: Session):
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        exist_email = session.query(User).filter(User.email == data.email).first()
        if exist_email:
            raise HTTPException(status_code=400, detail="Email already in use")
        
        user.email = data.email
        session.commit()
        return user
    
    def update_password(user: User, data: UpdatePasswordSchema, session: Session):
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if len(data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        user.password = pwd_context.hash(data.password)
        session.commit()
        return user
    
    def update_address(user: User, data: UpdateAddressSchema, session: Session):
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        formated_cep = "".join(filter(str.isdigit, data.cep))
        new_cep_data = is_valid_cep(formated_cep)

        if new_cep_data is False:
            raise HTTPException(status_code=400, detail="Invalid CEP")
        
        address = f"{new_cep_data['logradouro']}, {new_cep_data['bairro']}, {new_cep_data['localidade']}"
        user.cep = formated_cep
        user.address = address
        user.complement = data.complement
        session.commit()
        return user
    

