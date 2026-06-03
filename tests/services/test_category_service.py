import pytest
from app.services.category_service import CategoryService
from app.models.category import Category
from unittest.mock import Mock
from app.schemas.category_schemas import CategoryRequestSchema

class UploadResponse:
    pass

def test_get_categories(db_session):
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    categories = CategoryService.get_categories(db_session)
    assert len(categories) == 1
    assert categories[0].name == "Test Category"

def test_get_category_by_slug(db_session):
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    result = CategoryService.get_category_by_slug("test-category", db_session)
    assert result.name == "Test Category"

def test_get_category_by_slug_not_found(db_session):
    with pytest.raises(Exception) as excinfo:
        CategoryService.get_category_by_slug("non-existent-slug", db_session)
    assert "Category not found" in str(excinfo.value)

def test_delete_category(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    CategoryService.delete_category("test-category", db_session, admin)
    result = db_session.query(Category).filter(Category.slug == "test-category").first()
    assert result is None

def test_delete_category_not_found(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    with pytest.raises(Exception) as excinfo:
        CategoryService.delete_category("non-existent-slug", db_session, admin)
    assert "Category not found" in str(excinfo.value)

def test_delete_category_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    with pytest.raises(Exception) as excinfo:
        CategoryService.delete_category("test-category", db_session, user)
    assert "You don't have permission to perform this action" in str(excinfo.value)

def test_create_category(db_session, create_user, monkeypatch):
    admin = create_user(db_session)
    admin.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    image.file.read.return_value = b"test"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.return_value = UploadResponse()
    monkeypatch.setattr("app.services.category_service.supabase_client", supabase_mock)
    category = CategoryService.create_category("New Category", image, db_session, admin)
    assert category is not None
    assert category.name == "New Category"

def test_create_category_invalid_name(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    image.file.read.return_value = b"test"
    with pytest.raises(Exception) as excinfo:
        CategoryService.create_category("", image, db_session, admin)
    assert "Invalid name" in str(excinfo.value)

def test_create_category_invalid_file_format(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "application/pdf"
    with pytest.raises(Exception) as excinfo:
        CategoryService.create_category("New Category", image, db_session, admin)
    assert "Invalid file format" in str(excinfo.value) 

def test_create_category_unauthorized(db_session, create_user):
    user = create_user(db_session)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    with pytest.raises(Exception) as excinfo:
        CategoryService.create_category("New Category", image, db_session, user)
    assert "You don't have permission to perform this action" in str(excinfo.value)

def test_create_category_already_exists(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Existing Category", slug="existing-category")
    db_session.add(category)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    with pytest.raises(Exception) as excinfo:
        CategoryService.create_category("Existing Category", image, db_session, admin)
    assert "Already exists a category with this name" in str(excinfo.value)

def test_update_category_name(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Old Name", slug="old-name")
    db_session.add(category)
    db_session.commit()
    category_request = CategoryRequestSchema(name="New Name")
    updated_category = CategoryService.update_category_name(category_request, "old-name", db_session, admin)
    assert updated_category.name == "New Name"

def test_update_category_name_not_found(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    db_session.commit()
    category_request = CategoryRequestSchema(name="New Name")
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_name(category_request, "non-existent-slug", db_session, admin)
    assert "Category not found" in str(excinfo.value)

def test_update_category_name_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Old Name", slug="old-name")
    db_session.add(category)
    db_session.commit()
    category_request = CategoryRequestSchema(name="New Name")
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_name(category_request, "old-name", db_session, user)
    assert "You don't have permission to perform this action" in str(excinfo.value)

def test_update_category_name_already_exists(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    category1 = Category(name="Category One", slug="category-one")
    category2 = Category(name="Category Two", slug="category-two")
    db_session.add(category1)
    db_session.add(category2)
    db_session.commit()
    category_request = CategoryRequestSchema(name="Category Two")
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_name(category_request, "category-one", db_session, admin)
    assert "Category name already registered" in str(excinfo.value)

def test_update_category_name_invalid_name(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Old Name", slug="old-name")
    db_session.add(category)
    db_session.commit()
    category_request = CategoryRequestSchema(name="")
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_name(category_request, "old-name", db_session, admin)
    assert "Invalid name" in str(excinfo.value)

def test_update_category_image_success(db_session, create_user, monkeypatch):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    image.file.read.return_value = b"test"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.return_value = UploadResponse()
    monkeypatch.setattr("app.services.category_service.supabase_client", supabase_mock)
    updated_category = CategoryService.update_category_image("test-category", image, db_session, admin)
    assert updated_category.image_url is not None

def test_update_category_image_invalid_file_format(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    image = Mock()
    image.content_type = "application/pdf"
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_image("test-category", image, db_session, admin)
    assert "Invalid file format" in str(excinfo.value)

def test_update_category_image_unauthorized(db_session, create_user):
    user = create_user(db_session)
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_image("test-category", image, db_session, user)
    assert "You don't have permission to perform this action" in str(excinfo.value)

def test_update_category_image_category_not_found(db_session, create_user):
    admin = create_user(db_session)
    admin.is_admin = True
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_image("non-existent-slug", image, db_session, admin)
    assert "Category not found" in str(excinfo.value)

def test_update_category_image_upload_error(db_session, create_user, monkeypatch):
    admin = create_user(db_session)
    admin.is_admin = True
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()
    image = Mock()
    image.content_type = "image/jpeg"
    image.file.read.return_value = b"test"
    supabase_mock = Mock()
    supabase_mock.storage.from_.return_value.upload.return_value.error = "Upload error"
    monkeypatch.setattr("app.services.category_service.supabase_client", supabase_mock)
    with pytest.raises(Exception) as excinfo:
        CategoryService.update_category_image("test-category", image, db_session, admin)
    assert "Error uploading image" in str(excinfo.value)