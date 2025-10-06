#!/usr/bin/env python3
"""
FISO System Recovery - Fix all service issues
Quick diagnostic and repair script
"""

import requests
import subprocess
import time
import json
import os
from datetime import datetime

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code, response.text[:100]
    except requests.exceptions.ConnectionError:
        return False, "CONNECTION_REFUSED", "Service not running"
    except requests.exceptions.Timeout:
        return False, "TIMEOUT", "Service not responding"
    except Exception as e:
        return False, "ERROR", str(e)

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 FISO System Recovery - Diagnostic and Repair")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check current service status
    services = {
        'Production API': 'http://localhost:5000/health',
        'Real-time Server': 'http://localhost:5001/health',
        'React Frontend': 'http://localhost:3000'
    }
    
    print("📊 Current Service Status:")
    print("-" * 30)
    for name, url in services.items():
        is_healthy, status, details = check_service(name, url)
        status_icon = "✅" if is_healthy else "❌"
        print(f"{status_icon} {name}: {status}")
        if not is_healthy:
            print(f"   └─ {details}")
    print()
    
    # Check specific API endpoints
    print("🔌 API Endpoint Tests:")
    print("-" * 25)
    
    endpoints = {
        'Health Check': 'http://localhost:5000/health',
        'Pricing Data': 'http://localhost:5000/api/pricing-data',
        'Optimization': 'http://localhost:5000/api/optimization-recommendations',
        'AI Prediction': 'http://localhost:5000/api/ai/predict-costs',
        'Real-time Health': 'http://localhost:5001/health'
    }
    
    for name, url in endpoints.items():
        is_healthy, status, details = check_service(name, url, timeout=10)
        status_icon = "✅" if is_healthy else "❌"
        print(f"{status_icon} {name}: {status}")
    print()
    
    # Test POST endpoints
    print("📝 POST Endpoint Tests:")
    print("-" * 22)
    
    post_tests = [
        {
            'name': 'AI Cost Prediction',
            'url': 'http://localhost:5000/api/ai/predict-costs',
            'data': {'provider': 'aws', 'service': 'ec2', 'days': 1}
        },
        {
            'name': 'Natural Language Query',
            'url': 'http://localhost:5000/api/ai/natural-query',
            'data': {'query': 'What are my current costs?'}
        }
    ]
    
    for test in post_tests:
        try:
            response = requests.post(test['url'], json=test['data'], timeout=10)
            is_healthy = response.status_code == 200
            status_icon = "✅" if is_healthy else "❌"
            print(f"{status_icon} {test['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {str(e)[:50]}")
    print()
    
    # Check if React build exists
    print("📦 Frontend Build Check:")
    print("-" * 24)
    
    build_path = "frontend/build"
    if os.path.exists(build_path):
        build_files = os.listdir(build_path)
        if build_files:
            print("✅ React build directory exists with files")
        else:
            print("❌ React build directory is empty")
            print("   └─ Running npm run build...")
            success, stdout, stderr = run_command("npm run build", cwd="frontend")
            if success:
                print("   └─ ✅ Build completed successfully")
            else:
                print(f"   └─ ❌ Build failed: {stderr[:100]}")
    else:
        print("❌ React build directory doesn't exist")
        print("   └─ Running npm run build...")
        success, stdout, stderr = run_command("npm run build", cwd="frontend")
        if success:
            print("   └─ ✅ Build completed successfully")
        else:
            print(f"   └─ ❌ Build failed: {stderr[:100]}")
    print()
    
    # Quick fixes
    print("🛠️ Quick System Fixes:")
    print("-" * 22)
    
    # Check if we can start a simple frontend server
    frontend_healthy, _, _ = check_service("Frontend", "http://localhost:3000")
    if not frontend_healthy:
        print("🔄 Attempting to start React development server...")
        print("   (This may take a moment...)")
        
        # Try to serve the build directory directly if it exists
        if os.path.exists("frontend/build"):
            print("   └─ Starting static file server for built React app...")
            try:
                import http.server
                import socketserver
                import threading
                
                def start_static_server():
                    os.chdir("frontend/build")
                    handler = http.server.SimpleHTTPRequestHandler
                    with socketserver.TCPServer(("", 3000), handler) as httpd:
                        httpd.serve_forever()
                
                server_thread = threading.Thread(target=start_static_server)
                server_thread.daemon = True
                server_thread.start()
                
                time.sleep(3)  # Give it time to start
                
                frontend_healthy, _, _ = check_service("Frontend", "http://localhost:3000")
                if frontend_healthy:
                    print("   └─ ✅ Static server started successfully")
                else:
                    print("   └─ ❌ Static server failed to start")
                    
            except Exception as e:
                print(f"   └─ ❌ Failed to start static server: {str(e)}")
    
    print()
    print("🎯 System Recovery Summary:")
    print("-" * 28)
    
    # Final status check
    final_status = {}
    for name, url in services.items():
        is_healthy, status, _ = check_service(name, url)
        final_status[name] = is_healthy
    
    healthy_count = sum(final_status.values())
    total_count = len(final_status)
    
    print(f"📊 Services Online: {healthy_count}/{total_count}")
    for name, is_healthy in final_status.items():
        status_icon = "✅" if is_healthy else "❌"
        print(f"   {status_icon} {name}")
    
    print()
    if healthy_count == total_count:
        print("🎉 All services are now healthy!")
        print("🌐 Open http://localhost:3000 to access the FISO platform")
    else:
        print("⚠️ Some services still need attention")
        print("💡 Try running: python scripts/status_dashboard.py --continuous")
    
    print()
    print("🚀 Next Steps:")
    print("   • Open http://localhost:3000 for the React frontend")
    print("   • Test API at http://localhost:5000/health")
    print("   • Monitor real-time at http://localhost:5001/health")
    print("   • Run full tests: python tests/integration_tests.py")

if __name__ == '__main__':
    main()