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
    
    # Configure logging with UTF-8 encoding to handle Unicode characters
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/production_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set console output encoding to UTF-8 for Windows
    if sys.platform.startswith('win'):
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        elif hasattr(sys.stdout, 'buffer'):
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def create_production_app():
    """Create and configure the production Flask application"""
    try:
        from secure_server import app
        from flask import request
        
        # Import operational AI engine
        sys.path.append(os.path.join(os.path.dirname(__file__), 'predictor'))
        try:
            from operational_ai_engine import operational_ai
            operational_features_available = True
        except ImportError:
            operational_features_available = False
            logging.warning("Operational AI engine not available, using basic features")
        
        # Add operational endpoints if available
        if operational_features_available:
            @app.route('/api/operational/dashboard-data')
            def get_operational_dashboard():
                try:
                    data = operational_ai.create_operational_dashboard_data()
                    return {'status': 'success', 'data': data}
                except Exception as e:
                    logging.error(f"Failed to get operational dashboard data: {e}")
                    return {'status': 'error', 'message': str(e)}, 500
            
            @app.route('/api/operational/recommendations', methods=['POST'])
            def get_intelligent_recommendations():
                try:
                    user_criteria = request.get_json() or {}
                    recommendations = operational_ai.generate_intelligent_recommendations(user_criteria)
                    return {'status': 'success', 'recommendations': recommendations}
                except Exception as e:
                    logging.error(f"Failed to generate recommendations: {e}")
                    return {'status': 'error', 'message': str(e)}, 500
            
            @app.route('/api/operational/real-time-costs')
            def get_real_time_costs():
                try:
                    costs = operational_ai.monitor_real_time_costs()
                    return {'status': 'success', 'costs': costs}
                except Exception as e:
                    logging.error(f"Failed to get real-time costs: {e}")
                    return {'status': 'error', 'message': str(e)}, 500
            
            @app.route('/api/operational/current-time-pricing')
            def get_current_time_pricing():
                try:
                    region = request.args.get('region', 'us-east-1')
                    pricing = operational_ai.get_current_time_pricing(region)
                    return {'status': 'success', 'pricing': pricing}
                except Exception as e:
                    logging.error(f"Failed to get current time pricing: {e}")
                    return {'status': 'error', 'message': str(e)}, 500
        
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
