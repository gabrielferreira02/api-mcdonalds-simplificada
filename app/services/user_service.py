from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UpdateUsernameSchema, UpdateEmailSchema, UpdatePasswordSchema, UpdateAddressSchema
from fastapi import HTTPException
from app.core.security import pwd_context
from app.helpers.validate_cep import is_valid_cep
import logging

logger = logging.getLogger(__name__)

class UserService:
    def update_username(user: User, data: UpdateUsernameSchema, session: Session):
        if not data.first_name.strip() or not data.last_name.strip():
            logger.warning(f"Invalid first name or last name provided when trying to update username for user with ID {user.id}")
            raise HTTPException(status_code=400, detail="First name and last name cannot be empty")
        
        if not user:
            logger.warning(f"User with ID {user.id} not found when trying to update username")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Updating username for user with ID {user.id}")
        user.first_name = data.first_name
        user.last_name = data.last_name
        session.commit()
        logger.info(f"Username updated successfully for user with ID {user.id}")
        return user
    
    def update_email(user: User, data: UpdateEmailSchema, session: Session):
        if not data.email.strip():
            logger.warning(f"Invalid email provided when trying to update email for user with ID {user.id}")
            raise HTTPException(status_code=400, detail="Email cannot be empty")
        
        if not user:
            logger.warning(f"User with ID {user.id} not found when trying to update email")
            raise HTTPException(status_code=404, detail="User not found")
        
        exist_email = session.query(User).filter(User.email == data.email).first()
        if exist_email:
            logger.warning(f"Email {data.email} is already in use when trying to update email for user with ID {user.id}")
            raise HTTPException(status_code=400, detail="Email already in use")
        
        logger.info(f"Updating email for user with ID {user.id}")
        user.email = data.email
        session.commit()
        logger.info(f"Email updated successfully for user with ID {user.id}")
        return user
    
    def update_password(user: User, data: UpdatePasswordSchema, session: Session):
        if not data.password.strip():
            logger.warning(f"Invalid password provided when trying to update password for user with ID {user.id}")
            raise HTTPException(status_code=400, detail="Password cannot be empty")
        
        if not user:
            logger.warning(f"User with ID {user.id} not found when trying to update password")
            raise HTTPException(status_code=404, detail="User not found")
        
        if len(data.password) < 8:
            logger.warning(f"Password for user with ID {user.id} is too short")
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        logger.info(f"Updating password for user with ID {user.id}")
        user.password = pwd_context.hash(data.password)
        session.commit()
        logger.info(f"Password updated successfully for user with ID {user.id}")
        return user
    
    def update_address(user: User, data: UpdateAddressSchema, session: Session):
        if not data.cep.strip():
            logger.warning(f"Invalid CEP provided when trying to update address for user with ID {user.id}")
            raise HTTPException(status_code=400, detail="CEP cannot be empty")
        
        if not data.complement.strip():
            logger.warning(f"Invalid complement provided when trying to update address for user with ID {user.id}")
            raise HTTPException(status_code=400, detail="Complement cannot be empty")
        
        if not user:
            logger.warning(f"User with ID {user.id} not found when trying to update address")
            raise HTTPException(status_code=404, detail="User not found")
        
        formated_cep = "".join(filter(str.isdigit, data.cep))
        new_cep_data = is_valid_cep(formated_cep)

        if new_cep_data is False:
            logger.warning(f"Invalid CEP {data.cep} provided when trying to update address for user with ID {user.id}") 
            raise HTTPException(status_code=400, detail="Invalid CEP")
        
        address = f"{new_cep_data['logradouro']}, {new_cep_data['bairro']}, {new_cep_data['localidade']}"
        logger.info(f"Updating address for user with ID {user.id}")
        user.cep = formated_cep
        user.address = address
        user.complement = data.complement
        session.commit()
        logger.info(f"Address updated successfully for user with ID {user.id}")
        return user
    

