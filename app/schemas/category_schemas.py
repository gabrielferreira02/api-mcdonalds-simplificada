from pydantic import BaseModel

class CategoryResponseSchema(BaseModel):
    name: str
    slug: str
    imageUrl: str | None
    class Config:
        from_attributes = True

class CategoryRequestSchema(BaseModel):
    name: str
    class Config:
        from_attributes = True