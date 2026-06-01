from fastapi import APIRouter, Depends
from app.api.deps import verify_token, get_session
from app.models.user import User
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schemas.user_schemas import UpdateUsernameSchema, UpdateEmailSchema, UpdatePasswordSchema, UpdateAddressSchema, UserResponseSchema

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.get("/me", response_model=UserResponseSchema)
async def get_current_user(user: User = Depends(verify_token)):
    return user
    
@user_router.put("/me/username", response_model=UserResponseSchema)
async def update_username(body: UpdateUsernameSchema, user: User = Depends(verify_token), session: Session = Depends(get_session)):
    return UserService.update_username(user, body, session)

@user_router.patch("/me/email", response_model=UserResponseSchema)
async def update_email(body: UpdateEmailSchema, user: User = Depends(verify_token), session: Session = Depends(get_session)):
    return UserService.update_email(user, body, session)

@user_router.patch("/me/password", response_model=UserResponseSchema)
async def update_password(body: UpdatePasswordSchema, user: User = Depends(verify_token), session: Session = Depends(get_session)):
    return UserService.update_password(user, body, session)

@user_router.put("/me/address", response_model=UserResponseSchema)
async def update_address(body: UpdateAddressSchema, user: User = Depends(verify_token), session: Session = Depends(get_session)):
    return UserService.update_address(user, body, session)