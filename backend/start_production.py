#!/usr/bin/env python3
"""
FISO Production Server Launcher
Starts all production backend services with proper integration
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from threading import Thread
import signal

# Add backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    from config.production import get_config, validate_config
    from database.productionDB import ProductionDatabase
    from services.realMLService import RealMLService
    from productionAPI import create_app
except ImportError as e:
    print(f"❌ Failed to import production modules: {e}")
    print("Make sure you're running from the backend directory and have installed requirements")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/startup.log', 'a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionServer:
    """Production server manager"""
    
    def __init__(self):
        self.config = get_config()
        self.db = None
        self.ml_service = None
        self.flask_app = None
        self.processes = []
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        self.shutdown()
    
    def validate_environment(self):
        """Validate environment and configuration"""
        logger.info("🔍 Validating environment...")
        
        # Validate configuration
        if not validate_config():
            logger.warning("Configuration validation failed, using fallback settings")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ required")
            return False
        
        # Check required directories
        for directory in ['logs', 'data', 'models']:
            Path(directory).mkdir(exist_ok=True)
        
        logger.info("✅ Environment validation completed")
        return True
    
    def initialize_database(self):
        """Initialize production database"""
        logger.info("🗄️ Initializing production database...")
        try:
            self.db = ProductionDatabase()
            self.db.init_database()
            
            # Run initial data cleanup
            cleaned_records = self.db.cleanup_old_data(days=30)
            if cleaned_records > 0:
                logger.info(f"Cleaned up {cleaned_records} old database records")
            
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    def initialize_ml_service(self):
        """Initialize ML service"""
        logger.info("🧠 Initializing ML service...")
        try:
            self.ml_service = RealMLService()
            
            # Check if models need training
            if self.ml_service.should_retrain_models():
                logger.info("📈 Training ML models...")
                self.ml_service.train_all_models()
            
            logger.info("✅ ML service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ ML service initialization failed: {e}")
            return False
    
    def start_flask_app(self):
        """Start Flask application"""
        logger.info("🌐 Starting Flask application...")
        try:
            self.flask_app = create_app()
            
            # Start Flask in a separate thread for development
            # In production, use gunicorn instead
            if self.config.DEBUG:
                flask_thread = Thread(
                    target=self.flask_app.run,
                    kwargs={
                        'host': '0.0.0.0',
                        'port': 5000,
                        'debug': False,  # Disable debug in thread
                        'use_reloader': False
                    },
                    daemon=True
                )
                flask_thread.start()
                logger.info("✅ Flask application started in development mode")
            else:
                # Production: Use gunicorn
                gunicorn_cmd = [
                    'gunicorn',
                    '--bind', '0.0.0.0:5000',
                    '--workers', '4',
                    '--worker-class', 'gevent',
                    '--timeout', '120',
                    '--keep-alive', '5',
                    '--max-requests', '1000',
                    '--preload',
                    'productionAPI:create_app()'
                ]
                
                process = subprocess.Popen(gunicorn_cmd, cwd=backend_path)
                self.processes.append(process)
                logger.info("✅ Flask application started with gunicorn")
            
            return True
        except Exception as e:
            logger.error(f"❌ Flask application startup failed: {e}")
            return False
    
    def start_background_tasks(self):
        """Start background maintenance tasks"""
        logger.info("⚙️ Starting background tasks...")
        
        def model_update_task():
            """Background task to update ML models periodically"""
            while not self.shutdown_requested:
                try:
                    time.sleep(self.config.MODEL_UPDATE_INTERVAL)
                    if self.ml_service and self.ml_service.should_retrain_models():
                        logger.info("🔄 Retraining ML models...")
                        self.ml_service.train_all_models()
                except Exception as e:
                    logger.error(f"Model update task error: {e}")
        
        def database_cleanup_task():
            """Background task to clean up old database records"""
            while not self.shutdown_requested:
                try:
                    time.sleep(86400)  # Run daily
                    if self.db:
                        cleaned = self.db.cleanup_old_data(days=30)
                        if cleaned > 0:
                            logger.info(f"🧹 Cleaned up {cleaned} old database records")
                except Exception as e:
                    logger.error(f"Database cleanup task error: {e}")
        
        # Start background threads
        Thread(target=model_update_task, daemon=True).start()
        Thread(target=database_cleanup_task, daemon=True).start()
        
        logger.info("✅ Background tasks started")
    
    def health_check(self):
        """Perform system health check"""
        logger.info("🏥 Performing health check...")
        
        checks = {
            'database': False,
            'ml_service': False,
            'flask_app': False
        }
        
        # Check database
        try:
            if self.db:
                self.db.get_connection().execute("SELECT 1").fetchone()
                checks['database'] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
        
        # Check ML service
        try:
            if self.ml_service:
                self.ml_service.get_model_performance()
                checks['ml_service'] = True
        except Exception as e:
            logger.error(f"ML service health check failed: {e}")
        
        # Check Flask app
        checks['flask_app'] = self.flask_app is not None
        
        healthy = all(checks.values())
        status = "✅ Healthy" if healthy else "⚠️ Partial"
        
        logger.info(f"Health check: {status}")
        for service, status in checks.items():
            logger.info(f"  {service}: {'✅' if status else '❌'}")
        
        return healthy
    
    def shutdown(self):
        """Gracefully shutdown all services"""
        logger.info("🔄 Shutting down production server...")
        
        # Stop background processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
        
        # Close database connections
        if self.db:
            try:
                self.db.close_all_connections()
                logger.info("✅ Database connections closed")
            except Exception as e:
                logger.error(f"Error closing database: {e}")
        
        logger.info("✅ Production server shutdown completed")
    
    def start(self):
        """Start all production services"""
        logger.info("🚀 Starting FISO Production Server...")
        
        try:
            # Validation
            if not self.validate_environment():
                logger.error("Environment validation failed")
                return False
            
            # Initialize services
            if not self.initialize_database():
                logger.error("Database initialization failed")
                return False
            
            if not self.initialize_ml_service():
                logger.error("ML service initialization failed")
                return False
            
            if not self.start_flask_app():
                logger.error("Flask application startup failed")
                return False
            
            # Start background tasks
            self.start_background_tasks()
            
            # Initial health check
            time.sleep(2)  # Give services time to start
            self.health_check()
            
            logger.info("🎉 FISO Production Server started successfully!")
            logger.info("📊 Services available:")
            logger.info("  - API Server: http://localhost:5000")
            logger.info("  - Health Check: http://localhost:5000/api/production/health")
            logger.info("  - Metrics: http://localhost:5000/api/production/metrics")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Production server startup failed: {e}")
            self.shutdown()
            return False

def main():
    """Main entry point"""
    print("🔥 FISO Production Server")
    print("=" * 50)
    
    server = ProductionServer()
    
    if server.start():
        try:
            # Keep the main thread alive
            while not server.shutdown_requested:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            server.shutdown()
    else:
        print("❌ Failed to start production server")
        sys.exit(1)

if __name__ == "__main__":
    main()