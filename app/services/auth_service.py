from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from app.core.vars import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_TIME
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import LoginRequestSchema, LoginResponseSchema, RegisterRequestSchema
from fastapi import HTTPException
from app.helpers.validate_cep import is_valid_cep
from app.helpers.validate_cpf import is_valid_cpf
from app.models.user import User
from app.core.security import pwd_context
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def user_register(body: RegisterRequestSchema, session: Session):
        if not body.first_name:
            logger.warning("Empty first name provided")
            raise HTTPException(status_code=400, detail="Empty first name")
        if not body.last_name:
            logger.warning("Empty last name provided")
            raise HTTPException(status_code=400, detail="Empty last name")
        if not body.email:
            logger.warning("Invalid email provided")
            raise HTTPException(status_code=400, detail="Invalid email")
        if len(body.password) < 8:
            logger.warning("Invalid password provided")
            raise HTTPException(status_code=400, detail="Invalid password")
        if not body.cep:
            logger.warning("Empty cep provided")
            raise HTTPException(status_code=400, detail="Empty cep")
        if not body.complement:
            logger.warning("Empty complement provided")
            raise HTTPException(status_code=400, detail="Empty complement")
        if not body.cpf:
            logger.warning("Empty cpf provided")
            raise HTTPException(status_code=400, detail="Empty first cpf")
        
        formated_cep = "".join(filter(str.isdigit, body.cep))
        formated_cpf = "".join(filter(str.isdigit, body.cpf))
        data = is_valid_cep(formated_cep)

        if data is False:
            logger.warning(f"Invalid CEP provided: {body.cep}")
            raise HTTPException(status_code=400, detail="Invalid CEP")
        
        address = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}"
        
        if not is_valid_cpf(formated_cpf):
            logger.warning(f"Invalid CPF provided: {body.cpf}")
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

        logger.info(f"Registering user with email: {body.email}")
        session.add(user)
        session.commit()
        logger.info(f"User registered successfully with ID {user.id}")  
        return user

    @staticmethod
    def generate_token(user_id, duration=timedelta(minutes=int(JWT_EXPIRATION_TIME))):
        expiration_date = datetime.now(timezone.utc) + duration
        dic_info = {"sub": str(user_id), "exp": expiration_date}
        token = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
        logger.info(f"Token generated for user ID: {user_id}")
        return token
    
    def login(body: LoginRequestSchema, session: Session):
        if not body.email:
            logger.warning("Invalid email provided")
            raise HTTPException(status_code=400, detail="Invalid email")
        if not body.password:
            logger.warning("Invalid password provided")
            raise HTTPException(status_code=400, detail="Invalid password")
        
        user = session.query(User).filter(User.email == body.email).first()
        if not user:
            logger.warning("User not found")
            raise HTTPException(status_code=400, detail="Invalid email or password")
        
        if not pwd_context.verify(body.password, user.password):
            logger.warning("Invalid email or password")
            raise HTTPException(status_code=400, detail="Invalid email or password")
        
        token = AuthService.generate_token(user.id)
        refresh_token = AuthService.generate_token(user.id, duration=timedelta(days=7))
        logger.info(f"User logged in successfully with email: {body.email}")
        return LoginResponseSchema(access_token=token, refresh_token=refresh_token)
    
    def refresh_token(user: User):
        token = AuthService.generate_token(user.id)
        refresh_token = AuthService.generate_token(user.id, duration=timedelta(days=7))
        logger.info(f"Refreshing token for user ID: {user.id}")
        return LoginResponseSchema(access_token=token, refresh_token=refresh_token)

    def login_docs(body: OAuth2PasswordRequestForm, session: Session):
        user = session.query(User).filter(User.email == body.username).first()

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        if not pwd_context.verify(body.password, user.password):
            raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
        token = AuthService.generate_token(user.id)
        refresh_token = AuthService.generate_token(user.id, timedelta(days=7))

        return LoginResponseSchema(access_token=token, refresh_token=refresh_token)

        
