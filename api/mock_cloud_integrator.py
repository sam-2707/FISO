"""
Development/Demo Configuration for Cloud Data Integrator
Use this when cloud SDKs are not available or for testing
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import json
import random

logger = logging.getLogger(__name__)

class MockCloudDataIntegrator:
    """
    Mock cloud data integrator for development and testing
    Provides realistic mock data when cloud SDKs aren't available
    """
    
    def __init__(self, credentials_config: Dict = None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔧 Using Mock Cloud Data Integrator - Development Mode")
        
    async def initialize_connections(self):
        """Mock initialization - always succeeds"""
        self.logger.info("✅ Mock cloud connections initialized")
        
    async def get_cost_data(self, provider: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate realistic mock cost data"""
        days = (end_date - start_date).days
        mock_data = []
        
        services = {
            'aws': ['EC2', 'S3', 'RDS', 'Lambda', 'CloudFront', 'ELB'],
            'azure': ['Virtual Machines', 'Storage', 'SQL Database', 'Functions', 'CDN', 'Load Balancer'],
            'gcp': ['Compute Engine', 'Cloud Storage', 'Cloud SQL', 'Cloud Functions', 'Cloud CDN', 'Load Balancing']
        }
        
        for day in range(days):
            date = start_date + timedelta(days=day)
            for service in services.get(provider, services['aws']):
                cost = round(random.uniform(10, 500), 2)
                mock_data.append({
                    'date': date.isoformat(),
                    'service': service,
                    'cost': cost,
                    'currency': 'USD',
                    'region': 'us-east-1',
                    'provider': provider,
                    'usage_hours': round(random.uniform(1, 24), 2),
                    'mock_data': True
                })
                
        return mock_data
        
    async def get_pricing_data(self, provider: str, service_type: str, region: str = 'us-east-1') -> Dict:
        """Generate mock pricing data"""
        base_prices = {
            'aws': {'EC2': 0.0116, 'S3': 0.023, 'RDS': 0.115},
            'azure': {'Virtual Machines': 0.012, 'Storage': 0.024, 'SQL Database': 0.120},
            'gcp': {'Compute Engine': 0.010, 'Cloud Storage': 0.020, 'Cloud SQL': 0.110}
        }
        
        provider_prices = base_prices.get(provider, base_prices['aws'])
        base_price = provider_prices.get(service_type, 0.050)
        
        return {
            'provider': provider,
            'service': service_type,
            'region': region,
            'price_per_hour': base_price,
            'currency': 'USD',
            'last_updated': datetime.now().isoformat(),
            'mock_data': True
        }
        
    async def get_usage_data(self, provider: str, resource_id: str, metric: str) -> List[Dict]:
        """Generate mock usage/metrics data"""
        mock_usage = []
        now = datetime.now()
        
        for hour in range(24):  # Last 24 hours
            timestamp = now - timedelta(hours=hour)
            value = random.uniform(0, 100) if metric == 'cpu_utilization' else random.uniform(0, 1000)
            
            mock_usage.append({
                'timestamp': timestamp.isoformat(),
                'metric': metric,
                'value': round(value, 2),
                'unit': '%' if 'utilization' in metric else 'GB',
                'resource_id': resource_id,
                'provider': provider,
                'mock_data': True
            })
            
        return mock_usage

def create_development_integrator():
    """Factory function to create appropriate integrator"""
    try:
        # Try to import the real integrator
        from .real_cloud_data_integrator import RealCloudDataIntegrator
        
        # Create minimal credentials for development
        mock_credentials = {
            'aws': type('CloudCredentials', (), {
                'enabled': False,
                'credentials': {}
            })(),
            'azure': type('CloudCredentials', (), {
                'enabled': False,
                'credentials': {}
            })(),
            'gcp': type('CloudCredentials', (), {
                'enabled': False,
                'credentials': {}
            })()
        }
        
        logger.info("🔧 Creating development cloud integrator with disabled real APIs")
        return RealCloudDataIntegrator(mock_credentials)
        
    except ImportError as e:
        logger.warning(f"⚠️  Real cloud integrator not available: {e}")
        logger.info("🔧 Using mock cloud integrator")
        return MockCloudDataIntegrator()

def load_credentials_from_env():
    """Load credentials from environment - with fallback"""
    try:
        from .real_cloud_data_integrator import load_credentials_from_env as real_load_credentials
        return real_load_credentials()
    except ImportError:
        logger.info("🔧 Using mock credentials for development")
        return {}