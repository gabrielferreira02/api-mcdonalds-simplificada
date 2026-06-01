from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.deps import get_session, verify_token
from app.services.product_service import ProductService
from app.schemas.product_schemas import ProductResponseSchema, UpdateProductDataSchema, CartRequestSchema
from app.models.user import User

product_router = APIRouter(prefix="/products", tags=["Products"])

@product_router.post("", response_model=ProductResponseSchema, status_code=201)
async def create_product(name: str = Form(...),
                         price: float = Form(...),
                         description: str = Form(...),
                         category_slug: str = Form(...),
                         image: UploadFile = File(...),
                         session: Session = Depends(get_session),
                         user: User = Depends(verify_token)):
    return ProductService.create_product(name, price, description, category_slug, image, session, user)

@product_router.get("", response_model=list[ProductResponseSchema])
async def get_products(session: Session = Depends(get_session)):
    return ProductService.get_products(session)

@product_router.get("/category/{category_slug}", response_model=list[ProductResponseSchema])
async def get_products_by_category(category_slug: str, session: Session = Depends(get_session)):
    return ProductService.get_products_by_category(category_slug, session)

@product_router.post("/cart")
async def get_cart(data: CartRequestSchema,
                   session: Session = Depends(get_session),
                   user: User = Depends(verify_token)):
    return ProductService.get_cart_products(data, session, user)

@product_router.get("/{slug}", response_model=ProductResponseSchema)
async def get_product_by_slug(slug: str, session: Session = Depends(get_session)):
    return ProductService.get_product_by_slug(slug, session)

@product_router.put("/{slug}", response_model=ProductResponseSchema)
async def update_product_data(body: UpdateProductDataSchema,
                              slug: str,
                              session: Session = Depends(get_session),
                              user: User = Depends(verify_token)):
    return ProductService.update_product_data(body, slug, session, user)

@product_router.put("/{slug}/image", response_model=ProductResponseSchema)
async def update_product_image(slug: str,
                               image: UploadFile = File(...),
                               session: Session = Depends(get_session),
                               user: User = Depends(verify_token)):
    return ProductService.update_product_image(slug, image, session, user)

@product_router.patch("/{slug}/activate", status_code=204)
async def activate_product(slug: str,
                           session: Session = Depends(get_session),
                           user: User = Depends(verify_token)):
    return ProductService.activate_product(slug, session, user)

@product_router.patch("/{slug}/deactivate", status_code=204)
async def deactivate_product(slug: str,
                             session: Session = Depends(get_session),
                             user: User = Depends(verify_token)):
    return ProductService.deactivate_product(slug, session, user)
