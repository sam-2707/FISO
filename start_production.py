#!/usr/bin/env python3
"""
FISO Production Server - Startup Script
Clean version without Unicode issues for Windows compatibility
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUNBUFFERED'] = '1'

# Configure logging for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Start the FISO production server"""
    try:
        logger.info("Starting FISO Production Server...")
        logger.info("API Documentation: http://localhost:5000/docs")  
        logger.info("Health Check: http://localhost:5000/health")
        logger.info("Real Cost Summary: http://localhost:5000/cost/summary")
        logger.info("Real Recommendations: http://localhost:5000/recommendations")
        
        # Start the server on port 5000 to match frontend expectations
        uvicorn.run(
            "real_api_production:app",
            host="0.0.0.0",  
            port=5000,  # Changed from 8000 to 5000
            reload=False,  # Disable reload for production
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()