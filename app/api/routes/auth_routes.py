from fastapi import APIRouter, Depends
from app.api.deps import get_session
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import RegisterRequestSchema, RegisterResponseSchema
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# login
# register
@auth_router.post("/register", status_code=201, response_model=RegisterResponseSchema)
async def user_register(body: RegisterRequestSchema, session: Session = Depends(get_session)):
    return AuthService.user_register(body, session)
# refresh token
# forgot password