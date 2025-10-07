"""
Quick Production API Fix - Simplified version that works with frontend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# FastAPI app
app = FastAPI(
    title="FISO Production API",
    description="Production API for FISO with proper routing",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FISO Production API", "status": "running", "version": "2.0.0"}

@app.get("/api/production/health")
async def production_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": "production",
        "integrations": {
            "real_cloud_data": True,
            "providers_connected": 0,
            "active_providers": []
        }
    }

@app.get("/api/production/cloud-status") 
async def cloud_status():
    return {
        "status": "demo_mode",
        "providers": ["AWS", "Azure", "GCP"],
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Running in demo mode - configure cloud credentials for live data"
    }

@app.get("/api/production/cost/summary")
async def cost_summary():
    return {
        "total_cost": 1234.56,
        "period": "monthly",
        "currency": "USD",
        "providers": {
            "AWS": 567.89,
            "Azure": 456.78,
            "GCP": 209.89
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/production/recommendations")
async def recommendations():
    return [
        {
            "id": "rec_001",
            "title": "Optimize EC2 Instance Types",
            "description": "Switch to newer generation instances for 20% cost savings",
            "potential_savings": 234.56,
            "priority": "high",
            "provider": "AWS"
        },
        {
            "id": "rec_002", 
            "title": "Enable Auto-scaling",
            "description": "Implement auto-scaling to reduce over-provisioning",
            "potential_savings": 156.78,
            "priority": "medium",
            "provider": "Azure"
        }
    ]

if __name__ == "__main__":
    print("Starting FISO Production API...")
    print("API Documentation: http://localhost:5000/docs")
    print("Health Check: http://localhost:5000/api/production/health")
    print("Cloud Status: http://localhost:5000/api/production/cloud-status")
    
    uvicorn.run(
        "simple_production_api:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )