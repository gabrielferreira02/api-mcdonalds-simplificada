from pydantic import BaseModel
from app.schemas.category_schemas import CategoryResponseSchema

class ProductResponseSchema(BaseModel):
    name: str
    slug: str
    price: float
    description: str
    image_url: str
    is_active: bool
    category: CategoryResponseSchema

    class Config:
        from_attributes = True

class UpdateProductDataSchema(BaseModel):
    name: str
    price: float
    category_slug: str
    description: str

    class Config:
        from_attributes = True

class CartItem(BaseModel):
    slug: str
    quantity: int

class CartRequestSchema(BaseModel):
    items: list[CartItem]

class CartItemResponse(BaseModel):
    product: ProductResponseSchema
    quantity: int
    subtotal: float
    class Config:
        from_attributes = True

class CartResponseSchema(BaseModel):
    cart: list[CartItemResponse]
    invalid_slugs: list[str]
    total: float