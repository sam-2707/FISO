# FISO Secure API Server
# Flask-based secure web server for multi-cloud orchestration

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime

# Add security module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security'))

try:
    from secure_api import SecureMultiCloudAPI
except ImportError:
    print("Error: Could not import secure_api module")
    print("Make sure fiso_security.py and secure_api.py are in the security/ directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for web dashboard access

# Initialize secure API
secure_api = SecureMultiCloudAPI()

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def add_security_headers(response):
    """Add security headers to response"""
    headers = secure_api.security.get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Get request parameters
        provider = request.args.get('provider', 'auto')
        
        # Prepare request data
        request_data = {
            "action": "health",
            "provider": provider
        }
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 401 if not response_data.get('success') and 'Authentication' in str(response_data.get('error', {})) else 200
        if not response_data.get('success') and response_data.get('error', {}).get('code'):
            status_code = response_data['error']['code']
            
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """Multi-cloud orchestration endpoint"""
    try:
        # Get request data
        request_data = request.get_json() or {}
        request_data["action"] = "orchestrate"
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 200
        if not response_data.get('success') and response_data.get('error', {}).get('code'):
            status_code = response_data['error']['code']
            
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/status', methods=['GET'])
def system_status():
    """System status endpoint"""
    try:
        request_data = {"action": "status"}
        
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        status_code = 200
        if not response_data.get('success') and response_data.get('error', {}).get('code'):
            status_code = response_data['error']['code']
            
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics (admin only)"""
    try:
        request_data = {"action": "metrics"}
        
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        status_code = 200
        if not response_data.get('success') and response_data.get('error', {}).get('code'):
            status_code = response_data['error']['code']
            
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/auth/generate-key', methods=['POST'])
def generate_api_key():
    """Generate new API key"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', f'user_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}')
        permissions = data.get('permissions', ['read', 'orchestrate'])
        
        # For demo purposes, allow key generation without authentication
        # In production, this would require admin authentication
        
        key_data = secure_api.security.generate_api_key(user_id, permissions)
        
        response_data = {
            "success": True,
            "data": key_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = make_response(jsonify(response_data), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Failed to generate API key",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/auth/generate-jwt', methods=['POST'])
def generate_jwt():
    """Generate JWT token"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', f'user_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}')
        permissions = data.get('permissions', ['read'])
        
        jwt_token = secure_api.security.generate_jwt_token(user_id, permissions)
        
        response_data = {
            "success": True,
            "data": {
                "jwt_token": jwt_token,
                "user_id": user_id,
                "permissions": permissions,
                "expires_in": "24 hours"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = make_response(jsonify(response_data), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Failed to generate JWT token",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    try:
        docs = secure_api.get_api_documentation()
        
        response_data = {
            "success": True,
            "data": docs,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = make_response(jsonify(response_data), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Failed to get documentation",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API information"""
    info = {
        "name": "FISO Secure Multi-Cloud API",
        "version": "1.0.0",
        "description": "Enterprise-grade secure API for multi-cloud orchestration",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "orchestrate": "/orchestrate",
            "status": "/status",
            "metrics": "/metrics",
            "generate_api_key": "/auth/generate-key",
            "generate_jwt": "/auth/generate-jwt",
            "documentation": "/docs"
        },
        "authentication": "API Key or JWT Token required",
        "documentation": "GET /docs"
    }
    
    response = make_response(jsonify(info), 200)
    return add_security_headers(response)

if __name__ == '__main__':
    print("🚀 Starting FISO Secure API Server...")
    print("=====================================")
    
    # Generate demo credentials
    demo_key = secure_api.security.generate_api_key("demo_user", ["read", "orchestrate", "admin"])
    demo_jwt = secure_api.security.generate_jwt_token("demo_user", ["read", "orchestrate"])
    
    print(f"🔑 Demo API Key: {demo_key['api_key']}")
    print(f"🎫 Demo JWT Token: {demo_jwt}")
    print("\n📖 API Endpoints:")
    print("   GET  /              - API information")
    print("   GET  /health        - Health check")
    print("   POST /orchestrate   - Multi-cloud orchestration")
    print("   GET  /status        - System status")
    print("   GET  /metrics       - System metrics (admin)")
    print("   POST /auth/generate-key - Generate API key")
    print("   POST /auth/generate-jwt - Generate JWT token")
    print("   GET  /docs          - API documentation")
    
    print("\n🧪 Test Commands:")
    print(f"   curl -H 'X-API-Key: {demo_key['api_key']}' http://localhost:5000/health")
    print(f"   curl -H 'Authorization: Bearer {demo_jwt}' http://localhost:5000/status")
    
    print("\n🔒 Security Features:")
    print("   ✅ JWT Authentication")
    print("   ✅ API Key Authentication")
    print("   ✅ Rate Limiting")
    print("   ✅ Request Validation")
    print("   ✅ Security Headers")
    print("   ✅ CORS Support")
    
    print(f"\n🌐 Server starting on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
