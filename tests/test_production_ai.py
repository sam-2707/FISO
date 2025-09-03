# FISO Production AI Intelligence - Comprehensive Test Suite
# Demonstrates real market data integration and machine learning capabilities

import requests
import json
import time
from datetime import datetime
import sys
import os

# Add the predictor directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor'))

try:
    from production_ai_engine import ProductionAIEngine, test_production_ai_engine
    print("✅ Successfully imported ProductionAIEngine")
except ImportError as e:
    print(f"❌ Could not import ProductionAIEngine: {e}")
    ProductionAIEngine = None

class FISOProductionAITester:
    """Comprehensive test suite for FISO Production AI Intelligence"""
    
    def __init__(self, base_url="http://localhost:5000", api_key="fiso_zewMp28q5GGPC4wamS5iNM5ao6Q7cplmC4cYRzr8GKY"):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 FISO Production AI Intelligence - Comprehensive Test Suite")
        print("=" * 80)
        
        tests = [
            ("🏥 Health Check", self.test_health_check),
            ("📊 Real-Time Pricing Data", self.test_real_time_pricing),
            ("🤖 ML Cost Prediction", self.test_cost_prediction),
            ("⚡ Optimization Recommendations", self.test_optimization_recommendations),
            ("📈 Market Trend Analysis", self.test_trend_analysis),
            ("🎯 Comprehensive AI Analysis", self.test_comprehensive_analysis),
            ("🔬 AI Engine Direct Test", self.test_ai_engine_direct),
            ("📋 Performance Benchmark", self.test_performance_benchmark)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{test_name}")
            print("-" * 60)
            
            try:
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time
                
                if result.get('success', False):
                    print(f"✅ PASSED ({duration:.2f}s)")
                    results[test_name] = {'status': 'PASSED', 'duration': duration, 'data': result}
                else:
                    print(f"❌ FAILED ({duration:.2f}s): {result.get('error', 'Unknown error')}")
                    results[test_name] = {'status': 'FAILED', 'duration': duration, 'error': result.get('error')}
                    
            except Exception as e:
                print(f"💥 ERROR: {str(e)}")
                results[test_name] = {'status': 'ERROR', 'error': str(e)}
        
        # Print summary
        self.print_test_summary(results)
        return results
    
    def test_health_check(self):
        """Test server health and AI engine status"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            data = response.json()
            
            print(f"   Server Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            
            features = data.get('features', {})
            print(f"   AI Engine: {'✅' if features.get('ai_engine') == 'operational' else '❌'}")
            print(f"   Real-Time Pricing: {'✅' if features.get('real_time_pricing') else '❌'}")
            print(f"   ML Predictions: {'✅' if features.get('ml_predictions') else '❌'}")
            
            endpoints = data.get('endpoints', [])
            print(f"   Available AI Endpoints: {len(endpoints)}")
            
            return {
                'success': response.status_code == 200,
                'ai_engine_operational': features.get('ai_engine') == 'operational',
                'endpoint_count': len(endpoints),
                'data': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_real_time_pricing(self):
        """Test real-time pricing data fetching"""
        try:
            response = self.session.get(f"{self.base_url}/api/ai/real-time-pricing")
            data = response.json()
            
            pricing_data = data.get('pricing_data', {})
            total_points = data.get('total_data_points', 0)
            
            print(f"   Total Data Points: {total_points}")
            print(f"   Providers: {list(pricing_data.keys())}")
            print(f"   Data Source: {data.get('data_source', 'unknown')}")
            
            # Show sample pricing
            for provider, services in pricing_data.items():
                print(f"   {provider.upper()}: {len(services)} services")
                if services:
                    sample = services[0]
                    print(f"     Sample: {sample.get('service')} - ${sample.get('price_per_hour', 0)}/hour")
            
            return {
                'success': response.status_code == 200,
                'providers_count': len(pricing_data),
                'total_data_points': total_points,
                'data': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_cost_prediction(self):
        """Test ML-powered cost prediction"""
        try:
            test_params = {
                'provider': 'aws',
                'lambda_invocations': 5000000,
                'lambda_duration': 2000,
                'lambda_memory': 1024,
                'storage_gb': 500,
                'compute_hours': 200,
                'estimated_monthly_spend': 5000
            }
            
            response = self.session.post(
                f"{self.base_url}/api/ai/cost-prediction",
                json=test_params
            )
            data = response.json()
            
            print(f"   Provider: {data.get('provider', 'unknown')}")
            print(f"   Predicted Cost: ${data.get('predicted_monthly_cost', 0):.2f}/month")
            print(f"   Confidence Score: {data.get('confidence_score', 0) * 100:.1f}%")
            print(f"   Savings Opportunity: {data.get('savings_opportunity_percent', 0):.1f}%")
            
            recommendations = data.get('optimization_recommendations', [])
            print(f"   Recommendations: {len(recommendations)}")
            
            risk_factors = data.get('risk_factors', [])
            print(f"   Risk Factors: {len(risk_factors)}")
            
            return {
                'success': response.status_code == 200,
                'predicted_cost': data.get('predicted_monthly_cost', 0),
                'confidence_score': data.get('confidence_score', 0),
                'has_recommendations': len(recommendations) > 0,
                'data': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_optimization_recommendations(self):
        """Test AI-generated optimization recommendations"""
        try:
            test_params = {
                'lambda_invocations': 10000000,
                'lambda_duration': 3000,
                'lambda_memory': 2048,
                'storage_gb': 1000,
                'compute_hours': 500,
                'estimated_monthly_spend': 10000
            }
            
            response = self.session.post(
                f"{self.base_url}/api/ai/optimization-recommendations",
                json=test_params
            )
            data = response.json()
            
            provider_recs = data.get('provider_recommendations', [])
            cross_provider_recs = data.get('cross_provider_recommendations', [])
            avg_savings = data.get('average_savings_potential', 0)
            priority_actions = data.get('priority_actions', 0)
            
            print(f"   Provider Recommendations: {len(provider_recs)}")
            print(f"   Cross-Provider Recommendations: {len(cross_provider_recs)}")
            print(f"   Average Savings Potential: {avg_savings:.1f}%")
            print(f"   Priority Actions: {priority_actions}")
            
            # Show sample recommendations
            if provider_recs:
                sample_provider = provider_recs[0]
                print(f"   Sample ({sample_provider.get('provider', 'unknown').upper()}):")
                for rec in sample_provider.get('recommendations', [])[:2]:
                    print(f"     • {rec}")
            
            return {
                'success': response.status_code == 200,
                'provider_recommendations_count': len(provider_recs),
                'cross_provider_recommendations_count': len(cross_provider_recs),
                'average_savings_potential': avg_savings,
                'data': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_trend_analysis(self):
        """Test market trend analysis"""
        try:
            response = self.session.get(f"{self.base_url}/api/ai/trend-analysis")
            data = response.json()
            
            market_trends = data.get('market_trends', {})
            provider_trends = data.get('provider_trends', {})
            insights = data.get('market_insights', [])
            recommendations = data.get('recommendations', [])
            
            print(f"   Market Stability Score: {market_trends.get('overall_stability_score', 0):.2f}")
            print(f"   Market Volatility: {market_trends.get('market_volatility', 'unknown')}")
            print(f"   Providers Analyzed: {market_trends.get('providers_analyzed', 0)}")
            print(f"   Analysis Period: {market_trends.get('analysis_period_days', 0)} days")
            
            print(f"   Market Insights: {len(insights)}")
            print(f"   Trend Recommendations: {len(recommendations)}")
            
            # Show provider trends
            for provider, trend in provider_trends.items():
                stability = trend.get('price_stability_score', 0)
                print(f"   {provider.upper()}: Stability {stability:.2f}")
            
            return {
                'success': response.status_code == 200,
                'market_stability_score': market_trends.get('overall_stability_score', 0),
                'providers_analyzed': market_trends.get('providers_analyzed', 0),
                'insights_count': len(insights),
                'data': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_comprehensive_analysis(self):
        """Test comprehensive AI analysis"""
        try:
            test_scenario = {
                'lambda_invocations': 8000000,
                'lambda_duration': 1500,
                'lambda_memory': 768,
                'storage_gb': 750,
                'compute_hours': 300,
                'estimated_monthly_spend': 7500
            }
            
            response = self.session.post(
                f"{self.base_url}/api/ai/comprehensive-analysis",
                json=test_scenario
            )
            data = response.json()
            
            provider_predictions = data.get('provider_predictions', {})
            ai_insights = data.get('ai_insights', {})
            overall_recs = data.get('overall_recommendations', [])
            comparison = data.get('multi_provider_comparison', {})
            
            print(f"   Provider Predictions: {len(provider_predictions)}")
            print(f"   Overall Recommendations: {len(overall_recs)}")
            
            # Show AI insights
            best_provider = ai_insights.get('best_value_provider', 'unknown')
            max_savings = ai_insights.get('maximum_savings_potential', 0)
            avg_confidence = ai_insights.get('average_confidence_score', 0)
            
            print(f"   Best Value Provider: {best_provider.upper()}")
            print(f"   Maximum Savings Potential: {max_savings:.1f}%")
            print(f"   Average Confidence Score: {avg_confidence:.1f}%")
            
            # Show provider costs
            for provider, pred in provider_predictions.items():
                cost = pred.get('predicted_monthly_cost', 0)
                confidence = pred.get('confidence_score', 0)
                print(f"   {provider.upper()}: ${cost:.2f}/month (confidence: {confidence * 100:.1f}%)")
            
            return {
                'success': response.status_code == 200,
                'provider_count': len(provider_predictions),
                'best_value_provider': best_provider,
                'maximum_savings_potential': max_savings,
                'data': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_ai_engine_direct(self):
        """Test AI engine directly (if available)"""
        try:
            if not ProductionAIEngine:
                return {'success': False, 'error': 'ProductionAIEngine not available'}
            
            print("   Testing AI Engine directly...")
            
            # Run the test function
            result = test_production_ai_engine()
            
            print(f"   Analysis Type: {result.get('analysis_type', 'unknown')}")
            print(f"   Pricing Data Points: {result.get('pricing_data_points', 0)}")
            
            provider_predictions = result.get('provider_predictions', {})
            print(f"   Provider Predictions: {len(provider_predictions)}")
            
            ai_insights = result.get('ai_insights', {})
            if ai_insights:
                print(f"   Best Provider: {ai_insights.get('best_value_provider', 'unknown').upper()}")
                print(f"   Max Savings: {ai_insights.get('maximum_savings_potential', 0):.1f}%")
            
            return {
                'success': True,
                'provider_predictions_count': len(provider_predictions),
                'pricing_data_points': result.get('pricing_data_points', 0),
                'data': result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_performance_benchmark(self):
        """Performance benchmark test"""
        try:
            print("   Running performance benchmark...")
            
            # Test multiple rapid requests
            start_time = time.time()
            
            # Health check
            health_response = self.session.get(f"{self.base_url}/health")
            
            # Pricing data
            pricing_response = self.session.get(f"{self.base_url}/api/ai/real-time-pricing")
            
            # Quick prediction
            quick_prediction = self.session.post(
                f"{self.base_url}/api/ai/cost-prediction",
                json={'provider': 'aws', 'lambda_invocations': 1000000}
            )
            
            total_time = time.time() - start_time
            
            success_count = sum([
                1 for resp in [health_response, pricing_response, quick_prediction]
                if resp.status_code == 200
            ])
            
            print(f"   Total Time: {total_time:.2f}s")
            print(f"   Successful Requests: {success_count}/3")
            print(f"   Average Response Time: {total_time/3:.2f}s")
            
            return {
                'success': success_count == 3,
                'total_time': total_time,
                'average_response_time': total_time / 3,
                'successful_requests': success_count
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def print_test_summary(self, results):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🏆 FISO Production AI Intelligence - Test Summary")
        print("=" * 80)
        
        passed = sum(1 for r in results.values() if r.get('status') == 'PASSED')
        failed = sum(1 for r in results.values() if r.get('status') == 'FAILED')
        errors = sum(1 for r in results.values() if r.get('status') == 'ERROR')
        total = len(results)
        
        print(f"📊 Results: {passed} PASSED | {failed} FAILED | {errors} ERRORS | {total} TOTAL")
        print(f"✅ Success Rate: {(passed/total)*100:.1f}%")
        
        total_duration = sum(r.get('duration', 0) for r in results.values() if 'duration' in r)
        print(f"⏱️  Total Test Duration: {total_duration:.2f}s")
        
        print("\n📋 Detailed Results:")
        for test_name, result in results.items():
            status_emoji = {
                'PASSED': '✅',
                'FAILED': '❌', 
                'ERROR': '💥'
            }.get(result.get('status'), '❓')
            
            duration = result.get('duration', 0)
            print(f"   {status_emoji} {test_name} ({duration:.2f}s)")
            
            if result.get('status') != 'PASSED' and 'error' in result:
                print(f"       Error: {result['error']}")
        
        # Feature analysis
        if passed > 0:
            print(f"\n🎯 Key Features Validated:")
            
            # Check specific features
            for test_name, result in results.items():
                if result.get('status') == 'PASSED' and 'data' in result:
                    if 'Health Check' in test_name:
                        ai_operational = result['data'].get('ai_engine_operational', False)
                        print(f"   • AI Engine: {'✅ Operational' if ai_operational else '❌ Unavailable'}")
                    elif 'Real-Time Pricing' in test_name:
                        providers = result['data'].get('providers_count', 0)
                        data_points = result['data'].get('total_data_points', 0)
                        print(f"   • Real-Time Pricing: ✅ {providers} providers, {data_points} data points")
                    elif 'ML Cost Prediction' in test_name:
                        confidence = result['data'].get('confidence_score', 0)
                        print(f"   • ML Predictions: ✅ {confidence*100:.1f}% confidence")
                    elif 'Comprehensive AI Analysis' in test_name:
                        providers = result['data'].get('provider_count', 0)
                        savings = result['data'].get('maximum_savings_potential', 0)
                        print(f"   • Comprehensive Analysis: ✅ {providers} providers, {savings:.1f}% max savings")
        
        print("\n🚀 FISO Production AI Intelligence Test Suite Complete!")
        print("=" * 80)

def main():
    """Main test execution"""
    print("🤖 FISO Production AI Intelligence - Testing Suite")
    print("Starting comprehensive tests...")
    
    # Initialize tester
    tester = FISOProductionAITester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    return results

if __name__ == "__main__":
    main()
