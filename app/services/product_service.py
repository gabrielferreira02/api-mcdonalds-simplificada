from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from supabase import create_client
from app.core.vars import ALLOWED_TYPES, SUPABASE_KEY, SUPABASE_BUCKET, SUPABASE_URL
from app.helpers.generate_slug import generate_slug
from app.models.product import Product
from app.models.category import Category
from app.schemas.product_schemas import UpdateProductDataSchema, CartRequestSchema, CartItemResponse, CartResponseSchema
import uuid
from app.models.user import User
import logging

supabase_client = create_client(supabase_key=SUPABASE_KEY, supabase_url=SUPABASE_URL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class ProductService:
    def create_product(name: str,
                        price: float,
                        description: str,
                        category_slug: str,
                        image: UploadFile,
                        session: Session,
                        user: User):
        if not user.is_admin:
            logger.warning("Unauthorized attempt to create product")
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not name:
            logger.warning("Invalid product name provided")
            raise HTTPException(status_code=400, detail="Invalid product name")
        if price <= 0:
            logger.warning("Invalid product price provided")
            raise HTTPException(status_code=400, detail="Invalid product price, Must be greater than 0")
        if not description:
            logger.warning("Invalid product description provided")
            raise HTTPException(status_code=400, detail="Invalid product description")
        if not category_slug:
            logger.warning("Invalid category provided")
            raise HTTPException(status_code=400, detail="Invalid category")
        if not image:
            logger.warning("Product needs to have an image")
            raise HTTPException(status_code=400, detail="Product needs to have an image")
        
        slug = generate_slug(name)

        exist_product = session.query(Product).filter(Product.slug == slug).first()

        if exist_product:
            logger.warning("Product name already registered")
            raise HTTPException(status_code=400, detail="Product name already registered")
        
        category = session.query(Category).filter(Category.slug == category_slug).first()

        if not category:
            logger.warning("Category not found")
            raise HTTPException(status_code=404, detail="Category not found")
        
        if image.content_type not in ALLOWED_TYPES:
            logger.warning("Invalid file format. Images only")
            raise HTTPException(status_code=400, detail="Invalid file format. Images only")
        
        content = image.file.read()
        
        product = Product(
            name = name,
            description = description,
            slug = slug,
            price = price,
            category_id = category.id,
            category = category
        )

        session.add(product)

        filename = f"products/{uuid.uuid4()}.png"
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=content,
            file_options={"content-type": image.content_type}
        )

        if hasattr(response, "error"):
            logger.error("Error uploading image")
            raise HTTPException(status_code=500, detail="Error uploading image")

        product.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        product.image_path = filename
        session.commit()
        logger.info(f"Product created: {product.slug}")
        return product
    
    def get_products(session: Session):
        products = session.query(Product).filter(Product.is_active == True).all()
        logger.info(f"Fetched {len(products)} active products")
        return products
    
    def deactivate_product(slug: str, session: Session, user: User):
        if not user.is_admin:
            logger.warning("Unauthorized attempt to deactivate product")
            raise HTTPException(status_code=403, detail="Unauthorized")
        product = session.query(Product).filter(Product.slug == slug).first()

        if not product:
            logger.warning("Product not found")
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.is_active = False
        logger.info(f"Product deactivated: {product.slug}")
        session.commit()
    
    def activate_product(slug: str, session: Session, user: User):
        if not user.is_admin:
            logger.warning("Unauthorized attempt to activate product")
            raise HTTPException(status_code=403, detail="Unauthorized")
        product = session.query(Product).filter(Product.slug == slug).first()

        if not product:
            logger.warning("Product not found")
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.is_active = True
        logger.info(f"Product activated: {product.slug}")
        session.commit()

    def update_product_data(body: UpdateProductDataSchema, slug: str, session: Session, user: User):
        if not user.is_admin:
            logger.warning("Unauthorized attempt to update product data")
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not body.description:
            logger.warning("Invalid description")
            raise HTTPException(status_code=400, detail="Invalid description")
        if not body.name:
            logger.warning("Invalid name")
            raise HTTPException(status_code=400, detail="Invalid name")
        if body.price <= 0:
            logger.warning("Invalid price")
            raise HTTPException(status_code=400, detail="Invalid price. Must be greater than 0")
        if not body.category_slug:
            logger.warning("Invalid category")
            raise HTTPException(status_code=400, detail="Invalid category")
        
        product = session.query(Product).filter(Product.slug == slug).first()
        if not product:
            logger.warning("Product not found")
            raise HTTPException(status_code=404, detail="Product not found")
        
        category = session.query(Category).filter(Category.slug == body.category_slug).first()
        if not category:
            logger.warning("Category not found")
            raise HTTPException(status_code=404, detail="Category not found")
        
        new_slug = generate_slug(body.name)
        if new_slug != product.slug:
            exist_slug = session.query(Product).filter(Product.slug == new_slug).first()
            if exist_slug:
                logger.warning("Product name already registered")
                raise HTTPException(status_code=400, detail="Product name already registered")
            product.name = body.name
            product.slug = new_slug
        
        product.category_id = category.id
        product.category = category
        product.price = body.price
        product.description = body.description
        session.commit()
        logger.info(f"Product updated: {product.slug}")
        return product

    def update_product_image(slug: str, image: UploadFile, session: Session, user: User):
        if not user.is_admin:
            logger.warning("Unauthorized attempt to update product image")
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not image:
            logger.warning("Image required")
            raise HTTPException(status_code=400, detail="Image required")
        
        product = session.query(Product).filter(Product.slug == slug).first()
        if not product:
            logger.warning("Product not found")
            raise HTTPException(status_code=404, detail="Product not found")
        
        if image.content_type not in ALLOWED_TYPES:
            logger.warning("Invalid file format. Images only")
            raise HTTPException(status_code=400, detail="Invalid file format. Images only")
        
        content = image.file.read()

        filename = f"products/{uuid.uuid4()}.png"
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=content,
            file_options={"content-type": image.content_type}
        )

        if hasattr(response, "error"):
            logger.error("Error uploading image")
            raise HTTPException(status_code=500, detail="Error uploading image")

        if product.image_path:
            try:
                supabase_client.storage.from_(SUPABASE_BUCKET).remove([product.image_path])
            except Exception:
                logger.error("Internal error deleting old product image")
                raise HTTPException(status_code=500, detail="Internal error deleting old product image")
        product.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        product.image_path = filename
        session.commit()
        logger.info(f"Product image updated: {product.slug}")
        return product

    def get_products_by_category(category_slug: str, session: Session):
        products = (
            session.query(Product)
            .join(Product.category)
            .filter((Category.slug == category_slug) & (Product.is_active == True))
            .all())
        logger.info(f"Products found in category '{category_slug}': {len(products)}")
        return products

    def get_cart_products(data: CartRequestSchema, session: Session, user: User):
        slugs = [p.slug for p in data.items]

        products = (session.query(Product)
                    .filter(Product.slug.in_(slugs))
                    .all())
        
        product_map = {p.slug: p for p in products}
        response_items: list[CartItemResponse] = []
        invalid_slugs = []
        total = 0

        for item in data.items:
            product: Product = product_map.get(item.slug)
            if product and product.is_active:
                subtotal = product.price * item.quantity
                total += subtotal
                response_items.append(CartItemResponse(
                    product = product,
                    quantity = item.quantity,
                    subtotal =subtotal
                ))
            if product and not product.is_active:
                subtotal = product.price * item.quantity
                invalid_slugs.append(item.slug)
                response_items.append(CartItemResponse(
                    product = product,
                    quantity = item.quantity,
                    subtotal =subtotal
                ))

        logger.info(f"Cart items retrieved: {len(response_items)}")
        return CartResponseSchema(
            cart = response_items,
            invalid_slugs = invalid_slugs,
            total = total
        )

    def get_product_by_slug(slug: str, session: Session):
        product = session.query(Product).filter(Product.slug == slug).first()
        if not product:
            logger.warning("Product not found")
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info(f"Product retrieved: {product.slug}")
        return product