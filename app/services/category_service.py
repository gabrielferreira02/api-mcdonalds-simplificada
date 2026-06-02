from sqlalchemy.orm import Session
from app.models.category import Category
from fastapi import HTTPException, UploadFile
from app.schemas.category_schemas import CategoryRequestSchema
from supabase import create_client
from app.core.vars import SUPABASE_BUCKET, SUPABASE_KEY, SUPABASE_URL, ALLOWED_TYPES
from app.helpers.generate_slug import generate_slug
from app.models.user import User
import uuid
import logging

supabase_client = create_client(supabase_key=SUPABASE_KEY, supabase_url=SUPABASE_URL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class CategoryService:
    def get_categories(session: Session):
        categories = session.query(Category).all()
        logger.info("Retrieving all categories")
        return categories
    
    def get_category_by_slug(slug: str, session: Session):
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            logger.warning(f"Category not found with slug: {slug}")
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Retrieving category with slug: {slug}")
        return category
    
    @staticmethod
    def delete_category(slug: str, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="You don't have permission to perform this action")
        
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            logger.warning(f"Category not found with slug: {slug}")
            raise HTTPException(status_code=404, detail="Category not found")

        if category.image_path:
            try:
                supabase_client.storage.from_(SUPABASE_BUCKET).remove([category.image_path])
            except Exception:
                logger.error("Error occurred while deleting category image")
                raise HTTPException(status_code=500, detail="Internal error deleting category")
        session.delete(category)
        session.commit()

    def create_category(name: str, image: UploadFile, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="You don't have permission to perform this action")
        if not name:
            logger.warning("Invalid name provided")
            raise HTTPException(status_code=400, detail="Invalid name")
        
        slug = generate_slug(name)

        exist_category = session.query(Category).filter(Category.slug == slug).first()
        if exist_category:
            logger.warning(f"Category already exists with slug: {slug}")
            raise HTTPException(status_code=400, detail="Already exists a category with this name")

        if image.content_type not in ALLOWED_TYPES:
            logger.warning("Invalid file format provided")
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
            logger.error("Error occurred while uploading category image")
            raise HTTPException(status_code=500, detail="Error uploading image")

        category.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        category.image_path = filename
        session.commit()
        logger.info(f"Category created with name: {name} and slug: {slug}")
        return category

    def update_category_name(body: CategoryRequestSchema, slug: str, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="You don't have permission to perform this action")
        if not body.name:
            logger.warning("Invalid name provided")
            raise HTTPException(status_code=400, detail="Invalid name")
        
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            logger.warning(f"Category not found with slug: {slug}")
            raise HTTPException(status_code=404, detail="Category not found")
        
        new_slug = generate_slug(body.name)

        exist_category = session.query(Category).filter(Category.slug == new_slug).first()
        if exist_category:
            logger.warning(f"Category name already registered with slug: {new_slug}")
            raise HTTPException(status_code=400, detail="Category name already registered")
        
        if new_slug != slug:
            category.name = body.name
            category.slug = new_slug
            logger.info(f"Category updated with name: {body.name} and slug: {new_slug}")
            session.commit()
        
        return category

    def update_category_image(slug: str, image: UploadFile, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="You don't have permission to perform this action")
        if not image:
            logger.warning("Invalid image provided")
            raise HTTPException(status_code=400, detail="Invalid image. Field cannot be empty")
        
        category = session.query(Category).filter(Category.slug == slug).first()
        if not category:
            logger.warning(f"Category not found with slug: {slug}")
            raise HTTPException(status_code=404, detail="Category not found")

        if image.content_type not in ALLOWED_TYPES:
            logger.warning("Invalid file format provided")
            raise HTTPException(status_code=400, detail="Invalid file format. Images only")
        
        content = image.file.read()

        filename = f"categories/{uuid.uuid4()}.png"
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=content,
            file_options={"content-type": image.content_type}
        )

        if hasattr(response, "error"):
            logger.error("Error occurred while uploading category image")
            raise HTTPException(status_code=500, detail="Error uploading image")
        
        if category.image_path:
            try:
                supabase_client.storage.from_(SUPABASE_BUCKET).remove([category.image_path])
            except Exception:
                logger.error("Error occurred while deleting old category image")
                raise HTTPException(status_code=500, detail="Internal error deleting category")
        category.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        category.image_path = filename
        session.commit()
        logger.info(f"Category image updated for category: {category.name}")
        return category