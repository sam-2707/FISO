#!/usr/bin/env python3
"""
FISO Enterprise Intelligence Platform - Health Checks
Comprehensive health monitoring for production deployment
"""

import asyncio
import aiohttp
import argparse
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self, environment: str = 'production'):
        self.environment = environment
        self.base_urls = self._get_base_urls()
        self.session = None
        self.results = []
        
    def _get_base_urls(self) -> Dict[str, str]:
        """Get base URLs based on environment"""
        urls = {
            'local': {
                'production': 'http://localhost:5000',
                'realtime': 'http://localhost:5001'
            },
            'staging': {
                'production': 'https://staging-api.fiso.enterprise.com',
                'realtime': 'https://staging-api.fiso.enterprise.com:5001'
            },
            'production': {
                'production': 'https://api.fiso.enterprise.com',
                'realtime': 'https://api.fiso.enterprise.com:5001'
            }
        }
        return urls.get(self.environment, urls['local'])

    async def check_endpoint(self, service: str, endpoint: str, 
                           method: str = 'GET', 
                           payload: Optional[Dict] = None,
                           expected_status: int = 200,
                           timeout: int = 30) -> Tuple[bool, Dict]:
        """Check a single endpoint"""
        url = f"{self.base_urls[service]}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == 'POST':
                async with self.session.post(
                    url, 
                    json=payload, 
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    response_data = await response.text()
                    status_code = response.status
            else:
                async with self.session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    response_data = await response.text()
                    status_code = response.status
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Try to parse JSON response
            try:
                json_data = json.loads(response_data)
            except json.JSONDecodeError:
                json_data = None
            
            success = status_code == expected_status
            
            result = {
                'service': service,
                'endpoint': endpoint,
                'method': method,
                'url': url,
                'status_code': status_code,
                'expected_status': expected_status,
                'response_time_ms': round(response_time, 2),
                'success': success,
                'response_data': json_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return success, result
            
        except asyncio.TimeoutError:
            result = {
                'service': service,
                'endpoint': endpoint,
                'method': method,
                'url': url,
                'error': 'Timeout',
                'success': False,
                'response_time_ms': timeout * 1000,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            return False, result
            
        except Exception as e:
            result = {
                'service': service,
                'endpoint': endpoint,
                'method': method,
                'url': url,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            return False, result

    async def run_health_checks(self) -> Dict:
        """Run comprehensive health checks"""
        logger.info(f"🏥 Starting health checks for {self.environment} environment")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Define health check scenarios
            checks = [
                # Basic health checks
                {
                    'name': 'Production Server Health',
                    'service': 'production',
                    'endpoint': '/health',
                    'critical': True
                },
                {
                    'name': 'Real-time Server Health',
                    'service': 'realtime',
                    'endpoint': '/health',
                    'critical': True
                },
                
                # API functionality checks
                {
                    'name': 'Pricing Data API',
                    'service': 'production',
                    'endpoint': '/api/pricing-data',
                    'critical': True
                },
                {
                    'name': 'Optimization Recommendations',
                    'service': 'production',
                    'endpoint': '/api/optimization-recommendations',
                    'critical': True
                },
                
                # AI functionality checks
                {
                    'name': 'AI Cost Prediction',
                    'service': 'production',
                    'endpoint': '/api/ai/predict-costs',
                    'method': 'POST',
                    'payload': {
                        'provider': 'aws',
                        'service': 'ec2',
                        'days': 7
                    },
                    'critical': False
                },
                {
                    'name': 'Natural Language Query',
                    'service': 'production',
                    'endpoint': '/api/ai/natural-query',
                    'method': 'POST',
                    'payload': {
                        'query': 'What are my current costs?'
                    },
                    'critical': False
                },
                {
                    'name': 'Anomaly Detection',
                    'service': 'production',
                    'endpoint': '/api/ai/detect-anomalies',
                    'method': 'POST',
                    'payload': {
                        'provider': 'aws',
                        'threshold': 0.8
                    },
                    'critical': False
                },
                
                # Reporting functionality
                {
                    'name': 'Reports List',
                    'service': 'realtime',
                    'endpoint': '/api/reports/list',
                    'critical': False
                },
                
                # Performance checks
                {
                    'name': 'Fast Response Test',
                    'service': 'production',
                    'endpoint': '/health',
                    'timeout': 5,
                    'critical': False
                }
            ]
            
            # Execute all checks concurrently
            tasks = []
            for check in checks:
                task = self.check_endpoint(
                    service=check['service'],
                    endpoint=check['endpoint'],
                    method=check.get('method', 'GET'),
                    payload=check.get('payload'),
                    timeout=check.get('timeout', 30)
                )
                tasks.append((check['name'], check.get('critical', False), task))
            
            # Wait for all checks to complete
            results = []
            critical_failures = 0
            total_failures = 0
            
            for name, is_critical, task in tasks:
                try:
                    success, result = await task
                    result['check_name'] = name
                    result['critical'] = is_critical
                    results.append(result)
                    
                    if success:
                        logger.info(f"✅ {name}: OK ({result.get('response_time_ms', 0):.1f}ms)")
                    else:
                        logger.error(f"❌ {name}: FAILED - {result.get('error', 'Unknown error')}")
                        total_failures += 1
                        if is_critical:
                            critical_failures += 1
                            
                except Exception as e:
                    logger.error(f"❌ {name}: EXCEPTION - {str(e)}")
                    total_failures += 1
                    if is_critical:
                        critical_failures += 1
                    
                    results.append({
                        'check_name': name,
                        'critical': is_critical,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
        
        # Calculate overall health
        total_checks = len(results)
        successful_checks = sum(1 for r in results if r.get('success', False))
        success_rate = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
        
        overall_health = {
            'environment': self.environment,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_status': 'HEALTHY' if critical_failures == 0 else 'UNHEALTHY',
            'success_rate': round(success_rate, 2),
            'total_checks': total_checks,
            'successful_checks': successful_checks,
            'failed_checks': total_failures,
            'critical_failures': critical_failures,
            'checks': results
        }
        
        return overall_health

    async def run_smoke_tests(self) -> Dict:
        """Run smoke tests to verify basic functionality"""
        logger.info(f"🔍 Running smoke tests for {self.environment} environment")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            smoke_tests = [
                {
                    'name': 'Service Discovery',
                    'description': 'Verify all services are reachable',
                    'checks': [
                        ('production', '/health'),
                        ('realtime', '/health')
                    ]
                },
                {
                    'name': 'Data Flow',
                    'description': 'Verify data can be fetched and processed',
                    'checks': [
                        ('production', '/api/pricing-data'),
                        ('production', '/api/optimization-recommendations')
                    ]
                },
                {
                    'name': 'AI Pipeline',
                    'description': 'Verify AI functionality is working',
                    'checks': [
                        ('production', '/api/ai/predict-costs', 'POST', {'provider': 'aws', 'service': 'ec2', 'days': 1})
                    ]
                }
            ]
            
            smoke_results = []
            
            for test_group in smoke_tests:
                group_results = []
                
                for check in test_group['checks']:
                    service = check[0]
                    endpoint = check[1]
                    method = check[2] if len(check) > 2 else 'GET'
                    payload = check[3] if len(check) > 3 else None
                    
                    success, result = await self.check_endpoint(
                        service=service,
                        endpoint=endpoint,
                        method=method,
                        payload=payload,
                        timeout=15
                    )
                    
                    group_results.append(result)
                
                test_success = all(r.get('success', False) for r in group_results)
                
                smoke_results.append({
                    'name': test_group['name'],
                    'description': test_group['description'],
                    'success': test_success,
                    'checks': group_results
                })
                
                status = "✅ PASSED" if test_success else "❌ FAILED"
                logger.info(f"{status} {test_group['name']}: {test_group['description']}")
        
        overall_success = all(test.get('success', False) for test in smoke_results)
        
        return {
            'environment': self.environment,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_status': 'PASSED' if overall_success else 'FAILED',
            'smoke_tests': smoke_results
        }

async def main():
    parser = argparse.ArgumentParser(description='FISO Health Checks and Smoke Tests')
    parser.add_argument('--environment', choices=['local', 'staging', 'production'], 
                       default='production', help='Environment to check')
    parser.add_argument('--type', choices=['health', 'smoke', 'both'], 
                       default='both', help='Type of checks to run')
    parser.add_argument('--output', help='Output file for results (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    checker = HealthChecker(environment=args.environment)
    
    results = {}
    exit_code = 0
    
    try:
        if args.type in ['health', 'both']:
            logger.info("🏥 Running health checks...")
            health_results = await checker.run_health_checks()
            results['health_checks'] = health_results
            
            if health_results['overall_status'] != 'HEALTHY':
                exit_code = 1
                logger.error(f"❌ Health checks failed: {health_results['critical_failures']} critical failures")
            else:
                logger.info(f"✅ Health checks passed: {health_results['success_rate']:.1f}% success rate")
        
        if args.type in ['smoke', 'both']:
            logger.info("🔍 Running smoke tests...")
            smoke_results = await checker.run_smoke_tests()
            results['smoke_tests'] = smoke_results
            
            if smoke_results['overall_status'] != 'PASSED':
                exit_code = 1
                logger.error("❌ Smoke tests failed")
            else:
                logger.info("✅ Smoke tests passed")
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📄 Results saved to {args.output}")
        
        # Summary
        logger.info(f"🎯 Final Status: {'PASSED' if exit_code == 0 else 'FAILED'}")
        
    except Exception as e:
        logger.error(f"💥 Health check execution failed: {str(e)}")
        exit_code = 2
    
    sys.exit(exit_code)

if __name__ == '__main__':
    asyncio.run(main())