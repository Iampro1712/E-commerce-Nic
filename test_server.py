#!/usr/bin/env python3
"""
Test server with minimal dependencies
"""
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
import uuid

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-for-testing-only'
app.config['JWT_SECRET_KEY'] = 'jwt-dev-secret-key-for-testing-only'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Simple User model
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

# Simple Product model
class Product(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    inventory_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'sku': self.sku,
            'inventory_quantity': self.inventory_quantity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Routes
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'Test E-commerce API is running with SQLite'}

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already registered'}, 400
        
        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return {
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }, 201
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return {
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token
            }, 200
        else:
            return {'error': 'Invalid email or password'}, 401
            
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/auth/profile')
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return {'error': 'User not found'}, 404
        
        return {'user': user.to_dict()}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/products')
def get_products():
    try:
        products = Product.query.filter_by(is_active=True).all()
        return {
            'products': [product.to_dict() for product in products],
            'total': len(products)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return {'error': 'Admin access required'}, 403
        
        data = request.get_json()
        
        # Check if SKU exists
        if Product.query.filter_by(sku=data['sku']).first():
            return {'error': 'SKU already exists'}, 400
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            sku=data['sku'],
            inventory_quantity=data.get('inventory_quantity', 0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return {
            'message': 'Product created successfully',
            'product': product.to_dict()
        }, 201
        
    except Exception as e:
        return {'error': str(e)}, 500

def init_data():
    """Initialize test data"""
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            print("🔧 Creating test data...")
            
            # Create admin user
            admin = User(
                email='admin@test.com',
                first_name='Admin',
                last_name='User'
            )
            admin.set_password('admin123')
            admin.is_admin = True
            db.session.add(admin)
            
            # Create regular user
            user = User(
                email='user@test.com',
                first_name='Test',
                last_name='User'
            )
            user.set_password('user123')
            db.session.add(user)
            
            # Create test product
            product = Product(
                name='Test Product',
                description='A test product for development',
                price=29.99,
                sku='TEST-001',
                inventory_quantity=100
            )
            db.session.add(product)
            
            db.session.commit()
            print("✅ Test data created!")
        else:
            print("✅ Test data already exists")
        
        print("👤 Admin: admin@test.com / admin123")
        print("👤 User: user@test.com / user123")

if __name__ == '__main__':
    init_data()
    
    print("🚀 Starting test server...")
    print("📍 API available at: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/api/health")
    print("\n🔧 Test Mode - Using SQLite database")
    print("⚠️  This is for testing only!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
