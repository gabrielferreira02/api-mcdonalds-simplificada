from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.api.deps import get_session, verify_token
from app.services.category_service import CategoryService
from app.schemas.category_schemas import CategoryResponseSchema, CategoryRequestSchema
from app.models.user import User

category_router = APIRouter(prefix="/categories", tags=["Categories"])

@category_router.get("", response_model=list[CategoryResponseSchema])
async def get_categories(session: Session = Depends(get_session)):
    return CategoryService.get_categories(session)

@category_router.get("/{slug}", response_model=CategoryResponseSchema)
async def get_category_by_slug(slug: str, session: Session = Depends(get_session)):
    return CategoryService.get_category_by_slug(slug, session)

@category_router.delete("/{slug}", status_code=204)
async def delete_category(slug: str, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    return CategoryService.delete_category(slug, session, user)

@category_router.post("", status_code=201, response_model=CategoryResponseSchema)
async def create_category(name: str = Form(...),
                          image: UploadFile = File(...),
                          session: Session = Depends(get_session),
                          user: User = Depends(verify_token)):
    return CategoryService.create_category(name, image, session, user)

@category_router.put("/{slug}", response_model=CategoryResponseSchema)
async def update_category_name(slug: str,
                               body: CategoryRequestSchema,
                               session: Session = Depends(get_session),
                               user: User = Depends(verify_token)):
    return CategoryService.update_category_name(body, slug, session, user)

@category_router.patch("/{slug}", response_model=CategoryResponseSchema)
async def update_category_image(slug: str,
                               image: UploadFile = File(...),
                               session: Session = Depends(get_session),
                               user: User = Depends(verify_token)):
    return CategoryService.update_category_image(slug, image, session, user)