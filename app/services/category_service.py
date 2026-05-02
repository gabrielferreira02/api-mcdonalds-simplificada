from sqlalchemy.orm import Session
from app.models.category import Category
from fastapi import HTTPException, UploadFile
from app.schemas.category_schemas import CategoryRequestSchema
from supabase import create_client
from app.core.vars import SUPABASE_BUCKET, SUPABASE_KEY, SUPABASE_URL, ALLOWED_TYPES
from app.helpers.generate_slug import generate_slug
import uuid

supabase_client = create_client(supabase_key=SUPABASE_KEY, supabase_url=SUPABASE_URL)


class CategoryService:
    def get_categories(session: Session):
        categories = session.query(Category).all()
        return categories
    
    def get_category_by_slug(slug: str, session: Session):
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    
    @staticmethod
    def delete_category(slug: str, session: Session):
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category.image_path:
            try:
                supabase_client.storage.from_(SUPABASE_BUCKET).remove([category.image_path])
            except Exception:
                raise HTTPException(status_code=500, detail="Internal error deleting category")
        session.delete(category)
        session.commit()

    def create_category(name: str, image: UploadFile, session: Session):
        if not name:
            raise HTTPException(status_code=400, detail="Invalid name")
        
        slug = generate_slug(name)

        exist_category = session.query(Category).filter(Category.slug == slug).first()
        if exist_category:
            raise HTTPException(status_code=400, detail="Already exists a category with this name")

        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file format. Images only")
        
        content = image.file.read()

        
        category = Category(name=name, slug=slug)
        session.add(category)

        filename = f"categories/{uuid.uuid4()}.png"
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=content,
            file_options={"content-type": image.content_type}
        )

        if hasattr(response, "error"):
            raise HTTPException(status_code=500, detail="Error uploading image")

        category.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        category.image_path = filename
        session.commit()
        return category

    def update_category_name(body: CategoryRequestSchema, slug: str, session: Session):
        if not body.name:
            raise HTTPException(status_code=400, detail="Invalid name")
        
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        new_slug = generate_slug(body.name)

        exist_category = session.query(Category).filter(Category.slug == new_slug).first()
        if exist_category:
            raise HTTPException(status_code=400, detail="Category name already registered")
        
        if new_slug != slug:
            category.name = body.name
            category.slug = new_slug
            session.commit()
        
        return category

    def update_category_image(slug: str, image: UploadFile, session: Session):
        if not image:
            raise HTTPException(status_code=400, detail="Invalid image. Field cannot be empty")
        
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file format. Images only")
        
        content = image.file.read()

        filename = f"categories/{uuid.uuid4()}.png"
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=content,
            file_options={"content-type": image.content_type}
        )

        if hasattr(response, "error"):
            raise HTTPException(status_code=500, detail="Error uploading image")
        
        if category.image_path:
            try:
                supabase_client.storage.from_(SUPABASE_BUCKET).remove([category.image_path])
            except Exception:
                raise HTTPException(status_code=500, detail="Internal error deleting category")
        category.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        category.image_path = filename
        session.commit()
        return category