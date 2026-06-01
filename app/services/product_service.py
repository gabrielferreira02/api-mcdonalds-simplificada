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

supabase_client = create_client(supabase_key=SUPABASE_KEY, supabase_url=SUPABASE_URL)

class ProductService:
    def create_product(name: str,
                        price: float,
                        description: str,
                        category_slug: str,
                        image: UploadFile,
                        session: Session,
                        user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not name:
            raise HTTPException(status_code=400, detail="Invalid product name")
        if price <= 0:
            raise HTTPException(status_code=400, detail="Invalid product price, Must be greater than 0")
        if not description:
            raise HTTPException(status_code=400, detail="Invalid product description")
        if not category_slug:
            raise HTTPException(status_code=400, detail="Invalid category")
        if not image:
            raise HTTPException(status_code=400, detail="Product needs to have an image")
        
        slug = generate_slug(name)

        exist_product = session.query(Product).filter(Product.slug == slug).first()

        if exist_product:
            raise HTTPException(status_code=400, detail="Product name already registered")
        
        category = session.query(Category).filter(Category.slug == category_slug).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if image.content_type not in ALLOWED_TYPES:
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
            raise HTTPException(status_code=500, detail="Error uploading image")

        product.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        product.image_path = filename
        session.commit()
        return product
    
    def get_products(session: Session):
        products = session.query(Product).filter(Product.is_active == True).all()
        return products
    
    def deactivate_product(slug: str, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        product = session.query(Product).filter(Product.slug == slug).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.is_active = False
        session.commit()
    
    def activate_product(slug: str, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        product = session.query(Product).filter(Product.slug == slug).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.is_active = True
        session.commit()

    def update_product_data(body: UpdateProductDataSchema, slug: str, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not body.description:
            raise HTTPException(status_code=400, detail="Invalid description")
        if not body.name:
            raise HTTPException(status_code=400, detail="Invalid name")
        if body.price <= 0:
            raise HTTPException(status_code=400, detail="Invalid price. Must be greater than 0")
        if not body.category_slug:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        product = session.query(Product).filter(Product.slug == slug).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        category = session.query(Category).filter(Category.slug == body.category_slug).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        new_slug = generate_slug(body.name)
        if new_slug != product.slug:
            exist_slug = session.query(Product).filter(Product.slug == slug).first()
            if exist_slug:
                raise HTTPException(status_code=400, detail="Product name already registered")
            product.name = body.name
            product.slug = new_slug
        
        product.category_id = category.id
        product.category = category
        product.price = body.price
        product.description = body.description
        session.commit()
        return product

    def update_product_image(slug: str, image: UploadFile, session: Session, user: User):
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not image:
            raise HTTPException(status_code=400, detail="Image required")
        
        product = session.query(Product).filter(Product.slug == slug).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file format. Images only")
        
        content = image.file.read()

        filename = f"products/{uuid.uuid4()}.png"
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=content,
            file_options={"content-type": image.content_type}
        )

        if hasattr(response, "error"):
            raise HTTPException(status_code=500, detail="Error uploading image")

        if product.image_path:
            try:
                supabase_client.storage.from_(SUPABASE_BUCKET).remove([product.image_path])
            except Exception:
                raise HTTPException(status_code=500, detail="Internal error deleting old product image")
        product.image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        product.image_path = filename
        session.commit()
        return product

    def get_products_by_category(category_slug: str, session: Session):
        products = (
            session.query(Product)
            .join(Product.category)
            .filter((Category.slug == category_slug) & (Product.is_active == True))
            .all())
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

        return CartResponseSchema(
            cart = response_items,
            invalid_slugs = invalid_slugs,
            total = total
        )

    def get_product_by_slug(slug: str, session: Session):
        product = session.query(Product).filter(Product.slug == slug).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product