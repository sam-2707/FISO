#!/usr/bin/env python3
"""
FISO Production System Startup Script
Starts both backend API and provides frontend instructions
"""

import subprocess
import sys
import time
import os
import threading
from pathlib import Path

def start_backend():
    """Start the production API server"""
    print("🚀 Starting FISO Production API Server...")
    try:
        # Change to the project root directory
        os.chdir(Path(__file__).parent)
        
        # Start the API server
        subprocess.run([sys.executable, "production_api_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def start_frontend():
    """Instructions for starting frontend"""
    print("\n" + "="*60)
    print("🎯 FISO PRODUCTION SYSTEM READY")
    print("="*60)
    print("📊 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n🌐 To start the frontend:")
    print("   cd frontend")
    print("   npm start")
    print("\n✅ Then visit: http://localhost:3000")
    print("="*60)

def main():
    """Main startup function"""
    print("🎯 FISO Production System Startup")
    print("="*40)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    
    # Show frontend instructions
    start_frontend()
    
    try:
        # Keep main thread alive
        backend_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Shutting down FISO Production System")

if __name__ == "__main__":
    main()