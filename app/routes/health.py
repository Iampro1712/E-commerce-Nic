"""
Health check and utility routes for monitoring and deployment
"""
from flask import Blueprint, jsonify, current_app
from app import db
import os
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for load balancers and monitoring
    Returns application status and basic system information
    """
    try:
        # Test database connection
        db.engine.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'database': db_status,
        'services': {
            'database': db_status,
            'paypal': 'configured' if current_app.config.get('PAYPAL_CLIENT_ID') else 'not configured'
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@health_bp.route('/api/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint - indicates if the app is ready to serve traffic
    """
    try:
        # Test database connection
        db.engine.execute('SELECT 1')
        
        # Check if required environment variables are set
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            return jsonify({
                'status': 'not ready',
                'reason': f'Missing required environment variables: {", ".join(missing_vars)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 503
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'reason': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/api/live', methods=['GET'])
def liveness_check():
    """
    Liveness check endpoint - indicates if the app is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
