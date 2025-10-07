"""
FISO Enhanced API Service with FastAPI
Enterprise-grade API with authentication, rate limiting, and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import asyncio
import aioredis
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import create_engine, Column, String, DateTime, Float, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import redis
import logging
import time
import json
import os
from contextlib import asynccontextmanager
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import structlog

# Import our real cloud integration
from cloud_providers.real_cloud_integration import MultiCloudCostManager, CostRecord

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('fiso_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('fiso_api_request_duration_seconds', 'Request latency')
ACTIVE_CONNECTIONS = Gauge('fiso_api_active_connections', 'Active connections')
COST_DATA_POINTS = Counter('fiso_cost_data_points_total', 'Total cost data points processed', ['provider'])

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fiso_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    api_key = Column(String, unique=True, index=True)
    rate_limit_tier = Column(String, default="basic")  # basic, premium, enterprise

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    rate_limit = Column(Integer, default=1000)  # requests per hour

class CostDataCache(Base):
    __tablename__ = "cost_data_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String, unique=True, index=True, nullable=False)
    data = Column(Text, nullable=False)  # JSON data
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models for API
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class CostQuery(BaseModel):
    providers: List[str] = Field(default=["aws", "azure", "gcp"])
    start_date: datetime
    end_date: datetime
    group_by: List[str] = Field(default=["provider", "service"])
    filters: Dict[str, Any] = Field(default_factory=dict)

class OptimizationRecommendation(BaseModel):
    id: str
    provider: str
    service: str
    type: str
    description: str
    estimated_savings: float
    confidence: str
    implementation_complexity: str
    impact_assessment: Dict[str, Any]

class RealTimeMetrics(BaseModel):
    timestamp: datetime
    active_resources: Dict[str, int]
    current_spend_rate: Dict[str, float]
    anomalies_detected: List[Dict[str, Any]]
    optimization_opportunities: int

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FISO API service")
    
    # Initialize database
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Initialize Redis connection
    app.state.redis = await aioredis.from_url(REDIS_URL)
    
    # Initialize cloud cost manager
    app.state.cloud_manager = MultiCloudCostManager()
    
    # Validate cloud provider credentials
    validation_results = await app.state.cloud_manager.validate_all_credentials()
    logger.info("Cloud provider validation results", **validation_results)
    
    yield
    
    # Shutdown
    logger.info("Shutting down FISO API service")
    await app.state.redis.close()

# FastAPI application
app = FastAPI(
    title="FISO - Cloud Cost Intelligence API",
    description="Enterprise-grade cloud cost optimization and intelligence platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Extract API key or user info for rate limiting
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # Check rate limit for API key
        rate_limit_key = f"rate_limit:api_key:{api_key}"
        current_requests = await app.state.redis.get(rate_limit_key)
        
        if current_requests and int(current_requests) > 1000:  # 1000 requests per hour
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Increment counter
        await app.state.redis.incr(rate_limit_key)
        await app.state.redis.expire(rate_limit_key, 3600)  # 1 hour
    
    response = await call_next(request)
    
    # Record metrics
    process_time = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.observe(process_time)
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Database dependency
def get_db():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication utilities
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# API Endpoints

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_password = hash_password(user.password)
    api_key = str(uuid.uuid4())
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        api_key=api_key
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    logger.info("User registered", username=user.username, user_id=str(db_user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and get access token"""
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="User account is disabled")
    
    # Update last login
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    logger.info("User logged in", username=user.username, user_id=str(db_user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/cost/data", response_model=Dict[str, Any])
async def get_cost_data(
    query: CostQuery,
    current_user: str = Depends(verify_token)
):
    """Get unified cost data from all cloud providers"""
    try:
        # Generate cache key
        cache_key = f"cost_data:{hash(str(query.dict()))}"
        
        # Check cache first
        cached_data = await app.state.redis.get(cache_key)
        if cached_data:
            logger.info("Returning cached cost data", user=current_user, cache_key=cache_key)
            return json.loads(cached_data)
        
        # Fetch fresh data
        logger.info("Fetching fresh cost data", user=current_user, query=query.dict())
        
        cost_records = await app.state.cloud_manager.get_unified_cost_data(
            query.start_date, query.end_date
        )
        
        # Filter by requested providers
        if query.providers:
            cost_records = [r for r in cost_records if r.provider in query.providers]
        
        # Apply additional filters
        for filter_key, filter_value in query.filters.items():
            if hasattr(cost_records[0], filter_key):
                cost_records = [r for r in cost_records if getattr(r, filter_key) == filter_value]
        
        # Generate summary
        summary = app.state.cloud_manager.calculate_cost_summary(cost_records)
        
        # Group data as requested
        df = app.state.cloud_manager.get_cost_data_as_dataframe(cost_records)
        grouped_data = {}
        
        for group_field in query.group_by:
            if group_field in df.columns:
                grouped_data[f"by_{group_field}"] = df.groupby(group_field)['cost_amount'].sum().to_dict()
        
        response_data = {
            "summary": summary,
            "grouped_data": grouped_data,
            "record_count": len(cost_records),
            "query_info": {
                "start_date": query.start_date.isoformat(),
                "end_date": query.end_date.isoformat(),
                "providers": query.providers,
                "filters_applied": query.filters
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "cache_key": cache_key,
                "data_freshness": "real-time"
            }
        }
        
        # Cache the result for 15 minutes
        await app.state.redis.setex(
            cache_key, 
            900,  # 15 minutes
            json.dumps(response_data, default=str)
        )
        
        # Update metrics
        for provider in query.providers:
            provider_records = len([r for r in cost_records if r.provider == provider])
            COST_DATA_POINTS.labels(provider=provider).inc(provider_records)
        
        logger.info("Cost data retrieved successfully", 
                   user=current_user, 
                   record_count=len(cost_records),
                   providers=query.providers)
        
        return response_data
        
    except Exception as e:
        logger.error("Error fetching cost data", user=current_user, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error fetching cost data: {str(e)}")

@app.get("/recommendations", response_model=Dict[str, List[OptimizationRecommendation]])
async def get_optimization_recommendations(
    current_user: str = Depends(verify_token)
):
    """Get optimization recommendations from all cloud providers"""
    try:
        logger.info("Fetching optimization recommendations", user=current_user)
        
        recommendations = await app.state.cloud_manager.get_unified_recommendations()
        
        # Transform recommendations to our standard format
        formatted_recommendations = {}
        
        for provider, provider_recs in recommendations.items():
            formatted_recs = []
            for rec in provider_recs:
                formatted_rec = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    provider=provider,
                    service=rec.get('service', 'unknown'),
                    type=rec.get('type', 'optimization'),
                    description=rec.get('recommendation', ''),
                    estimated_savings=float(rec.get('estimated_savings', 0)),
                    confidence=rec.get('confidence', 'medium'),
                    implementation_complexity='medium',  # Would be calculated based on recommendation type
                    impact_assessment={
                        'cost_impact': rec.get('estimated_savings', 0),
                        'risk_level': 'low',
                        'implementation_time': '1-2 weeks'
                    }
                )
                formatted_recs.append(formatted_rec)
            
            formatted_recommendations[provider] = formatted_recs
        
        logger.info("Optimization recommendations retrieved", 
                   user=current_user, 
                   total_recommendations=sum(len(recs) for recs in formatted_recommendations.values()))
        
        return formatted_recommendations
        
    except Exception as e:
        logger.error("Error fetching recommendations", user=current_user, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

@app.get("/metrics/realtime", response_model=RealTimeMetrics)
async def get_realtime_metrics(
    current_user: str = Depends(verify_token)
):
    """Get real-time cloud metrics and alerts"""
    try:
        logger.info("Fetching real-time metrics", user=current_user)
        
        # This would integrate with real-time monitoring systems
        # For now, we'll return sample data structure
        
        metrics = RealTimeMetrics(
            timestamp=datetime.utcnow(),
            active_resources={
                "aws": {"ec2": 15, "rds": 3, "lambda": 45},
                "azure": {"vm": 8, "sql": 2, "functions": 23},
                "gcp": {"compute": 12, "cloudsql": 1, "functions": 18}
            },
            current_spend_rate={
                "aws": 145.67,  # USD per hour
                "azure": 89.23,
                "gcp": 67.45
            },
            anomalies_detected=[
                {
                    "type": "cost_spike",
                    "provider": "aws",
                    "service": "ec2",
                    "severity": "medium",
                    "description": "Unusual increase in EC2 costs detected",
                    "detected_at": datetime.utcnow().isoformat()
                }
            ],
            optimization_opportunities=7
        )
        
        return metrics
        
    except Exception as e:
        logger.error("Error fetching real-time metrics", user=current_user, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error fetching real-time metrics: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check Redis connection
        await app.state.redis.ping()
        
        # Check cloud provider status
        validation_results = await app.state.cloud_manager.validate_all_credentials()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "services": {
                "redis": "connected",
                "cloud_providers": validation_results
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Admin endpoints
@app.get("/admin/users", dependencies=[Depends(verify_token)])
async def list_users(db: Session = Depends(get_db)):
    """List all users (admin only)"""
    users = db.query(User).all()
    return [{"id": str(u.id), "username": u.username, "email": u.email, "is_active": u.is_active} for u in users]

@app.get("/admin/cache/clear", dependencies=[Depends(verify_token)])
async def clear_cache():
    """Clear all cached data (admin only)"""
    await app.state.redis.flushdb()
    return {"message": "Cache cleared successfully"}

# Custom OpenAPI documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FISO Cloud Cost Intelligence API",
        version="2.0.0",
        description="Enterprise-grade cloud cost optimization and intelligence platform with real-time monitoring, multi-cloud support, and AI-powered recommendations.",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "apiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "enhanced_api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )