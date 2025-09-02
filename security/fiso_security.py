# FISO Security & Authentication System
# Enterprise-grade security for multi-cloud orchestration

import jwt
import time
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional
import secrets
import re

class FISOSecurityManager:
    """
    Enterprise security manager for FISO multi-cloud system
    Provides JWT authentication, rate limiting, and request validation
    """
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.rate_limits = {}  # IP-based rate limiting
        self.api_keys = {}     # API key management
        self.blocked_ips = set()
        self.security_events = []
        
    def generate_api_key(self, user_id: str, permissions: list = None) -> Dict[str, Any]:
        """Generate a new API key for a user"""
        api_key = f"fiso_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        key_data = {
            "user_id": user_id,
            "key_hash": key_hash,
            "permissions": permissions or ["read", "orchestrate"],
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "rate_limit": 100  # requests per minute
        }
        
        self.api_keys[key_hash] = key_data
        
        return {
            "api_key": api_key,
            "user_id": user_id,
            "permissions": key_data["permissions"],
            "rate_limit": key_data["rate_limit"]
        }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user data"""
        if not api_key or not api_key.startswith("fiso_"):
            return None
            
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in self.api_keys:
            key_data = self.api_keys[key_hash]
            key_data["last_used"] = datetime.utcnow().isoformat()
            key_data["usage_count"] += 1
            return key_data
        
        return None
    
    def generate_jwt_token(self, user_id: str, permissions: list = None) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            "user_id": user_id,
            "permissions": permissions or ["read"],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            self._log_security_event("token_expired", {"token": token[:20] + "..."})
            return None
        except jwt.InvalidTokenError:
            self._log_security_event("invalid_token", {"token": token[:20] + "..."})
            return None
    
    def check_rate_limit(self, ip_address: str, api_key_data: Dict = None) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        # Get rate limit (from API key or default)
        rate_limit = 60  # default: 60 requests per minute
        if api_key_data:
            rate_limit = api_key_data.get("rate_limit", 100)
        
        # Check IP-based rate limiting
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = {}
        
        ip_limits = self.rate_limits[ip_address]
        
        # Clean old entries
        ip_limits = {k: v for k, v in ip_limits.items() if k >= minute_window - 5}
        self.rate_limits[ip_address] = ip_limits
        
        # Check current minute
        current_requests = ip_limits.get(minute_window, 0)
        
        if current_requests >= rate_limit:
            self._log_security_event("rate_limit_exceeded", {
                "ip": ip_address,
                "requests": current_requests,
                "limit": rate_limit
            })
            return False
        
        # Increment counter
        ip_limits[minute_window] = current_requests + 1
        return True
    
    def validate_request(self, request_data: Dict) -> Dict[str, Any]:
        """Validate and sanitize request data"""
        validation_result = {
            "valid": True,
            "errors": [],
            "sanitized_data": {}
        }
        
        # Check required fields
        if "action" not in request_data:
            validation_result["valid"] = False
            validation_result["errors"].append("Missing required field: action")
        
        # Validate action
        allowed_actions = ["health", "orchestrate", "status", "metrics"]
        action = request_data.get("action", "").lower()
        if action and action not in allowed_actions:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Invalid action: {action}")
        
        # Sanitize provider
        provider = request_data.get("provider", "auto")
        if provider:
            # Only allow alphanumeric and specific values
            if not re.match(r"^(aws|azure|gcp|auto)$", provider.lower()):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Invalid provider: {provider}")
            else:
                validation_result["sanitized_data"]["provider"] = provider.lower()
        
        # Sanitize and validate other fields
        for field in ["region", "instance_type", "timeout"]:
            if field in request_data:
                value = str(request_data[field])
                # Basic sanitization - remove special characters
                sanitized = re.sub(r'[^\w\-\.]', '', value)
                if len(sanitized) <= 50:  # Reasonable length limit
                    validation_result["sanitized_data"][field] = sanitized
        
        return validation_result
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "X-FISO-Version": "1.0.0",
            "X-Rate-Limit-Remaining": "auto",
            "Cache-Control": "no-store, no-cache, must-revalidate"
        }
    
    def authenticate_request(self, headers: Dict[str, str], ip_address: str) -> Dict[str, Any]:
        """
        Comprehensive request authentication
        Returns authentication result with user data
        """
        auth_result = {
            "authenticated": False,
            "user_data": None,
            "auth_method": None,
            "errors": []
        }
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            auth_result["errors"].append("IP address is blocked")
            return auth_result
        
        # Check rate limiting first
        if not self.check_rate_limit(ip_address):
            auth_result["errors"].append("Rate limit exceeded")
            return auth_result
        
        # Try API Key authentication
        api_key = headers.get("X-API-Key") or headers.get("Authorization", "").replace("Bearer ", "")
        if api_key and api_key.startswith("fiso_"):
            user_data = self.validate_api_key(api_key)
            if user_data:
                auth_result["authenticated"] = True
                auth_result["user_data"] = user_data
                auth_result["auth_method"] = "api_key"
                return auth_result
        
        # Try JWT authentication
        jwt_token = headers.get("Authorization", "").replace("Bearer ", "")
        if jwt_token and not jwt_token.startswith("fiso_"):
            payload = self.validate_jwt_token(jwt_token)
            if payload:
                auth_result["authenticated"] = True
                auth_result["user_data"] = payload
                auth_result["auth_method"] = "jwt"
                return auth_result
        
        # For demo purposes, allow unauthenticated requests with basic rate limiting
        if self.check_rate_limit(ip_address):
            auth_result["authenticated"] = True
            auth_result["user_data"] = {
                "user_id": "anonymous",
                "permissions": ["read"],
                "rate_limit": 30
            }
            auth_result["auth_method"] = "anonymous"
        else:
            auth_result["errors"].append("Authentication failed")
        
        return auth_result
    
    def _log_security_event(self, event_type: str, details: Dict):
        """Log security events for monitoring"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "details": details
        }
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and statistics"""
        current_time = time.time()
        hour_ago = current_time - 3600
        
        recent_events = [
            event for event in self.security_events 
            if datetime.fromisoformat(event["timestamp"]).timestamp() > hour_ago
        ]
        
        metrics = {
            "total_events": len(self.security_events),
            "recent_events": len(recent_events),
            "active_api_keys": len(self.api_keys),
            "blocked_ips": len(self.blocked_ips),
            "rate_limit_violations": len([e for e in recent_events if e["type"] == "rate_limit_exceeded"]),
            "authentication_failures": len([e for e in recent_events if e["type"] in ["token_expired", "invalid_token"]]),
            "total_requests": sum(
                sum(limits.values()) for limits in self.rate_limits.values()
            )
        }
        
        return metrics

# Example usage and testing
if __name__ == "__main__":
    # Initialize security manager
    security = FISOSecurityManager()
    
    # Generate demo API key
    demo_key = security.generate_api_key("demo_user", ["read", "orchestrate", "admin"])
    print(f"Demo API Key: {demo_key['api_key']}")
    
    # Generate JWT token
    jwt_token = security.generate_jwt_token("demo_user", ["read", "orchestrate"])
    print(f"JWT Token: {jwt_token}")
    
    # Test authentication
    test_headers = {"X-API-Key": demo_key["api_key"]}
    auth_result = security.authenticate_request(test_headers, "192.168.1.100")
    print(f"Authentication Result: {auth_result}")
    
    # Test request validation
    test_request = {
        "action": "orchestrate",
        "provider": "aws",
        "region": "us-east-1"
    }
    validation_result = security.validate_request(test_request)
    print(f"Validation Result: {validation_result}")
    
    # Get security headers
    headers = security.get_security_headers()
    print(f"Security Headers: {headers}")
    
    # Get security metrics
    metrics = security.get_security_metrics()
    print(f"Security Metrics: {metrics}")
