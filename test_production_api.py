#!/usr/bin/env python3
"""
FISO Production System Test Script
Tests all API endpoints to ensure everything is working
"""

import requests
import json
import time

def test_endpoint(url, description, method="GET", data=None):
    """Test a single endpoint"""
    try:
        print(f"Testing {description}...")
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    """Test all API endpoints"""
    print("🧪 FISO Production API Test Suite")
    print("="*40)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    tests = [
        (f"{base_url}/", "Root endpoint"),
        (f"{base_url}/api/production/health", "Health check"),
        (f"{base_url}/api/production/cloud-status", "Cloud status"),
        (f"{base_url}/api/production/pricing", "Pricing data"),
        (f"{base_url}/api/production/recommendations", "Recommendations"),
        (f"{base_url}/api/production/anomalies", "Anomaly detection"),
        (f"{base_url}/api/production/model-performance", "Model performance"),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, description in tests:
        if test_endpoint(url, description):
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    # Test POST endpoints
    print("\nTesting POST endpoints...")
    
    predict_data = {
        "provider": "AWS",
        "service_type": "Compute",
        "usage_pattern": "moderate"
    }
    
    if test_endpoint(f"{base_url}/api/production/predict", "Cost prediction", "POST", predict_data):
        passed += 1
    total += 1
    
    train_data = {
        "model_types": ["cost_prediction", "anomaly_detection"]
    }
    
    if test_endpoint(f"{base_url}/api/production/train-models", "Model training", "POST", train_data):
        passed += 1
    total += 1
    
    # Results
    print("\n" + "="*40)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! API is fully functional")
        print("\n🚀 Ready for frontend integration")
        print("Frontend should be available at: http://localhost:3000")
    else:
        print(f"❌ {total - passed} tests failed")
    
    print("="*40)

if __name__ == "__main__":
    main()