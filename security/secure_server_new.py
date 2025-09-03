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
        if not response_data.get('success'):
            if 'Authentication' in str(response_data.get('error', {})):
                status_code = 401
            elif response_data.get('error', {}).get('code'):
                status_code = response_data['error']['code']
            else:
                status_code = 500
        
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
def status():
    """System status endpoint"""
    try:
        # Prepare request data
        request_data = {
            "action": "status"
        }
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 200
        if not response_data.get('success'):
            if 'Authentication' in str(response_data.get('error', {})):
                status_code = 401
            elif response_data.get('error', {}).get('code'):
                status_code = response_data['error']['code']
            else:
                status_code = 500
        
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
        # Get request data
        request_data = request.get_json() or {}
        request_data["action"] = "generate_api_key"
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 200
        if not response_data.get('success'):
            if 'Authentication' in str(response_data.get('error', {})):
                status_code = 401
            elif response_data.get('error', {}).get('code'):
                status_code = response_data['error']['code']
            else:
                status_code = 500
        
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

@app.route('/compatible_dashboard.html', methods=['GET'])
def compatible_dashboard():
    """Serve the compatible dashboard HTML file with table-based layout"""
    try:
        # Get the dashboard file path
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'compatible_dashboard.html')
        
        # Read and serve the dashboard file
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        response = make_response(dashboard_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        return make_response(f"Error loading dashboard: {str(e)}", 500)

@app.route('/simple_dashboard.html', methods=['GET'])
def simple_dashboard():
    """Serve the simple dashboard HTML file for testing"""
    try:
        # Get the dashboard file path
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'simple_dashboard.html')
        
        # Read and serve the dashboard file
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        response = make_response(dashboard_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        return make_response(f"Error loading simple dashboard: {str(e)}", 500)

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
            "generate_api_key": "/auth/generate-key",
            "dashboards": {
                "compatible": "/compatible_dashboard.html",
                "simple": "/simple_dashboard.html"
            }
        },
        "authentication": "API Key or JWT Token required"
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
    
    print("\n🎨 Dashboard Options:")
    print("   http://localhost:5000/compatible_dashboard.html - Full-featured with proper styling")
    print("   http://localhost:5000/simple_dashboard.html     - Simple testing interface")
    
    print("\n🧪 Test Commands:")
    print(f"   curl -H 'X-API-Key: {demo_key['api_key']}' http://localhost:5000/health")
    
    print("\n🔒 Security Features:")
    print("   ✅ JWT Authentication")
    print("   ✅ API Key Authentication") 
    print("   ✅ Rate Limiting")
    print("   ✅ CORS Support")
    
    print(f"\n🌐 Server starting on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
