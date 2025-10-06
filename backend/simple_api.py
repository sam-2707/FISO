#!/usr/bin/env python3
"""
Simple Flask Server for FISO Development
Provides basic API endpoints for frontend testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import json

app = Flask(__name__)
CORS(app)

# Sample data generators
def generate_pricing_data():
    """Generate sample pricing data"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "pricing_data": {
            "aws": {
                "ec2": {
                    "t3.micro": {
                        "price": round(random.uniform(0.008, 0.012), 6),
                        "currency": "USD",
                        "unit": "hour",
                        "region": "us-east-1",
                        "trend": random.choice(["up", "down", "stable"])
                    },
                    "t3.small": {
                        "price": round(random.uniform(0.018, 0.022), 6),
                        "currency": "USD", 
                        "unit": "hour",
                        "region": "us-east-1",
                        "trend": random.choice(["up", "down", "stable"])
                    }
                },
                "rds": {
                    "db.t3.micro": {
                        "price": round(random.uniform(0.015, 0.020), 6),
                        "currency": "USD",
                        "unit": "hour",
                        "region": "us-east-1",
                        "trend": random.choice(["up", "down", "stable"])
                    }
                }
            },
            "azure": {
                "vm": {
                    "B1s": {
                        "price": round(random.uniform(0.010, 0.015), 6),
                        "currency": "USD",
                        "unit": "hour",
                        "region": "East US",
                        "trend": random.choice(["up", "down", "stable"])
                    }
                }
            },
            "gcp": {
                "compute": {
                    "e2-micro": {
                        "price": round(random.uniform(0.006, 0.010), 6),
                        "currency": "USD",
                        "unit": "hour",
                        "region": "us-central1",
                        "trend": random.choice(["up", "down", "stable"])
                    }
                }
            }
        }
    }

def generate_recommendations():
    """Generate sample recommendations"""
    recommendations = [
        {
            "id": "rec_001",
            "type": "cost_optimization",
            "priority": "high",
            "provider": "aws",
            "service": "EC2",
            "title": "Resize underutilized instances",
            "description": "Consider downsizing t3.small instances with low CPU utilization to t3.micro",
            "potential_savings": round(random.uniform(50, 200), 2),
            "confidence": round(random.uniform(0.8, 0.95), 2),
            "impact": "medium"
        },
        {
            "id": "rec_002", 
            "type": "reserved_instances",
            "priority": "medium",
            "provider": "aws",
            "service": "RDS",
            "title": "Purchase Reserved Instances",
            "description": "Switch to 1-year reserved instances for consistent database workloads",
            "potential_savings": round(random.uniform(100, 400), 2),
            "confidence": round(random.uniform(0.85, 0.98), 2),
            "impact": "high"
        },
        {
            "id": "rec_003",
            "type": "automation",
            "priority": "low", 
            "provider": "azure",
            "service": "VM",
            "title": "Auto-scaling configuration",
            "description": "Implement auto-scaling to handle variable workloads efficiently",
            "potential_savings": round(random.uniform(30, 100), 2),
            "confidence": round(random.uniform(0.7, 0.85), 2),
            "impact": "medium"
        }
    ]
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations,
        "total_potential_savings": sum(r["potential_savings"] for r in recommendations)
    }

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "FISO API"
    })

@app.route('/api/production/health', methods=['GET'])
def production_health():
    """Production health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": {"status": "healthy", "uptime": "5min"},
            "database": {"status": "healthy", "connections": 3},
            "ml_service": {"status": "healthy", "models": 2}
        }
    })

@app.route('/api/production/pricing', methods=['GET'])
def get_production_pricing():
    """Get production pricing data"""
    return jsonify(generate_pricing_data())

@app.route('/api/production/recommendations', methods=['GET'])
def get_production_recommendations():
    """Get production recommendations"""
    return jsonify(generate_recommendations())

@app.route('/api/production/predict', methods=['POST'])
def predict_costs():
    """Predict costs using ML"""
    data = request.get_json() or {}
    
    # Simulate ML prediction
    base_cost = random.uniform(100, 1000)
    prediction = {
        "status": "success",
        "prediction": {
            "cost": round(base_cost, 2),
            "period": data.get("period_days", 30),
            "confidence": round(random.uniform(0.8, 0.95), 2),
            "model_used": "prophet",
            "trend": random.choice(["increasing", "decreasing", "stable"])
        },
        "factors": [
            {"name": "Historical usage", "impact": 0.4},
            {"name": "Seasonal patterns", "impact": 0.3},
            {"name": "Market trends", "impact": 0.3}
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(prediction)

@app.route('/api/production/anomalies', methods=['GET'])
def detect_anomalies():
    """Detect cost anomalies"""
    provider = request.args.get('provider', 'aws')
    service_type = request.args.get('service_type', 'ec2')
    
    # Simulate anomaly detection
    anomalies = []
    if random.random() > 0.7:  # 30% chance of anomaly
        anomalies.append({
            "id": "anom_001",
            "type": "cost_spike",
            "severity": random.choice(["low", "medium", "high"]),
            "provider": provider,
            "service": service_type,
            "description": f"Unusual cost increase detected in {provider} {service_type}",
            "cost_impact": round(random.uniform(50, 500), 2),
            "timestamp": datetime.now().isoformat(),
            "confidence": round(random.uniform(0.7, 0.9), 2)
        })
    
    return jsonify({
        "status": "success",
        "anomalies": anomalies,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/production/model-performance', methods=['GET'])
def get_model_performance():
    """Get ML model performance metrics"""
    return jsonify({
        "status": "success",
        "models": {
            "prophet": {
                "accuracy": round(random.uniform(0.85, 0.95), 3),
                "last_trained": (datetime.now() - timedelta(hours=2)).isoformat(),
                "data_points": random.randint(1000, 5000)
            },
            "lstm": {
                "accuracy": round(random.uniform(0.80, 0.90), 3),
                "last_trained": (datetime.now() - timedelta(hours=1)).isoformat(),
                "data_points": random.randint(800, 3000)
            }
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/production/cloud-status', methods=['GET'])
def get_cloud_status():
    """Get cloud provider status"""
    providers = {
        "aws": {"status": "active", "last_update": datetime.now().isoformat()},
        "azure": {"status": "active", "last_update": datetime.now().isoformat()},
        "gcp": {"status": "active", "last_update": datetime.now().isoformat()}
    }
    
    return jsonify({
        "status": "success",
        "providers": providers,
        "timestamp": datetime.now().isoformat()
    })

# Legacy endpoints for backward compatibility
@app.route('/api/ai/real-time-pricing', methods=['GET'])
def get_realtime_pricing():
    """Legacy pricing endpoint"""
    return jsonify(generate_pricing_data())

@app.route('/api/ai/live-recommendations', methods=['GET'])
def get_live_recommendations():
    """Legacy recommendations endpoint"""
    return jsonify(generate_recommendations())

if __name__ == '__main__':
    print("🚀 Starting FISO Development API Server...")
    print("📊 Available endpoints:")
    print("   - Health: http://localhost:5000/health")
    print("   - Production Health: http://localhost:5000/api/production/health")
    print("   - Pricing: http://localhost:5000/api/production/pricing")
    print("   - Recommendations: http://localhost:5000/api/production/recommendations")
    print("")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)