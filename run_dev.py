#!/usr/bin/env python3
"""
Development server runner with SQLite database
"""
import os
import sys
from dev_config import DevConfig

def create_dev_app():
    """Create app with development configuration"""
    # Set environment variable to avoid loading default config
    os.environ['FLASK_ENV'] = 'development'

    # Create Flask app directly with dev config
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # Initialize extensions
    from app import db, jwt, migrate
    from flask_cors import CORS

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.payments import payments_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'E-commerce API is running (Development Mode)'}

    return app

def init_dev_data(app):
    """Initialize development data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("✅ Development data already exists")
            return
        
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
        print(f"👤 Admin: admin@dev.com / admin123")
        print(f"👤 User: user@dev.com / user123")

def main():
    """Run development server"""
    app = create_dev_app()
    
    # Initialize development data
    init_dev_data(app)
    
    print("🚀 Starting development server...")
    print("📍 API available at: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/api/health")
    print("📖 API Documentation: See API_DOCUMENTATION.md")
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
