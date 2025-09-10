#!/usr/bin/env python3
"""
FISO Production Server
Production-ready WSGI server configuration for FISO Enterprise Intelligence Platform
"""

import os
import sys
import logging
from datetime import datetime, timezone

# Production server imports
from waitress import serve
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import WSGIRequestHandler

# Add security directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'security'))

def setup_production_logging():
    """Configure production logging"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/production_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def create_production_app():
    """Create and configure the production Flask application"""
    try:
        from secure_server import app
        
        # Ensure production configuration
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'ENVIRONMENT': 'production',
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'prod-secret-key-change-me'),
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
        })
        
        return app
        
    except ImportError as e:
        logging.error(f"Failed to import secure_server: {e}")
        raise

class ProductionRequestHandler(WSGIRequestHandler):
    """Custom request handler with proper logging"""
    
    def log_request(self, code='-', size='-'):
        """Log requests in production format"""
        self.log('info', f"{self.address_string()} - {self.requestline} - {code} - {size}")

def main():
    """Main production server entry point"""
    setup_production_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting FISO Production Server...")
    
    # Create production Flask app
    app = create_production_app()
    
    # Production server configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    threads = int(os.environ.get('THREADS', 4))
    
    logger.info(f"🌐 Production Server Configuration:")
    logger.info(f"   • Host: {host}")
    logger.info(f"   • Port: {port}")
    logger.info(f"   • Threads: {threads}")
    logger.info(f"   • Environment: {app.config['ENVIRONMENT']}")
    
    logger.info("======================================================================")
    logger.info("🎯 FISO Enterprise Intelligence Platform - PRODUCTION MODE")
    logger.info("======================================================================")
    
    try:
        # Start production server with Waitress
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            url_scheme='https' if os.environ.get('HTTPS', '').lower() == 'true' else 'http',
            channel_timeout=120,
            cleanup_interval=30,
            max_request_body_size=1048576,  # 1MB
            send_bytes=18000,
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Production server stopped by user")
    except Exception as e:
        logger.error(f"❌ Production server error: {e}")
        raise

if __name__ == '__main__':
    main()
