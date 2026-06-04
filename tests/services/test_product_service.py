import pytest
from app.services.product_service import ProductService
from app.models.product import Product
from app.models.category import Category
from unittest.mock import Mock
from app.schemas.product_schemas import UpdateProductDataSchema, CartRequestSchema, CartItem

class UploadResponse:
    pass

def test_get_product_by_slug_success(db_session):
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    response: Product = ProductService.get_product_by_slug("test-product", db_session) 
    assert response is not None
    assert response.name == "Test Product"
    assert response.slug == "test-product"
    assert response.price == 10.0

def test_get_product_by_slug_not_found(db_session):
    with pytest.raises(Exception) as exc_info:
        ProductService.get_product_by_slug("non-existent-product", db_session)
    assert "Product not found" in str(exc_info.value)

def test_create_product_success(db_session, create_user,monkeypatch):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    user.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.return_value = UploadResponse()
    monkeypatch.setattr("app.services.product_service.supabase_client", supabase_mock)

    response = ProductService.create_product(
        name="New Product",
        price=20.0,
        description="A new test product",
        category_slug=category.slug,
        image=image,
        session=db_session,
        user=user
    )
    assert response is not None
    assert response.name == "New Product"
    assert response.slug == "new-product"
    assert response.price == 20.0

def test_create_product_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    user.is_admin = False
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"

    with pytest.raises(Exception) as exc_info:
        ProductService.create_product(
            name="New Product",
            price=20.0,
            description="A new test product",
            category_slug=category.slug,
            image=image,
            session=db_session,
            user=user
        )
    assert "Unauthorized" in str(exc_info.value)

def test_create_product_invalid_image(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    user.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "application/pdf"

    with pytest.raises(Exception) as exc_info:
        ProductService.create_product(
            name="New Product",
            price=20.0,
            description="A new test product",
            category_slug=category.slug,
            image=image,
            session=db_session,
            user=user
        )
    assert "Invalid file format. Images only" in str(exc_info.value)

def test_create_product_category_not_found(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"

    with pytest.raises(Exception) as exc_info:
        ProductService.create_product(
            name="New Product",
            price=20.0,
            description="A new test product",
            category_slug="non-existent-category",
            image=image,
            session=db_session,
            user=user
        )
    assert "Category not found" in str(exc_info.value)

def test_create_product_image_upload_failure(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    user.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.side_effect = Exception("Upload failed")
    monkeypatch.setattr("app.services.product_service.supabase_client", supabase_mock)

    with pytest.raises(Exception) as exc_info:
        ProductService.create_product(
            name="New Product",
            price=20.0,
            description="A new test product",
            category_slug=category.slug,
            image=image,
            session=db_session,
            user=user
        )
    assert "Upload failed" in str(exc_info.value)

def test_create_product_duplicate_slug(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Existing Product",
        slug="existing-product",
        price=15.0,
        description="An existing product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)

def test_deactivate_product_success(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    response = ProductService.deactivate_product("test-product", db_session, user)
    assert response is None

def test_deactivate_product_not_found(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        ProductService.deactivate_product("non-existent-product", db_session, user)
    assert "Product not found" in str(exc_info.value)

def test_deactivate_product_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    user.is_admin = False
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        ProductService.deactivate_product("test-product", db_session, user)
    assert "Unauthorized" in str(exc_info.value)

def test_activate_product_success(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=False
    )
    db_session.add(product)
    db_session.commit()
    response = ProductService.activate_product("test-product", db_session, user)
    assert response is None

def test_activate_product_not_found(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        ProductService.activate_product("non-existent-product", db_session, user)
    assert "Product not found" in str(exc_info.value)

def test_activate_product_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=False
    )
    db_session.add(product)
    user.is_admin = False
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        ProductService.activate_product("test-product", db_session, user)
    assert "Unauthorized" in str(exc_info.value)

def test_update_product_data_success(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=15.0,
        description="An updated test product",
        category_slug=category.slug
    )
    response = ProductService.update_product_data(
        body,
        "test-product",
        session=db_session,
        user=user
    )

    assert response is not None
    assert response.name == "Updated Product"
    assert response.price == 15.0

def test_update_product_data_not_found(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=15.0,
        description="An updated test product",
        category_slug="test-category"
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "non-existent-product",
            session=db_session,
            user=user
        )
    assert "Product not found" in str(exc_info.value)

def test_update_product_data_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    user.is_admin = False
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=15.0,
        description="An updated test product",
        category_slug=category.slug
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product",
            session=db_session,
            user=user
        )
    assert "Unauthorized" in str(exc_info.value)

def test_update_product_data_category_not_found(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=15.0,
        description="An updated test product",
        category_slug="non-existent-category"
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product",
            session=db_session,
            user=user
        )
    assert "Category not found" in str(exc_info.value)

def test_update_product_data_duplicate_slug(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product1 = Product(
        name="Test Product 1",
        slug="test-product-1",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    product2 = Product(
        name="Updated Product",
        slug="updated-product",
        price=15.0,
        description="Another test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product1)
    db_session.add(product2)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=20.0,
        description="An updated test product",
        category_slug=category.slug
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product-1",
            session=db_session,
            user=user
        )
    assert "Product name already registered" in str(exc_info.value)

def test_update_product_data_invalid_name(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="",
        price=15.0,
        description="An updated test product",
        category_slug=category.slug
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product",
            session=db_session,
            user=user
        )
    assert "Invalid name" in str(exc_info.value)

def test_update_product_data_invalid_price(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=-5.0,
        description="An updated test product",
        category_slug=category.slug
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product",
            session=db_session,
            user=user
        )
    assert "Invalid price. Must be greater than 0" in str(exc_info.value)

def test_update_product_data_invalid_description(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=15.0,
        description="",
        category_slug=category.slug
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product",
            session=db_session,
            user=user
        )
    assert "Invalid description" in str(exc_info.value)

def test_update_product_data_invalid_category(db_session, create_user):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    body = UpdateProductDataSchema(
        name="Updated Product",
        price=15.0,
        description="An updated test product",
        category_slug="non-existent-category"
    )
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_data(
            body,
            "test-product",
            session=db_session,
            user=user
        )
    assert "Category not found" in str(exc_info.value)

def test_update_product_image_success(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.return_value = UploadResponse()
    monkeypatch.setattr("app.services.product_service.supabase_client", supabase_mock)
    
    response = ProductService.update_product_image(
        "test-product",
        image=image,
        session=db_session,
        user=user
    )
    assert response is not None

def test_update_product_image_not_found(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    user.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_image(
            "non-existent-product",
            image=image,
            session=db_session,
            user=user
        )
    assert "Product not found" in str(exc_info.value)

def test_update_product_image_unauthorized(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    user.is_admin = False
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_image(
            "test-product",
            image=image,
            session=db_session,
            user=user
        )
    assert "Unauthorized" in str(exc_info.value)

def test_update_product_image_invalid_file_format(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    image = Mock()
    image.content_type = "application/pdf"
    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_image(
            "test-product",
            image=image,
            session=db_session,
            user=user
        )
    assert "Invalid file format. Images only" in str(exc_info.value)

def test_update_product_image_upload_failure(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    user.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    product = Product(
        name="Test Product",
        slug="test-product",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.side_effect = Exception("Upload failed")
    monkeypatch.setattr("app.services.product_service.supabase_client", supabase_mock)

    with pytest.raises(Exception) as exc_info:
        ProductService.update_product_image(
            "test-product",
            image=image,
            session=db_session,
            user=user
        )
    assert "Upload failed" in str(exc_info.value)

def test_get_products_by_category_success(db_session):
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    product1 = Product(
        name="Test Product 1",
        slug="test-product-1",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True
    )
    product2 = Product(
        name="Test Product 2",
        slug="test-product-2",
        price=15.0,
        description="Another test product",
        category_id=category.id,
        is_active=True
    )
    db_session.add(product1)
    db_session.add(product2)
    db_session.commit()
    response = ProductService.get_products_by_category("test-category", db_session)
    assert response is not None
    assert len(response) == 2
    assert response[0].name == "Test Product 1"
    assert response[1].name == "Test Product 2"

def test_get_cart_products(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    product1 = Product(
        name="Test Product 1",
        slug="test-product-1",
        price=10.0,
        description="A test product",
        category_id=category.id,
        is_active=True,
        image_url="http://example.com/image.jpg"
    )
    product2 = Product(
        name="Test Product 2",
        slug="test-product-2",
        price=15.0,
        description="Another test product",
        category_id=category.id,
        is_active=True,
        image_url="http://example.com/image.jpg"
    )
    db_session.add(product1)
    db_session.add(product2)
    db_session.commit()
    items = CartRequestSchema(items=[CartItem(slug="test-product-1", quantity=2), CartItem(slug="test-product-2", quantity=1)])
    response = ProductService.get_cart_products(items, db_session, user)
    assert response is not None
    assert len(response.cart) == 2
    assert response.cart[0].product.name == "Test Product 1"
    assert response.cart[1].product.name == "Test Product 2"