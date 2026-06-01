from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_session, verify_token
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import LoginRequestSchema, LoginResponseSchema, RegisterRequestSchema, RegisterResponseSchema
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# login
@auth_router.post("/login", response_model=LoginResponseSchema)
async def login(body: LoginRequestSchema, session: Session = Depends(get_session)):
    return AuthService.login(body, session)
# register
@auth_router.post("/register", status_code=201, response_model=RegisterResponseSchema)
async def user_register(body: RegisterRequestSchema, session: Session = Depends(get_session)):
    return AuthService.user_register(body, session)
# refresh token
@auth_router.post("/refresh-token", response_model=LoginResponseSchema)
async def refresh_token(user: str = Depends(verify_token)):
    return AuthService.refresh_token(user)

@auth_router.post("/login-docs", response_model=LoginResponseSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    return AuthService.login_docs(body, session)