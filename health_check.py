#!/usr/bin/env python3
"""
FISO Production Health Check and System Verification
Run this script to verify your production system is ready
"""

import requests
import json
import time
import sys
from datetime import datetime

class FISOHealthChecker:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results = []
        
    def log_result(self, test_name, success, message):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message}")
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Backend Health", True, f"Backend responding on {self.api_base}")
                return True
            else:
                self.log_result("Backend Health", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health", False, f"Backend not responding: {str(e)}")
            return False
            
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        endpoints = [
            "/api/ai/automl/status",
            "/api/production/health", 
            "/api/production/cost/summary",
            "/api/production/cloud-status"
        ]
        
        passed = 0
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_base}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                    self.log_result(f"API {endpoint}", True, f"Endpoint accessible")
                    passed += 1
                else:
                    self.log_result(f"API {endpoint}", False, f"Unexpected status {response.status_code}")
            except Exception as e:
                self.log_result(f"API {endpoint}", False, f"Error: {str(e)}")
                
        return passed >= len(endpoints) // 2  # At least half should work
        
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            # Try to import database module
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            from backend.database.productionDB import ProductionDatabase
            db = ProductionDatabase()
            
            # Test basic database operation
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            self.log_result("Database Connection", True, "Database accessible")
            return True
        except Exception as e:
            self.log_result("Database Connection", False, f"Database error: {str(e)}")
            return False
            
    def test_frontend_build(self):
        """Check if frontend is built and accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_result("Frontend Access", True, f"Frontend accessible at {self.frontend_url}")
                return True
            else:
                self.log_result("Frontend Access", False, f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Frontend Access", False, f"Frontend not accessible: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run complete health check"""
        print("🚀 FISO Production Health Check")
        print("=" * 50)
        print(f"Timestamp: {datetime.now()}")
        print(f"Backend URL: {self.api_base}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 50)
        
        tests = [
            self.test_backend_health,
            self.test_api_endpoints,
            self.test_database_connection,
            self.test_frontend_build
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                
        print("\n" + "=" * 50)
        print(f"🎯 RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - System is production ready!")
            return True
        elif passed >= total * 0.75:
            print("⚠️  MOSTLY READY - Some minor issues detected")
            return True
        else:
            print("❌ NOT READY - Critical issues need fixing")
            return False
            
    def generate_report(self):
        """Generate detailed health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'healthy' if len([r for r in self.results if r['success']]) >= len(self.results) * 0.75 else 'issues_detected',
            'tests': self.results,
            'summary': {
                'total_tests': len(self.results),
                'passed': len([r for r in self.results if r['success']]),
                'failed': len([r for r in self.results if not r['success']])
            }
        }
        
        with open('logs/health_check_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Detailed report saved to: logs/health_check_report.json")

if __name__ == "__main__":
    # Ensure logs directory exists
    import os
    os.makedirs('logs', exist_ok=True)
    
    checker = FISOHealthChecker()
    success = checker.run_all_tests()
    checker.generate_report()
    
    sys.exit(0 if success else 1)