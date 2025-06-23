#!/usr/bin/env python3
"""
Script to initialize the database with tables and optional sample data
Suitable for both development and production environments
"""
import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.product import Product, Category, ProductImage
from app.models.cart import Cart
from werkzeug.security import generate_password_hash
import uuid

def create_sample_data():
    """Create sample data for development"""
    
    # Create admin user
    admin = User(
        email='admin@ecommerce.com',
        password='AdminPassword123',
        first_name='Admin',
        last_name='User'
    )
    admin.is_admin = True
    db.session.add(admin)
    
    # Create regular user
    user = User(
        email='user@ecommerce.com',
        password='UserPassword123',
        first_name='John',
        last_name='Doe',
        phone='+505 8888-8888'
    )
    db.session.add(user)
    
    # Create categories
    electronics = Category(
        name='Electronics',
        slug='electronics',
        description='Electronic devices and gadgets',
        is_active=True,
        sort_order=1
    )
    db.session.add(electronics)
    
    clothing = Category(
        name='Clothing',
        slug='clothing',
        description='Fashion and apparel',
        is_active=True,
        sort_order=2
    )
    db.session.add(clothing)
    
    books = Category(
        name='Books',
        slug='books',
        description='Books and literature',
        is_active=True,
        sort_order=3
    )
    db.session.add(books)
    
    db.session.flush()  # Get category IDs
    
    # Create products
    products_data = [
        {
            'name': 'Smartphone Pro Max',
            'description': 'Latest smartphone with advanced features',
            'short_description': 'High-end smartphone with excellent camera',
            'sku': 'PHONE-001',
            'slug': 'smartphone-pro-max',
            'price': 899.99,
            'compare_price': 999.99,
            'category_id': electronics.id,
            'inventory_quantity': 50,
            'is_featured': True
        },
        {
            'name': 'Wireless Headphones',
            'description': 'Premium wireless headphones with noise cancellation',
            'short_description': 'Wireless headphones with great sound quality',
            'sku': 'HEADPHONES-001',
            'slug': 'wireless-headphones',
            'price': 199.99,
            'category_id': electronics.id,
            'inventory_quantity': 30
        },
        {
            'name': 'Cotton T-Shirt',
            'description': '100% cotton comfortable t-shirt',
            'short_description': 'Comfortable cotton t-shirt for everyday wear',
            'sku': 'TSHIRT-001',
            'slug': 'cotton-t-shirt',
            'price': 24.99,
            'category_id': clothing.id,
            'inventory_quantity': 100
        },
        {
            'name': 'Programming Guide',
            'description': 'Complete guide to modern programming',
            'short_description': 'Learn programming with this comprehensive guide',
            'sku': 'BOOK-001',
            'slug': 'programming-guide',
            'price': 39.99,
            'category_id': books.id,
            'inventory_quantity': 25,
            'is_digital': True
        }
    ]
    
    for product_data in products_data:
        product = Product(**product_data)
        db.session.add(product)
    
    db.session.flush()  # Get product IDs
    
    # Create cart for user
    cart = Cart(user_id=user.id)
    db.session.add(cart)
    
    db.session.commit()
    print("✅ Sample data created successfully!")

def init_database():
    """Initialize database with tables and optional sample data"""
    app = create_app()

    with app.app_context():
        try:
            # Test database connection
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)

        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created!")
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            sys.exit(1)

        # Check environment - only create sample data in development
        flask_env = os.environ.get('FLASK_ENV', 'development')
        create_samples = os.environ.get('CREATE_SAMPLE_DATA', 'true').lower() == 'true'

        if flask_env == 'production' and not create_samples:
            print("🚀 Production environment detected. Skipping sample data creation.")
            print("💡 To create sample data in production, set CREATE_SAMPLE_DATA=true")
            return

        # Check if data already exists
        if User.query.first():
            print("⚠️  Database already contains data. Skipping sample data creation.")
            return

        if create_samples:
            print("📝 Creating sample data...")
            create_sample_data()
        else:
            print("⏭️  Sample data creation skipped.")

def create_admin_user():
    """Create admin user from environment variables"""
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_email or not admin_password:
        print("⚠️  ADMIN_EMAIL and ADMIN_PASSWORD not set. Skipping admin user creation.")
        return

    # Check if admin already exists
    if User.query.filter_by(email=admin_email).first():
        print(f"⚠️  Admin user {admin_email} already exists.")
        return

    admin = User(
        email=admin_email,
        password=admin_password,
        first_name='Admin',
        last_name='User'
    )
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print(f"✅ Admin user {admin_email} created successfully!")

if __name__ == '__main__':
    print("🚀 Initializing database...")
    init_database()

    # Create admin user if environment variables are set
    app = create_app()
    with app.app_context():
        create_admin_user()

    print("🎉 Database initialization completed!")
