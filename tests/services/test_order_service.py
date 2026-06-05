import pytest
from app.services.order_service import OrderService, client
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User
from unittest.mock import Mock
from app.schemas.order_schemas import CreateOrderSchema, OrderItems
import uuid

def test_get_order_by_id_success(db_session, create_user):
    user = create_user(db_session)
    order = Order(
        user_id=user.id,
        total=20,
        status=OrderStatus.pending,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    response = OrderService.get_order_by_id(order.id, db_session, user)
    assert response is not None
    assert response.order.id == order.id

def test_get_order_by_id_not_found(db_session, create_user):
    user = create_user(db_session)
    with pytest.raises(Exception) as exc_info:
        OrderService.get_order_by_id(uuid.uuid4(), db_session, user)
    assert "Order not found" in str(exc_info.value)

def test_get_order_by_id_unauthorized(db_session, create_user):
    user1 = create_user(db_session)
    user2 = create_user(db_session)
    order = Order(
        user_id=user1.id,
        total=20,
        status=OrderStatus.pending,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        OrderService.get_order_by_id(order.id, db_session, user2)
    assert "You are not authorized to view this order" in str(exc_info.value)

def test_get_order_by_id_admin_access(db_session, create_user):
    admin_user = create_user(db_session)
    admin_user.is_admin = True
    regular_user = create_user(db_session)
    order = Order(
        user_id=regular_user.id,
        total=20,
        status=OrderStatus.pending,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    response = OrderService.get_order_by_id(order.id, db_session, admin_user)
    assert response is not None
    assert response.order.id == order.id

def test_get_user_orders_success(db_session, create_user):
    user = create_user(db_session)
    for i in range(5):
        order = Order(
            user_id=user.id,
            total=20,
            status=OrderStatus.pending,
            address="123 Main St",
            complement="Apt 4B",
            payment_link="http://payment.link"
        )
        db_session.add(order)
    db_session.commit()
    response = OrderService.get_user_orders(user.id, 1, db_session, user)
    assert response is not None
    assert len(response.orders) == 5
    assert response.page == 1
    assert response.total_pages == 1

def test_get_user_orders_unauthorized(db_session, create_user):
    user1 = create_user(db_session)
    user2 = create_user(db_session)
    with pytest.raises(Exception) as exc_info:
        OrderService.get_user_orders(user1.id, 1, db_session, user2)
    assert "You are not authorized to view orders for this user" in str(exc_info.value)

def test_get_user_orders_invalid_page(db_session, create_user):
    user = create_user(db_session)
    with pytest.raises(Exception) as exc_info:
        OrderService.get_user_orders(user.id, 0, db_session, user)
    assert "Invalid page" in str(exc_info.value)

def test_get_user_orders_pagination(db_session, create_user):
    user = create_user(db_session)
    for i in range(25):
        order = Order(
            user_id=user.id,
            total=20,
            status=OrderStatus.pending,
            address="123 Main St",
            complement="Apt 4B",
            payment_link="http://payment.link"
        )
        db_session.add(order)
    db_session.commit()
    response = OrderService.get_user_orders(user.id, 2, db_session, user)
    assert response is not None
    assert len(response.orders) == 10
    assert response.page == 2
    assert response.total_pages == 3

def test_cancel_order_success(db_session, create_user):
    user = create_user(db_session)
    order = Order(
        user_id=user.id,
        total=20,
        status=OrderStatus.pending,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    response = OrderService.cancel_order(order.id, db_session, user)
    updated_order = db_session.query(Order).filter(Order.id == order.id).first()
    assert response is None
    assert updated_order.status == OrderStatus.canceled

def test_cancel_order_not_found(db_session, create_user):
    user = create_user(db_session)
    with pytest.raises(Exception) as exc_info:
        OrderService.cancel_order(uuid.uuid4(), db_session, user)
    assert "Order not found" in str(exc_info.value)

def test_cancel_order_unauthorized(db_session, create_user):
    user1 = create_user(db_session)
    user2 = create_user(db_session)
    order = Order(
        user_id=user1.id,
        total=20,
        status=OrderStatus.pending,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        OrderService.cancel_order(order.id, db_session, user2)
    assert "You are not authorized to cancel this order" in str(exc_info.value)

def test_cancel_order_invalid_status(db_session, create_user):
    user = create_user(db_session)
    order = Order(
        user_id=user.id,
        total=20,
        status=OrderStatus.delivered,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    with pytest.raises(Exception) as exc_info:
        OrderService.cancel_order(order.id, db_session, user)
    assert "Order cannot be canceled" in str(exc_info.value)

def test_cancel_order_admin_access(db_session, create_user):
    admin_user = create_user(db_session)
    admin_user.is_admin = True
    regular_user = create_user(db_session)
    order = Order(
        user_id=regular_user.id,
        total=20,
        status=OrderStatus.pending,
        address="123 Main St",
        complement="Apt 4B",
        payment_link="http://payment.link"
    )
    db_session.add(order)
    db_session.commit()
    response = OrderService.cancel_order(order.id, db_session, admin_user)
    updated_order = db_session.query(Order).filter(Order.id == order.id).first()
    assert response is None
    assert updated_order.status == OrderStatus.canceled

def test_create_order_success(db_session, create_user, monkeypatch):
    user = create_user(db_session)
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url"
    )
    db_session.add(product)
    db_session.commit()
    session_checkout = Mock()
    session_checkout.url = "https://paymentlink.com"
    mock_create = Mock(return_value=session_checkout)
    monkeypatch.setattr(client.v1.checkout.sessions, "create", mock_create)
    data = CreateOrderSchema(
        items= [
            OrderItems(slug="test-product", quantity=2)
        ],
        user=user.id
    )
    response = OrderService.create_order(data, db_session, user)
    assert response is not None
    assert response["payment_url"] == "https://paymentlink.com"

def test_create_order_with_invalid_items_quantity(db_session, create_user):
    user = create_user(db_session)
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url"
    )
    db_session.add(product)
    db_session.commit()
    data = CreateOrderSchema(
        items= [
            OrderItems(slug="test-product", quantity=16)
        ],
        user=user.id
    )
    with pytest.raises(Exception) as exc_info:
        OrderService.create_order(data, db_session, user)

    assert "Cart limit exceeded. Max 15 items permited" in str(exc_info.value)

def test_create_order_with_unauthorized_user(db_session, create_user):
    user = create_user(db_session)
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url"
    )
    db_session.add(product)
    db_session.commit()
    data = CreateOrderSchema(
        items= [
            OrderItems(slug="test-product", quantity=6)
        ],
        user=uuid.uuid4()
    )
    with pytest.raises(Exception) as exc_info:
        OrderService.create_order(data, db_session, user)

    assert "You are not authorized to create order for this user" in str(exc_info.value)
    
def test_create_product_with_empty_cart(db_session, create_user):
    user = create_user(db_session)
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url"
    )
    db_session.add(product)
    db_session.commit()
    data = CreateOrderSchema(
        items= [],
        user=user.id
    )
    with pytest.raises(Exception) as exc_info:
        OrderService.create_order(data, db_session, user)

    assert "There are no items in cart" in str(exc_info.value)

def test_create_order_without_user_address(db_session, create_user):
    user = create_user(db_session)
    user.address = ""
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url"
    )
    db_session.add(product)
    db_session.commit()
    data = CreateOrderSchema(
        items= [OrderItems(slug="test-product", quantity=6)],
        user=user.id
    )
    with pytest.raises(Exception) as exc_info:
        OrderService.create_order(data, db_session, user)

    assert "Invalid address or complement. Please verify them" in str(exc_info.value)

def test_create_order_with_invalid_item_quantity(db_session, create_user):
    user = create_user(db_session)
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url"
    )
    db_session.add(product)
    db_session.commit()
    data = CreateOrderSchema(
        items= [OrderItems(slug="test-product", quantity=6),OrderItems(slug="test-product", quantity=-1)],
        user=user.id
    )
    with pytest.raises(Exception) as exc_info:
        OrderService.create_order(data, db_session, user)

    assert "Products quantity must be greater than 0" in str(exc_info.value) 

def test_create_order_with_inactive_item(db_session, create_user):
    user = create_user(db_session)
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test Description",
        price=10,
        image_url="http://image.url",
        is_active=False
    )
    db_session.add(product)
    db_session.commit()
    data = CreateOrderSchema(
        items= [OrderItems(slug="test-product", quantity=6)],
        user=user.id
    )
    with pytest.raises(Exception) as exc_info:
        OrderService.create_order(data, db_session, user)

    assert "There are invalid product in cart" in str(exc_info.value)

