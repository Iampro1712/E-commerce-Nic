import pytest
import tempfile
import os
from app import create_app, db
from app.models.user import User
from app.models.product import Product, Category
from app.models.cart import Cart
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    """Create application for testing"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            email='test@example.com',
            password='TestPassword123',
            first_name='Test',
            last_name='User'
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    """Create test admin user"""
    with app.app_context():
        admin = User(
            email='admin@example.com',
            password='AdminPassword123',
            first_name='Admin',
            last_name='User'
        )
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def category(app):
    """Create test category"""
    with app.app_context():
        category = Category(
            name='Test Category',
            slug='test-category',
            description='Test category description'
        )
        db.session.add(category)
        db.session.commit()
        return category

@pytest.fixture
def product(app, category):
    """Create test product"""
    with app.app_context():
        product = Product(
            name='Test Product',
            description='Test product description',
            sku='TEST-001',
            slug='test-product',
            price=29.99,
            category_id=category.id,
            inventory_quantity=10
        )
        db.session.add(product)
        db.session.commit()
        return product

@pytest.fixture
def auth_headers(app, user):
    """Create authorization headers for test user"""
    with app.app_context():
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def admin_headers(app, admin_user):
    """Create authorization headers for admin user"""
    with app.app_context():
        access_token = create_access_token(identity=admin_user.id)
        return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def cart_with_items(app, user, product):
    """Create cart with items for testing"""
    with app.app_context():
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.flush()
        
        cart.add_item(product, quantity=2)
        db.session.commit()
        return cart
