#!/usr/bin/env python3
"""
Quick start development server
"""
import os

# Set environment variables before importing anything
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing-only'
os.environ['JWT_SECRET_KEY'] = 'jwt-dev-secret-key-for-testing-only'
os.environ['DB_HOST'] = 'sqlite'
os.environ['DB_NAME'] = 'ecommerce_dev.db'
os.environ['PAYPAL_CLIENT_ID'] = 'mock-client-id'
os.environ['PAYPAL_CLIENT_SECRET'] = 'mock-client-secret'
os.environ['PAYPAL_MODE'] = 'sandbox'
os.environ['PAYPAL_WEBHOOK_ID'] = 'mock-webhook-id'

# Now import the app
from app import create_app, db
from app.models.user import User
from app.models.product import Product, Category
from app.models.cart import Cart

def main():
    """Run development server"""
    app = create_app()
    
    # Override database URI for SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce_dev.db'
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if not User.query.first():
            print("🔧 Creating development data...")
            
            # Create admin user
            admin = User(
                email='admin@dev.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            admin.is_admin = True
            db.session.add(admin)
            
            # Create regular user
            user = User(
                email='user@dev.com',
                password='user123',
                first_name='Test',
                last_name='User',
                phone='+505 8888-8888'
            )
            db.session.add(user)
            
            # Create category
            category = Category(
                name='Electronics',
                slug='electronics',
                description='Electronic devices and gadgets',
                is_active=True,
                sort_order=1
            )
            db.session.add(category)
            db.session.flush()
            
            # Create product
            product = Product(
                name='Test Smartphone',
                description='A test smartphone for development',
                short_description='Test smartphone',
                sku='PHONE-DEV-001',
                slug='test-smartphone',
                price=299.99,
                compare_price=399.99,
                category_id=category.id,
                inventory_quantity=50,
                is_featured=True,
                is_active=True
            )
            db.session.add(product)
            db.session.flush()
            
            # Create cart for user
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            
            db.session.commit()
            print("✅ Development data created!")
        else:
            print("✅ Development data already exists")
        
        print(f"👤 Admin: admin@dev.com / admin123")
        print(f"👤 User: user@dev.com / user123")
    
    print("🚀 Starting development server...")
    print("📍 API available at: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/api/health")
    print("\n🔧 Development Mode - Using SQLite database")
    print("⚠️  This is for development only!")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

if __name__ == '__main__':
    main()
