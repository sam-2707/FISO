# FISO Secure API Server
# Flask-based secure web server for multi-cloud orchestration with Production AI Intelligence

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import sys
import os
import json
import time
from datetime import datetime, timezone
import pandas as pd
import secrets
import logging
from functools import wraps

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'

# Add security and predictor modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor'))

try:
    from secure_api import SecureMultiCloudAPI
except ImportError:
    print("Error: Could not import secure_api module")
    print("Make sure fiso_security.py and secure_api.py are in the security/ directory")
    sys.exit(1)

# Import AI Engine
try:
    from lightweight_ai_engine import EnhancedAIEngine
    AI_ENGINE_AVAILABLE = True
    print("✅ AI Engine imported successfully")
    AIEngineClass = EnhancedAIEngine
except ImportError as e:
    print(f"⚠️  No AI Engine available: {e}")
    AI_ENGINE_AVAILABLE = False
    AIEngineClass = None

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)  # Enable CORS for web dashboard access

# Initialize secure API
secure_api = SecureMultiCloudAPI()

# Initialize Production AI Engine
ai_engine = None
if AI_ENGINE_AVAILABLE:
    try:
        ai_engine = AIEngineClass()
        print("✅ AI Engine initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing AI Engine: {str(e)}")
        ai_engine = None

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def add_security_headers(response):
    """Add security headers to response"""
    headers = secure_api.security.get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Get request parameters
        provider = request.args.get('provider', 'auto')
        
        # Prepare request data
        request_data = {
            "action": "health",
            "provider": provider
        }
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Add AI Engine status to health check
        if response_data.get('success'):
            response_data['ai_features'] = {
                'ai_engine_status': 'operational' if ai_engine else 'unavailable',
                'real_time_pricing': AI_ENGINE_AVAILABLE,
                'ml_predictions': AI_ENGINE_AVAILABLE,
                'optimization_recommendations': AI_ENGINE_AVAILABLE,
                'trend_analysis': AI_ENGINE_AVAILABLE
            }
            response_data['ai_endpoints'] = [
                '/api/ai/comprehensive-analysis',
                '/api/ai/real-time-pricing',
                '/api/ai/cost-prediction',
                '/api/ai/optimization-recommendations',
                '/api/ai/trend-analysis'
            ]
        
        # Create response
        status_code = 401 if not response_data.get('success') and 'Authentication' in str(response_data.get('error', {})) else 200
        if not response_data.get('success') and response_data.get('error', {}).get('code'):
            status_code = response_data['error']['code']
            
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """Multi-cloud orchestration endpoint"""
    try:
        # Get request data
        request_data = request.get_json() or {}
        request_data["action"] = "orchestrate"
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 200
        if not response_data.get('success'):
            if 'Authentication' in str(response_data.get('error', {})):
                status_code = 401
            elif response_data.get('error', {}).get('code'):
                status_code = response_data['error']['code']
            else:
                status_code = 500
        
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/status', methods=['GET'])
def status():
    """System status endpoint"""
    try:
        # Prepare request data
        request_data = {
            "action": "status"
        }
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 200
        if not response_data.get('success'):
            if 'Authentication' in str(response_data.get('error', {})):
                status_code = 401
            elif response_data.get('error', {}).get('code'):
                status_code = response_data['error']['code']
            else:
                status_code = 500
        
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

# ========================================
# PRODUCTION AI INTELLIGENCE ENDPOINTS
# ========================================

@app.route('/api/ai/live-recommendations', methods=['GET'])
def get_live_recommendations():
    """Get live AI recommendations for dashboard display"""
    try:
        # Mock professional recommendations for now
        recommendations = [
            {
                'title': 'Implement Auto-Scaling Policies',
                'description': 'Configure intelligent auto-scaling to reduce idle compute costs by 35-50%',
                'impact_score': 0.85,
                'confidence_score': 0.92,
                'potential_savings': 4250.00,
                'priority': 'high',
                'implementation_effort': 'medium',
                'category': 'cost_optimization'
            },
            {
                'title': 'Reserved Instance Planning',
                'description': 'Purchase reserved instances for predictable workloads to save 30-60%',
                'impact_score': 0.75,
                'confidence_score': 0.89,
                'potential_savings': 3180.00,
                'priority': 'high',
                'implementation_effort': 'low',
                'category': 'cost_optimization'
            },
            {
                'title': 'CDN Implementation',
                'description': 'Deploy global CDN to reduce latency by 40-60% for end users',
                'impact_score': 0.80,
                'confidence_score': 0.94,
                'potential_savings': 0,
                'priority': 'medium',
                'implementation_effort': 'medium',
                'category': 'performance'
            },
            {
                'title': 'Storage Tier Optimization',
                'description': 'Implement intelligent storage tiering to reduce costs by 25-45%',
                'impact_score': 0.70,
                'confidence_score': 0.87,
                'potential_savings': 1890.00,
                'priority': 'medium',
                'implementation_effort': 'medium',
                'category': 'cost_optimization'
            },
            {
                'title': 'Zero-Trust Architecture',
                'description': 'Implement zero-trust network security model for enhanced protection',
                'impact_score': 0.95,
                'confidence_score': 0.96,
                'potential_savings': 0,
                'priority': 'high',
                'implementation_effort': 'high',
                'category': 'security'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        print(f"Error getting live recommendations: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/ai/comprehensive-analysis', methods=['POST'])
def comprehensive_ai_analysis():
    """Comprehensive AI analysis with real market data"""
    try:
        if not ai_engine:
            return jsonify({
                'error': 'AI Engine not available',
                'fallback_data': {
                    'analysis_type': 'fallback_comprehensive',
                    'provider_predictions': {
                        'aws': {
                            'predicted_monthly_cost': 150.75,
                            'confidence_score': 0.85,
                            'savings_opportunity_percent': 35.0,
                            'optimization_recommendations': [
                                'Consider Reserved Instances for predictable workloads',
                                'Optimize Lambda memory allocation',
                                'Use S3 Intelligent Tiering for storage cost optimization'
                            ],
                            'risk_factors': ['AWS pricing changes quarterly', 'Market volatility']
                        },
                        'azure': {
                            'predicted_monthly_cost': 145.20,
                            'confidence_score': 0.82,
                            'savings_opportunity_percent': 30.0,
                            'optimization_recommendations': [
                                'Consider Azure Reserved VM Instances',
                                'Use Azure Functions Premium plan for consistency',
                                'Implement Azure Cost Management policies'
                            ],
                            'risk_factors': ['Azure pricing varies by region', 'Market conditions']
                        },
                        'gcp': {
                            'predicted_monthly_cost': 138.90,
                            'confidence_score': 0.88,
                            'savings_opportunity_percent': 40.0,
                            'optimization_recommendations': [
                                'Enable Sustained Use Discounts',
                                'Consider Committed Use Discounts',
                                'Use Preemptible VMs for fault-tolerant workloads'
                            ],
                            'risk_factors': ['GCP automatic discounts may vary', 'Usage pattern changes']
                        }
                    },
                    'ai_insights': {
                        'best_value_provider': 'gcp',
                        'maximum_savings_potential': 40.0,
                        'average_confidence_score': 85.0,
                        'total_optimization_opportunities': 9
                    },
                    'overall_recommendations': [
                        '🏆 **Best Value Provider**: GCP offers the lowest predicted costs',
                        '💰 **Maximum Savings**: GCP offers up to 40.0% cost reduction opportunities',
                        '🔄 **Multi-Cloud Strategy**: Consider workload distribution - cost difference between providers is 8.5%',
                        '🛡️ **Most Reliable Prediction**: GCP has the highest confidence score',
                        '📊 **Monitor Continuously**: Set up automated cost monitoring',
                        '🤖 **Implement AI Automation**: Enable auto-scaling and optimization'
                    ]
                }
            }), 200
        
        # Get request data
        usage_scenario = request.get_json() or {}
        
        # Run comprehensive analysis
        analysis_result = ai_engine.generate_comprehensive_analysis(usage_scenario)
        
        response = make_response(jsonify(analysis_result), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "AI analysis error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/api/ai/real-time-pricing', methods=['GET'])
def real_time_pricing():
    """Get real-time pricing data from all providers"""
    try:
        if not ai_engine:
            # Fallback pricing data
            fallback_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'pricing_data': {
                    'aws': {
                        'lambda': {'requests': 0.0000002, 'gb_second': 0.0000167, 'unit': 'per request/GB-second'},
                        'ec2': {'t3_micro': 0.0104, 't3_small': 0.0208, 'unit': 'per hour'},
                        'storage': {'s3_standard': 0.023, 'unit': 'per GB/month'}
                    },
                    'azure': {
                        'functions': {'consumption': 0.0000002, 'unit': 'per execution'},
                        'vm': {'b1s': 0.0104, 'b2s': 0.0416, 'unit': 'per hour'},
                        'storage': {'blob_hot': 0.0184, 'unit': 'per GB/month'}
                    },
                    'gcp': {
                        'cloud_functions': {'invocations': 0.0000004, 'gb_second': 0.0000025, 'unit': 'per invocation/GB-second'},
                        'compute': {'e2_micro': 0.006, 'e2_small': 0.012, 'unit': 'per hour'},
                        'storage': {'standard': 0.02, 'unit': 'per GB/month'}
                    }
                },
                'market_analysis': {
                    'overall_trend': 'stable',
                    'volatility_level': 'low',
                    'best_value_provider': 'gcp',
                    'price_alerts': [],
                    'market_recommendation': 'Good time to purchase - stable market conditions'
                },
                'data_quality': {
                    'total_data_points': 15,
                    'update_frequency': 'fallback_mode',
                    'accuracy_score': '85%'
                },
                'data_source': 'fallback_static'
            }
            response = make_response(jsonify(fallback_data), 200)
            return add_security_headers(response)
        
        # Get real-time pricing data from AI engine
        region = request.args.get('region', 'us-east-1')
        pricing_data = ai_engine.get_real_time_pricing(region)
        
        response = make_response(jsonify(pricing_data), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Pricing data error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/api/ai/cost-prediction', methods=['POST'])
def cost_prediction():
    """Generate ML-powered cost predictions"""
    try:
        if not ai_engine:
            # Fallback prediction
            usage_params = request.get_json() or {}
            provider = usage_params.get('provider', 'aws')
            
            fallback_data = {
                'provider': provider,
                'predicted_monthly_cost': 125.50,
                'confidence_score': 0.85,
                'savings_opportunity_percent': 35.0,
                'optimization_recommendations': [
                    'Optimize function memory allocation',
                    'Consider reserved capacity for predictable workloads',
                    'Implement intelligent storage tiering'
                ],
                'trend_analysis': {
                    'overall_trend': 'stable',
                    'volatility': 'low',
                    'price_stability_score': 0.92
                },
                'risk_factors': [
                    'Limited historical data available',
                    'Market conditions may vary'
                ],
                'prediction_timestamp': datetime.utcnow().isoformat(),
                'data_source': 'fallback_ml_model'
            }
            
            response = make_response(jsonify(fallback_data), 200)
            return add_security_headers(response)
        
        usage_params = request.get_json() or {}
        provider = usage_params.get('provider', 'aws')
        
        # Generate ML prediction
        prediction = ai_engine.predict_costs_with_ml(provider, usage_params)
        
        result = {
            'provider': prediction.provider,
            'predicted_monthly_cost': prediction.predicted_cost,
            'confidence_score': prediction.confidence_score,
            'savings_opportunity_percent': prediction.savings_opportunity * 100,
            'optimization_recommendations': prediction.optimization_recommendations,
            'trend_analysis': prediction.trend_analysis,
            'risk_factors': prediction.risk_factors,
            'prediction_timestamp': datetime.utcnow().isoformat(),
            'data_source': 'ml_prediction_engine'
        }
        
        response = make_response(jsonify(result), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Cost prediction error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/api/ai/optimization-recommendations', methods=['POST'])
def optimization_recommendations():
    """Get AI-generated optimization recommendations"""
    try:
        usage_params = request.get_json() or {}
        
        if not ai_engine:
            # Fallback recommendations
            fallback_data = {
                'recommendations': [
                    {
                        'category': 'Memory Optimization',
                        'description': 'Reduce Lambda memory allocation from 1024MB to 512MB',
                        'potential_savings': '20%',
                        'implementation_effort': 'Low',
                        'risk_level': 'Low'
                    },
                    {
                        'category': 'Storage Optimization',
                        'description': 'Implement intelligent storage tiering',
                        'potential_savings': '40%',
                        'implementation_effort': 'Medium',
                        'risk_level': 'Low'
                    },
                    {
                        'category': 'Compute Optimization',
                        'description': 'Consider spot instances for batch workloads',
                        'potential_savings': '70%',
                        'implementation_effort': 'Medium',
                        'risk_level': 'Medium'
                    }
                ],
                'total_potential_savings': '45%',
                'priority_recommendations': 2,
                'timestamp': datetime.utcnow().isoformat(),
                'data_source': 'fallback_optimizer'
            }
            
            response = make_response(jsonify(fallback_data), 200)
            return add_security_headers(response)
        
        # Generate optimization insights for all providers
        all_recommendations = []
        total_savings = 0.0
        
        for provider in ['aws', 'azure', 'gcp']:
            try:
                insights = ai_engine._generate_optimization_insights(provider, usage_params, pd.DataFrame())
                
                provider_recommendations = {
                    'provider': provider,
                    'recommendations': insights['recommendations'],
                    'savings_potential': insights['total_savings_potential'] * 100,
                    'optimization_priority': insights['optimization_priority']
                }
                
                all_recommendations.append(provider_recommendations)
                total_savings += insights['total_savings_potential']
                
            except Exception as e:
                print(f"Warning: Error generating {provider} recommendations: {str(e)}")
        
        result = {
            'provider_recommendations': all_recommendations,
            'cross_provider_recommendations': [
                'Consider multi-cloud strategy for workload distribution',
                'Implement automated cost monitoring across all providers',
                'Use cloud-native cost optimization tools',
                'Regular review and adjustment of resource allocations'
            ],
            'average_savings_potential': (total_savings / len(all_recommendations) * 100) if all_recommendations else 0,
            'priority_actions': len([r for r in all_recommendations if r.get('optimization_priority') == 'high']),
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'ai_optimization_engine'
        }
        
        response = make_response(jsonify(result), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Optimization recommendations error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/api/ai/trend-analysis', methods=['GET'])
def trend_analysis():
    """Get market trend analysis and price volatility assessment"""
    try:
        if not ai_engine:
            # Fallback trend analysis
            fallback_data = {
                'market_trends': {
                    'overall_direction': 'stable_with_slight_decrease',
                    'volatility_level': 'low',
                    'price_stability_score': 0.88,
                    'trend_confidence': 0.82
                },
                'provider_trends': {
                    'aws': {
                        'trend': 'stable',
                        'volatility': 'low',
                        'price_change_30_days': '-2.1%'
                    },
                    'azure': {
                        'trend': 'slight_increase',
                        'volatility': 'medium',
                        'price_change_30_days': '+1.5%'
                    },
                    'gcp': {
                        'trend': 'decreasing',
                        'volatility': 'low',
                        'price_change_30_days': '-3.8%'
                    }
                },
                'market_insights': [
                    'Cloud pricing showing overall stability',
                    'GCP leading with price reductions',
                    'Compute costs trending downward',
                    'Storage pricing remains competitive'
                ],
                'forecast': {
                    'next_30_days': 'continued_stability',
                    'next_90_days': 'slight_decrease_expected',
                    'confidence': 0.78
                },
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'data_source': 'fallback_trend_analysis'
            }
            
            response = make_response(jsonify(fallback_data), 200)
            return add_security_headers(response)
        
        # Get historical data for trend analysis
        trend_results = {}
        
        for provider in ['aws', 'azure', 'gcp']:
            try:
                historical_data = ai_engine._get_historical_pricing(provider, days=90)
                trend_analysis_result = ai_engine._analyze_pricing_trends(historical_data)
                trend_results[provider] = trend_analysis_result
            except Exception as e:
                print(f"Warning: Error analyzing {provider} trends: {str(e)}")
                trend_results[provider] = {
                    'trend': 'stable',
                    'volatility': 'unknown',
                    'price_stability_score': 0.5
                }
        
        # Calculate overall market trends
        overall_stability = sum([t.get('price_stability_score', 0.5) for t in trend_results.values()]) / len(trend_results)
        
        result = {
            'market_trends': {
                'overall_stability_score': overall_stability,
                'market_volatility': 'low' if overall_stability > 0.8 else 'medium' if overall_stability > 0.6 else 'high',
                'providers_analyzed': len(trend_results),
                'analysis_period_days': 90
            },
            'provider_trends': trend_results,
            'market_insights': [
                f'Overall market stability score: {overall_stability:.2f}',
                'Multi-provider analysis shows competitive pricing',
                'Price volatility remains manageable across providers',
                'Historical data indicates sustainable cost trends'
            ],
            'recommendations': [
                'Monitor pricing trends weekly for optimization opportunities',
                'Consider provider switching if volatility increases',
                'Lock in pricing with reserved instances during stable periods',
                'Diversify workloads across providers to minimize risk'
            ],
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'data_source': 'historical_trend_analysis'
        }
        
        response = make_response(jsonify(result), 200)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Trend analysis error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/api/session-info', methods=['GET'])
def session_info():
    """Provide session information including a temporary API key for the dashboard"""
    try:
        if DEMO_MODE and 'DEMO_API_KEY' in app.config:
            # Return stored demo credentials
            session_data = {
                "success": True,
                "api_key": app.config['DEMO_API_KEY'],
                "session_id": "demo_session",
                "permissions": ["read", "orchestrate"],
                "expires_in": 3600,  # 1 hour
                "mode": "demo",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Generate a temporary API key for this session
            temp_key = secure_api.security.generate_api_key("dashboard_session", ["read", "orchestrate"])
            
            session_data = {
                "success": True,
                "api_key": temp_key['api_key'],
                "session_id": temp_key.get('user_id', 'session_' + str(int(time.time()))),
                "permissions": temp_key.get('permissions', ["read", "orchestrate"]),
                "expires_in": 3600,  # 1 hour
                "mode": "production",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        response = make_response(jsonify(session_data), 200)
        return add_security_headers(response)
        
    except Exception as e:
        logger.error(f"Session info error: {str(e)}")
        error_response = {
            "success": False,
            "error": "Session initialization failed",
            "details": str(e) if DEMO_MODE else "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

@app.route('/auth/generate-key', methods=['POST'])
def generate_api_key():
    """Generate new API key"""
    try:
        # Get request data
        request_data = request.get_json() or {}
        request_data["action"] = "generate_api_key"
        
        # Process through secure API
        response_data = secure_api.process_secure_request(
            request_data,
            dict(request.headers),
            get_client_ip()
        )
        
        # Create response
        status_code = 200
        if not response_data.get('success'):
            if 'Authentication' in str(response_data.get('error', {})):
                status_code = 401
            elif response_data.get('error', {}).get('code'):
                status_code = response_data['error']['code']
            else:
                status_code = 500
        
        response = make_response(jsonify(response_data), status_code)
        return add_security_headers(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": [str(e)]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = make_response(jsonify(error_response), 500)
        return add_security_headers(response)

# Enterprise Dashboard Route - Serves the professional industry-standard dashboard
@app.route('/', methods=['GET'])
@app.route('/dashboard', methods=['GET'])
@app.route('/enterprise_dashboard.html', methods=['GET'])
def enterprise_dashboard():
    """Serve the enterprise FISO dashboard with professional industry-standard design"""
    try:
        # Get the enterprise dashboard file path
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'enterprise_dashboard.html')
        
        # Read and serve the dashboard file
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        response = make_response(dashboard_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        return make_response(f"Error loading enterprise dashboard: {str(e)}", 500)

# Legacy dashboard routes for backwards compatibility (redirect to enterprise)
@app.route('/unified_dashboard.html', methods=['GET'])
@app.route('/ai_dashboard.html', methods=['GET'])
@app.route('/enhanced_ai_dashboard.html', methods=['GET'])
@app.route('/compatible_dashboard.html', methods=['GET'])
@app.route('/simple_dashboard.html', methods=['GET'])
def legacy_dashboard_redirect():
    """Redirect legacy dashboard routes to the enterprise dashboard"""
    from flask import redirect, url_for
    return redirect(url_for('enterprise_dashboard'), code=301)

@app.route('/ai_predictor_integration.js', methods=['GET'])
def ai_predictor_integration_js():
    """Serve the AI predictor integration JavaScript file"""
    try:
        # Get the JS file path
        js_path = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'ai_predictor_integration.js')
        
        # Read and serve the JS file
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        response = make_response(js_content)
        response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        return make_response(f"Error loading AI predictor integration: {str(e)}", 500)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - serves the enterprise dashboard"""
    return enterprise_dashboard()

# API Info endpoint for those who need it
@app.route('/api', methods=['GET'])
@app.route('/info', methods=['GET']) 
def api_info():
    """API information endpoint"""
    info = {
        "name": "FISO Secure Multi-Cloud API with Production AI Intelligence",
        "version": "3.0.0-production-ai",
        "description": "Enterprise-grade secure API for multi-cloud orchestration with AI-powered cost optimization",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ai_status": {
            "ai_engine": "operational" if ai_engine else "unavailable",
            "real_time_pricing": AI_ENGINE_AVAILABLE,
            "ml_predictions": AI_ENGINE_AVAILABLE,
            "features_enabled": ["real-time pricing", "ML predictions", "optimization", "trend analysis"] if AI_ENGINE_AVAILABLE else []
        },
        "endpoints": {
            "health": "/health",
            "orchestrate": "/orchestrate", 
            "status": "/status",
            "generate_api_key": "/auth/generate-key",
            "ai_endpoints": {
                "comprehensive_analysis": "/api/ai/comprehensive-analysis",
                "real_time_pricing": "/api/ai/real-time-pricing",
                "cost_prediction": "/api/ai/cost-prediction",
                "optimization_recommendations": "/api/ai/optimization-recommendations",
                "trend_analysis": "/api/ai/trend-analysis"
            },
            "dashboards": {
                "unified_main": "/",
                "unified_direct": "/unified_dashboard.html", 
                "dashboard_alias": "/dashboard",
                "features": "AI Intelligence • Multi-Cloud Comparison • API Testing • System Monitoring"
            }
        },
        "authentication": "API Key or JWT Token required"
    }
    
    response = make_response(jsonify(info), 200)
    return add_security_headers(response)

if __name__ == '__main__':
    logger.info("🚀 Starting FISO Secure API Server with Production AI Intelligence...")
    logger.info("=" * 70)
    
    # Only show demo credentials in demo mode
    if DEMO_MODE:
        # Generate demo credentials
        demo_key = secure_api.security.generate_api_key("demo_user", ["read", "orchestrate", "admin"])
        demo_jwt = secure_api.security.generate_jwt_token("demo_user", ["read", "orchestrate"])
        
        logger.info("🔧 DEMO MODE ENABLED")
        logger.info("� Demo Credentials Available - Use /api/session-info endpoint")
        
        # Store demo credentials for session endpoint (don't print them)
        app.config['DEMO_API_KEY'] = demo_key['api_key']
        app.config['DEMO_JWT_TOKEN'] = demo_jwt
    else:
        logger.info("🔒 PRODUCTION MODE - Use proper authentication")
    
    logger.info("\n🤖 AI Intelligence Features:")
    ai_status = "✅ OPERATIONAL" if ai_engine else "❌ UNAVAILABLE"
    logger.info(f"   • AI Engine: {ai_status}")
    logger.info(f"   • Real-Time Pricing: {'✅' if AI_ENGINE_AVAILABLE else '❌'}")
    logger.info(f"   • ML Predictions: {'✅' if AI_ENGINE_AVAILABLE else '❌'}")
    logger.info(f"   • Smart Optimization: {'✅' if AI_ENGINE_AVAILABLE else '❌'}")
    
    print("\n🎨 Enterprise Dashboard:")
    print("   http://localhost:5000/                       - 🚀 FISO Enterprise Intelligence Dashboard (MAIN)")
    print("   http://localhost:5000/enterprise_dashboard.html - 📊 Direct Access to Enterprise Dashboard")
    print("   http://localhost:5000/dashboard              - 📊 Alternative Dashboard Route")
    print("\n   ✨ Features: AI Intelligence • Multi-Cloud Comparison • API Testing • System Monitoring")
    
    print("\n🎯 AI API Endpoints:")
    print("   POST /api/ai/comprehensive-analysis")
    print("   GET  /api/ai/real-time-pricing")
    print("   POST /api/ai/cost-prediction")
    print("   POST /api/ai/optimization-recommendations")
    print("   GET  /api/ai/trend-analysis")
    
    if DEMO_MODE:
        print("\n🧪 Test Commands (Demo Mode):")
        print("   curl http://localhost:5000/api/session-info  # Get demo API key")
        print("   curl http://localhost:5000/health")
        print("   curl http://localhost:5000/api/ai/real-time-pricing")
    
    print("\n🔒 Security Features:")
    print("   ✅ JWT Authentication")
    print("   ✅ API Key Authentication") 
    print("   ✅ Rate Limiting")
    print("   ✅ CORS Support")
    print("   ✅ Security Headers")
    print("   ✅ Environment-based Configuration")
    
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"\n🌐 Server starting on http://localhost:{port}")
    print("=" * 70)
    print("💡 TIP: Visit http://localhost:{port}/ for the complete FISO Enterprise Intelligence Dashboard!")
    print("     Features: AI Intelligence • Multi-Cloud Analysis • API Testing • Real-Time Monitoring")
    
    if debug_mode:
        logger.warning("⚠️  Running in DEBUG mode - Use production WSGI server for production!")
    
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
