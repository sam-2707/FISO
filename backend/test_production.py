#!/usr/bin/env python3
"""
FISO Production Integration Test
Tests the integration between all production components
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

class ProductionIntegrationTest:
    """Test production services integration"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
    def print_result(self, test_name, success, details=""):
        """Print test result with formatting"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_health_endpoint(self):
        """Test production health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/production/health")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                services = data.get('services', {})
                healthy_count = sum(1 for s in services.values() if s.get('status') == 'healthy')
                details += f", Services: {healthy_count}/{len(services)} healthy"
            
            self.print_result("Health Check", success, details)
            return success
        except Exception as e:
            self.print_result("Health Check", False, f"Error: {e}")
            return False
    
    def test_pricing_endpoint(self):
        """Test production pricing endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/production/pricing")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                providers = len(data.get('pricing_data', {}).keys())
                details += f", Providers: {providers}"
            
            self.print_result("Pricing Data", success, details)
            return success
        except Exception as e:
            self.print_result("Pricing Data", False, f"Error: {e}")
            return False
    
    def test_recommendations_endpoint(self):
        """Test production recommendations endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/production/recommendations")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                recs = len(data.get('recommendations', []))
                details += f", Recommendations: {recs}"
            
            self.print_result("ML Recommendations", success, details)
            return success
        except Exception as e:
            self.print_result("ML Recommendations", False, f"Error: {e}")
            return False
    
    def test_prediction_endpoint(self):
        """Test production ML prediction endpoint"""
        try:
            test_data = {
                "provider": "aws",
                "service_type": "ec2",
                "instance_type": "t3.micro",
                "period_days": 30
            }
            
            response = self.session.post(
                f"{self.base_url}/api/production/predict",
                json=test_data
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                model = data.get('model_used', 'unknown')
                confidence = data.get('confidence', 0)
                details += f", Model: {model}, Confidence: {confidence:.2f}"
            
            self.print_result("ML Prediction", success, details)
            return success
        except Exception as e:
            self.print_result("ML Prediction", False, f"Error: {e}")
            return False
    
    def test_anomaly_detection(self):
        """Test production anomaly detection"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/production/anomalies",
                params={"provider": "aws", "service_type": "ec2"}
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                anomalies = len(data.get('anomalies', []))
                details += f", Anomalies detected: {anomalies}"
            
            self.print_result("Anomaly Detection", success, details)
            return success
        except Exception as e:
            self.print_result("Anomaly Detection", False, f"Error: {e}")
            return False
    
    def test_model_performance(self):
        """Test model performance endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/production/model-performance")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                models = len(data.get('models', {}))
                details += f", Models: {models}"
            
            self.print_result("Model Performance", success, details)
            return success
        except Exception as e:
            self.print_result("Model Performance", False, f"Error: {e}")
            return False
    
    def test_cloud_status(self):
        """Test cloud provider status"""
        try:
            response = self.session.get(f"{self.base_url}/api/production/cloud-status")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            details = f"Status: {response.status_code}"
            if success and data:
                providers = data.get('providers', {})
                active = sum(1 for p in providers.values() if p.get('status') == 'active')
                details += f", Active providers: {active}/{len(providers)}"
            
            self.print_result("Cloud Provider Status", success, details)
            return success
        except Exception as e:
            self.print_result("Cloud Provider Status", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 FISO Production Integration Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_endpoint,
            self.test_pricing_endpoint,
            self.test_recommendations_endpoint,
            self.test_prediction_endpoint,
            self.test_anomaly_detection,
            self.test_model_performance,
            self.test_cloud_status,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! Production services are working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Check the logs for details.")
            return False

def main():
    """Main test runner"""
    tester = ProductionIntegrationTest()
    
    print("Waiting for server to be ready...")
    time.sleep(3)
    
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()