"""
Development configuration for local testing without external dependencies
"""
import os
from datetime import timedelta

class DevConfig:
    """Development configuration with minimal dependencies"""
    SECRET_KEY = 'dev-secret-key-for-testing-only'
    JWT_SECRET_KEY = 'jwt-dev-secret-key-for-testing-only'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Longer for development
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Use SQLite for development if MySQL is not available
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ecommerce_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mock PayPal configuration for development
    PAYPAL_CLIENT_ID = 'mock-client-id'
    PAYPAL_CLIENT_SECRET = 'mock-client-secret'
    PAYPAL_MODE = 'sandbox'
    PAYPAL_WEBHOOK_ID = 'mock-webhook-id'
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16777216  # 16MB
    
    # CORS Configuration
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"]
    
    # Development settings
    DEBUG = True
    TESTING = False
