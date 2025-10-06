#!/usr/bin/env python3
"""
FISO Enterprise Intelligence Platform - System Status Dashboard
Real-time system status monitoring and overview
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style, Back
import threading
import os

# Initialize colorama for Windows color support
init()

class FISOStatusDashboard:
    def __init__(self):
        self.services = {
            'production_api': {
                'name': 'Production API Server',
                'url': 'http://localhost:5000/health',
                'port': 5000,
                'status': 'unknown'
            },
            'realtime_server': {
                'name': 'Real-time WebSocket Server',
                'url': 'http://localhost:5001/health',
                'port': 5001,
                'status': 'unknown'
            },
            'frontend': {
                'name': 'React Frontend',
                'url': 'http://localhost:3000',
                'port': 3000,
                'status': 'unknown'
            }
        }
        
        self.api_endpoints = {
            'pricing_data': 'http://localhost:5000/api/pricing-data',
            'optimization': 'http://localhost:5000/api/optimization-recommendations',
            'ai_prediction': 'http://localhost:5000/api/ai/predict-costs',
            'natural_language': 'http://localhost:5000/api/ai/natural-query',
            'reports_list': 'http://localhost:5001/api/reports/list'
        }
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def check_service_health(self, service_key):
        """Check health of a specific service"""
        service = self.services[service_key]
        try:
            response = requests.get(service['url'], timeout=5)
            if response.status_code == 200:
                service['status'] = 'healthy'
                if service_key in ['production_api', 'realtime_server']:
                    service['details'] = response.json()
                else:
                    service['details'] = {'status': 'responding'}
            else:
                service['status'] = 'error'
                service['details'] = {'error': f'HTTP {response.status_code}'}
        except requests.exceptions.ConnectionError:
            service['status'] = 'offline'
            service['details'] = {'error': 'Connection refused'}
        except requests.exceptions.Timeout:
            service['status'] = 'timeout'
            service['details'] = {'error': 'Request timeout'}
        except Exception as e:
            service['status'] = 'error'
            service['details'] = {'error': str(e)}
    
    def check_api_endpoints(self):
        """Check API endpoint functionality"""
        results = {}
        
        for endpoint_name, url in self.api_endpoints.items():
            try:
                if endpoint_name in ['ai_prediction', 'natural_language']:
                    # POST requests
                    payload = {'query': 'test'} if endpoint_name == 'natural_language' else {
                        'provider': 'aws', 'service': 'ec2', 'days': 1
                    }
                    response = requests.post(url, json=payload, timeout=10)
                else:
                    # GET requests
                    response = requests.get(url, timeout=10)
                    
                if response.status_code == 200:
                    results[endpoint_name] = {
                        'status': 'healthy',
                        'response_time': f"{response.elapsed.total_seconds()*1000:.1f}ms",
                        'details': 'OK'
                    }
                else:
                    results[endpoint_name] = {
                        'status': 'error',
                        'response_time': f"{response.elapsed.total_seconds()*1000:.1f}ms",
                        'details': f'HTTP {response.status_code}'
                    }
            except Exception as e:
                results[endpoint_name] = {
                    'status': 'error',
                    'response_time': 'N/A',
                    'details': str(e)[:50] + '...' if len(str(e)) > 50 else str(e)
                }
        
        return results
    
    def get_status_color(self, status):
        """Get color for status"""
        colors = {
            'healthy': Fore.GREEN,
            'offline': Fore.RED,
            'error': Fore.RED,
            'timeout': Fore.YELLOW,
            'unknown': Fore.CYAN
        }
        return colors.get(status, Fore.WHITE)
    
    def get_status_symbol(self, status):
        """Get symbol for status"""
        symbols = {
            'healthy': '✅',
            'offline': '❌',
            'error': '⚠️',
            'timeout': '⏱️',
            'unknown': '❓'
        }
        return symbols.get(status, '?')
    
    def display_header(self):
        """Display dashboard header"""
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*80}")
        print(f"🎯 FISO Enterprise Intelligence Platform - System Status Dashboard")
        print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}{Style.RESET_ALL}")
        print()
    
    def display_services_status(self):
        """Display services status"""
        print(f"{Fore.YELLOW}{Style.BRIGHT}🔧 CORE SERVICES STATUS{Style.RESET_ALL}")
        print("-" * 50)
        
        for service_key, service in self.services.items():
            status_color = self.get_status_color(service['status'])
            status_symbol = self.get_status_symbol(service['status'])
            
            print(f"{status_symbol} {status_color}{service['name']:<25}{Style.RESET_ALL} "
                  f"[Port {service['port']}] - {status_color}{service['status'].upper()}{Style.RESET_ALL}")
            
            if 'details' in service and service['status'] == 'healthy':
                if service_key in ['production_api', 'realtime_server']:
                    details = service['details']
                    if 'connected_clients' in details:
                        print(f"   └─ WebSocket Clients: {details.get('connected_clients', 0)}")
                    if 'ai_engine_available' in details:
                        ai_status = "✅ Available" if details['ai_engine_available'] else "❌ Unavailable"
                        print(f"   └─ AI Engine: {ai_status}")
            elif 'details' in service and service['status'] != 'healthy':
                error = service['details'].get('error', 'Unknown error')
                print(f"   └─ {Fore.RED}Error: {error}{Style.RESET_ALL}")
        
        print()
    
    def display_api_status(self, api_results):
        """Display API endpoints status"""
        print(f"{Fore.YELLOW}{Style.BRIGHT}🔌 API ENDPOINTS STATUS{Style.RESET_ALL}")
        print("-" * 50)
        
        for endpoint_name, result in api_results.items():
            status_color = self.get_status_color(result['status'])
            status_symbol = self.get_status_symbol(result['status'])
            
            endpoint_display = endpoint_name.replace('_', ' ').title()
            print(f"{status_symbol} {status_color}{endpoint_display:<25}{Style.RESET_ALL} "
                  f"({result['response_time']}) - {status_color}{result['status'].upper()}{Style.RESET_ALL}")
            
            if result['status'] != 'healthy':
                print(f"   └─ {Fore.RED}{result['details']}{Style.RESET_ALL}")
        
        print()
    
    def display_system_info(self):
        """Display system information"""
        print(f"{Fore.YELLOW}{Style.BRIGHT}📋 SYSTEM INFORMATION{Style.RESET_ALL}")
        print("-" * 50)
        
        # Count healthy services
        healthy_services = sum(1 for s in self.services.values() if s['status'] == 'healthy')
        total_services = len(self.services)
        
        health_percentage = (healthy_services / total_services) * 100
        health_color = Fore.GREEN if health_percentage == 100 else Fore.YELLOW if health_percentage > 50 else Fore.RED
        
        print(f"📊 Overall Health: {health_color}{health_percentage:.0f}% ({healthy_services}/{total_services} services){Style.RESET_ALL}")
        print(f"🌐 Frontend URL: http://localhost:3000")
        print(f"🔧 Production API: http://localhost:5000")
        print(f"⚡ Real-time Server: http://localhost:5001")
        print(f"📈 Health Monitor: http://localhost:5000/health")
        print()
    
    def display_quick_actions(self):
        """Display quick action commands"""
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚡ QUICK ACTIONS{Style.RESET_ALL}")
        print("-" * 50)
        print("🔍 Health Check:     python tests/health_checks.py --environment local")
        print("🧪 Integration Test: python tests/integration_tests.py")
        print("📊 Load Test:        k6 run tests/performance/load_test.js")
        print("🚀 Deploy Local:     python scripts/deploy.py local")
        print("⏹️  Stop All:         Ctrl+C in each terminal")
        print()
    
    def run_single_check(self):
        """Run a single status check"""
        self.clear_screen()
        
        # Check all services
        threads = []
        for service_key in self.services.keys():
            thread = threading.Thread(target=self.check_service_health, args=(service_key,))
            threads.append(thread)
            thread.start()
        
        # Wait for all checks to complete
        for thread in threads:
            thread.join()
        
        # Check API endpoints
        api_results = self.check_api_endpoints()
        
        # Display results
        self.display_header()
        self.display_services_status()
        self.display_api_status(api_results)
        self.display_system_info()
        self.display_quick_actions()
        
        return api_results
    
    def run_continuous_monitoring(self, interval=30):
        """Run continuous monitoring"""
        print(f"{Fore.GREEN}🔄 Starting continuous monitoring (refresh every {interval} seconds)...")
        print("Press Ctrl+C to stop{Style.RESET_ALL}")
        print()
        
        try:
            while True:
                self.run_single_check()
                
                # Show countdown
                for remaining in range(interval, 0, -1):
                    print(f"\r{Fore.CYAN}⏳ Next refresh in {remaining} seconds...{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(1)
                print("\r" + " " * 50 + "\r", end='')  # Clear countdown line
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Monitoring stopped by user{Style.RESET_ALL}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FISO System Status Dashboard')
    parser.add_argument('--continuous', '-c', action='store_true', 
                       help='Run continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Refresh interval for continuous monitoring (seconds)')
    
    args = parser.parse_args()
    
    dashboard = FISOStatusDashboard()
    
    if args.continuous:
        dashboard.run_continuous_monitoring(args.interval)
    else:
        dashboard.run_single_check()
        print(f"{Fore.CYAN}💡 Tip: Use --continuous for real-time monitoring{Style.RESET_ALL}")

if __name__ == '__main__':
    main()