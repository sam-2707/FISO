"""
Production Configuration for FISO Backend Services
Centralized configuration management for all production components
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

class ProductionConfig:
    """Production configuration settings"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'fiso-production-key-2024')
    DEBUG = False
    TESTING = False
    
    # Database settings
    DATABASE_PATH = str(DATA_DIR / "fiso_production.db")
    DATABASE_TIMEOUT = 30
    DATABASE_MAX_CONNECTIONS = 10
    
    # ML Model settings
    MODEL_UPDATE_INTERVAL = 3600  # 1 hour in seconds
    PREDICTION_CACHE_TTL = 300    # 5 minutes
    MODEL_PERFORMANCE_THRESHOLD = 0.85
    
    # Cloud Provider API settings
    CLOUD_API_TIMEOUT = 30
    CLOUD_API_RETRY_COUNT = 3
    CLOUD_API_CACHE_TTL = 900  # 15 minutes
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # Azure Configuration
    AZURE_SUBSCRIPTION_ID = os.environ.get('AZURE_SUBSCRIPTION_ID')
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
    AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
    
    # GCP Configuration
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
    GCP_SERVICE_ACCOUNT_PATH = os.environ.get('GCP_SERVICE_ACCOUNT_PATH')
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = str(LOGS_DIR / "production.log")
    
    # Performance monitoring
    ENABLE_METRICS = True
    METRICS_COLLECTION_INTERVAL = 60  # seconds
    
    # Cache settings
    CACHE_TYPE = 'simple'  # Can be 'redis' in production
    CACHE_DEFAULT_TIMEOUT = 300
    
    # API Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "100 per hour"
    
    # CORS settings for frontend integration
    CORS_ORIGINS = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5000",  # Flask dev server
        "https://fiso-app.com",   # Production domain
    ]

class DevelopmentConfig(ProductionConfig):
    """Development configuration with debug settings"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    MODEL_UPDATE_INTERVAL = 300  # 5 minutes for faster testing
    PREDICTION_CACHE_TTL = 60    # 1 minute
    RATELIMIT_DEFAULT = "1000 per hour"  # More lenient for dev

class TestingConfig(ProductionConfig):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ":memory:"  # In-memory database for tests
    CACHE_TYPE = 'null'
    ENABLE_METRICS = False

# Configuration selection
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])

# Export current configuration
current_config = get_config()

# Validation helper
def validate_config():
    """Validate that required configuration is present"""
    errors = []
    
    # Check database path is writable
    try:
        db_path = Path(current_config.DATABASE_PATH)
        if db_path != Path(":memory:"):
            db_path.parent.mkdir(exist_ok=True)
            # Test write access
            test_file = db_path.parent / ".write_test"
            test_file.touch()
            test_file.unlink()
    except Exception as e:
        errors.append(f"Database path not writable: {e}")
    
    # Check cloud provider configuration
    if not any([
        current_config.AWS_ACCESS_KEY_ID,
        current_config.AZURE_CLIENT_ID,
        current_config.GCP_PROJECT_ID
    ]):
        errors.append("No cloud provider credentials configured")
    
    if errors:
        print("⚠️ Configuration warnings:")
        for error in errors:
            print(f"  - {error}")
        print("  Application will use fallback data where needed")
    else:
        print("✅ Configuration validation passed")
    
    return len(errors) == 0

if __name__ == "__main__":
    print(f"Current configuration: {current_config.__name__}")
    validate_config()