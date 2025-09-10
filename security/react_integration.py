"""
Flask + React Integration
Serves React build files in production and handles API routing
"""

import os
from flask import send_from_directory, send_file

def setup_react_integration(app):
    """Configure Flask to serve React build files"""
    
    # Path to React build directory
    react_build_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
    react_static_path = os.path.join(react_build_path, 'static')
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        """Serve React app for all non-API routes"""
        # API routes are handled by existing Flask routes
        if path.startswith('api/'):
            return {'error': 'API endpoint not found'}, 404
            
        # Serve static files
        if path and os.path.exists(os.path.join(react_build_path, path)):
            return send_from_directory(react_build_path, path)
            
        # Serve React index.html for all other routes (SPA routing)
        index_path = os.path.join(react_build_path, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            # Fallback to existing enterprise dashboard if React build not available
            return send_from_directory(
                os.path.join(os.path.dirname(__file__), '..', 'dashboard'),
                'enterprise_dashboard.html'
            )
    
    @app.route('/static/<path:path>')
    def serve_react_static(path):
        """Serve React static assets"""
        if os.path.exists(react_static_path):
            return send_from_directory(react_static_path, path)
        return {'error': 'Static file not found'}, 404
    
    return app
