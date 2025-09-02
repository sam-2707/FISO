#!/usr/bin/env python3
"""
FISO CLI - Multi-Cloud Command Line Interface
Professional DevOps tooling for FISO multi-cloud orchestration
"""

import argparse
import json
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
import os
from pathlib import Path

class FISOColors:
    """ANSI color codes for beautiful CLI output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class FISOCLI:
    """Professional CLI for FISO Multi-Cloud Operations"""
    
    def __init__(self):
        self.api_base = "http://localhost:5000"
        self.config_file = Path.home() / ".fiso" / "config.json"
        self.api_key = None
        self.load_config()
    
    def load_config(self):
        """Load CLI configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
                    self.api_base = config.get('api_base', self.api_base)
        except Exception as e:
            pass  # Silent fail for missing config
    
    def save_config(self):
        """Save CLI configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                'api_key': self.api_key,
                'api_base': self.api_base,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.error(f"Failed to save config: {e}")
    
    def print_banner(self):
        """Print the FISO CLI banner"""
        banner = f"""
{FISOColors.CYAN}{FISOColors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                        🚀 FISO CLI                           ║
║              Professional Multi-Cloud Orchestration          ║
║                   Enterprise DevOps Toolkit                  ║
╚═══════════════════════════════════════════════════════════════╝
{FISOColors.END}
        """
        print(banner)
    
    def success(self, message: str):
        """Print success message"""
        print(f"{FISOColors.GREEN}✅ {message}{FISOColors.END}")
    
    def error(self, message: str):
        """Print error message"""
        print(f"{FISOColors.RED}❌ {message}{FISOColors.END}")
        
    def warning(self, message: str):
        """Print warning message"""
        print(f"{FISOColors.YELLOW}⚠️  {message}{FISOColors.END}")
    
    def info(self, message: str):
        """Print info message"""
        print(f"{FISOColors.BLUE}ℹ️  {message}{FISOColors.END}")
    
    def header(self, message: str):
        """Print section header"""
        print(f"\n{FISOColors.BOLD}{FISOColors.UNDERLINE}{message}{FISOColors.END}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated API request"""
        if not self.api_key:
            self.error("No API key configured. Use 'fiso auth login' first.")
            sys.exit(1)
        
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                self.error(f"API request failed: {response.status_code} - {response.text}")
                sys.exit(1)
                
        except requests.exceptions.RequestException as e:
            self.error(f"Failed to connect to FISO API: {e}")
            self.info("Make sure the FISO server is running on http://localhost:5000")
            sys.exit(1)
    
    def cmd_auth_login(self, args):
        """Authenticate with FISO API"""
        self.header("🔐 FISO Authentication")
        
        if args.key:
            # Use provided API key
            self.api_key = args.key
        else:
            # Generate new API key
            try:
                response = requests.post(f"{self.api_base}/auth/generate-key", 
                                       json={
                                           "user_id": f"cli_user_{int(time.time())}",
                                           "permissions": ["read", "orchestrate", "admin"]
                                       },
                                       timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    self.api_key = data['data']['api_key']
                else:
                    self.error(f"Failed to generate API key: {response.text}")
                    return
            except Exception as e:
                self.error(f"Failed to connect to FISO API: {e}")
                return
        
        # Test the API key
        try:
            headers = {'X-API-Key': self.api_key}
            test_response = requests.get(f"{self.api_base}/status", headers=headers, timeout=10)
            
            if test_response.status_code == 200:
                self.save_config()
                self.success("Authentication successful!")
                self.info(f"API Key: {self.api_key[:20]}...")
                self.info(f"Config saved to: {self.config_file}")
            else:
                self.error("Invalid API key")
        except Exception as e:
            self.error(f"Failed to test API key: {e}")
    
    def cmd_status(self, args):
        """Get system status"""
        self.header("📊 System Status")
        
        data = self.make_request('GET', '/status')
        
        if data.get('success'):
            status_data = data['data']
            
            # Overall Status
            status = status_data.get('system_status', 'unknown')
            status_color = FISOColors.GREEN if status == 'healthy' else FISOColors.RED
            print(f"System Status: {status_color}{status.upper()}{FISOColors.END}")
            print(f"API Version: {status_data.get('api_version', 'unknown')}")
            print(f"Timestamp: {status_data.get('timestamp', 'unknown')}")
            
            # Multi-Cloud Health
            health = status_data.get('multi_cloud_health', {})
            if health:
                print(f"\n{FISOColors.BOLD}Multi-Cloud Health:{FISOColors.END}")
                print(f"Overall: {health.get('overall_status', 'unknown')}")
                print(f"Healthy Providers: {health.get('healthy_providers', '0/0')}")
                
                providers = health.get('providers', {})
                for name, info in providers.items():
                    status_icon = "🟢" if info.get('status') == 'healthy' else "🔴"
                    response_time = info.get('response_time_ms', 'N/A')
                    print(f"  {status_icon} {name.upper()}: {info.get('status', 'unknown')} ({response_time}ms)")
            
            # Features
            features = status_data.get('features', {})
            if features:
                print(f"\n{FISOColors.BOLD}Features:{FISOColors.END}")
                for feature, enabled in features.items():
                    icon = "✅" if enabled else "❌"
                    print(f"  {icon} {feature.replace('_', ' ').title()}")
        else:
            self.error(f"Failed to get status: {data.get('message', 'Unknown error')}")
    
    def cmd_health(self, args):
        """Check provider health"""
        self.header("🏥 Provider Health Check")
        
        provider = args.provider if args.provider else "auto"
        data = self.make_request('GET', f'/health?provider={provider}')
        
        if data.get('success'):
            health_data = data['data']
            providers = health_data.get('providers', {})
            
            print(f"Overall Status: {health_data.get('overall_status', 'unknown')}")
            print(f"Healthy Providers: {health_data.get('healthy_providers', '0/0')}")
            print(f"Timestamp: {health_data.get('timestamp', 'unknown')}")
            
            print(f"\n{FISOColors.BOLD}Provider Details:{FISOColors.END}")
            for name, info in providers.items():
                status = info.get('status', 'unknown')
                if status == 'healthy':
                    status_display = f"{FISOColors.GREEN}🟢 HEALTHY{FISOColors.END}"
                elif status == 'error':
                    status_display = f"{FISOColors.RED}🔴 ERROR{FISOColors.END}"
                else:
                    status_display = f"{FISOColors.YELLOW}🟡 {status.upper()}{FISOColors.END}"
                
                print(f"\n{FISOColors.BOLD}{name.upper()}{FISOColors.END}")
                print(f"  Status: {status_display}")
                
                if 'response_time_ms' in info:
                    print(f"  Response Time: {info['response_time_ms']}ms")
                
                if 'endpoint' in info:
                    print(f"  Endpoint: {info['endpoint']}")
                
                if 'error' in info:
                    print(f"  Error: {FISOColors.RED}{info['error']}{FISOColors.END}")
                
                if 'response_data' in info:
                    response_data = info['response_data']
                    if isinstance(response_data, dict):
                        if 'service' in response_data:
                            print(f"  Service: {response_data['service']}")
        else:
            self.error(f"Health check failed: {data.get('message', 'Unknown error')}")
    
    def cmd_orchestrate(self, args):
        """Orchestrate multi-cloud request"""
        self.header("🎭 Multi-Cloud Orchestration")
        
        provider = args.provider if args.provider else "auto"
        
        self.info(f"Starting orchestration with provider: {provider}")
        start_time = time.time()
        
        data = self.make_request('POST', '/orchestrate', {"provider": provider})
        
        elapsed = (time.time() - start_time) * 1000
        
        if data.get('success'):
            result = data['data']
            
            self.success(f"Orchestration completed in {elapsed:.2f}ms")
            print(f"Selected Provider: {FISOColors.BOLD}{result.get('selected_provider', 'unknown').upper()}{FISOColors.END}")
            print(f"Response Time: {result.get('response_time_ms', 'N/A')}ms")
            
            if 'response_data' in result:
                print(f"\n{FISOColors.BOLD}Response Data:{FISOColors.END}")
                response_data = result['response_data']
                if isinstance(response_data, dict):
                    for key, value in response_data.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  {response_data}")
        else:
            self.error(f"Orchestration failed: {data.get('message', 'Unknown error')}")
    
    def cmd_metrics(self, args):
        """Get system metrics"""
        self.header("📈 System Metrics")
        
        data = self.make_request('GET', '/metrics')
        
        if data.get('success'):
            metrics = data['data']
            
            # Performance Metrics
            perf = metrics.get('performance', {})
            if perf:
                print(f"{FISOColors.BOLD}Performance Metrics:{FISOColors.END}")
                print(f"  Total Requests: {perf.get('total_requests', 0)}")
                print(f"  Average Response Time: {perf.get('avg_response_time_ms', 'N/A')}ms")
                print(f"  Success Rate: {perf.get('success_rate_percent', 'N/A')}%")
                
                if 'provider_stats' in perf:
                    print(f"\n  {FISOColors.BOLD}Provider Statistics:{FISOColors.END}")
                    for provider, stats in perf['provider_stats'].items():
                        print(f"    {provider.upper()}: {stats.get('avg_response_time', 'N/A')}ms avg")
            
            # Security Metrics
            security = metrics.get('security', {})
            if security:
                print(f"\n{FISOColors.BOLD}Security Metrics:{FISOColors.END}")
                print(f"  Authentication Failures: {security.get('authentication_failures', 0)}")
                print(f"  Rate Limit Violations: {security.get('rate_limit_violations', 0)}")
                print(f"  Blocked IPs: {security.get('blocked_ips', 0)}")
            
            # System Info
            system = metrics.get('system', {})
            if system:
                print(f"\n{FISOColors.BOLD}System Information:{FISOColors.END}")
                print(f"  Uptime: {system.get('uptime', 'N/A')}")
                print(f"  Last Restart: {system.get('last_restart', 'N/A')}")
        else:
            self.error(f"Failed to get metrics: {data.get('message', 'Unknown error')}")
    
    def cmd_config(self, args):
        """Manage CLI configuration"""
        self.header("⚙️  CLI Configuration")
        
        if args.action == 'show':
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                print(f"Configuration File: {self.config_file}")
                print(f"API Base URL: {config.get('api_base', 'Not set')}")
                print(f"API Key: {config.get('api_key', 'Not set')[:20]}..." if config.get('api_key') else "API Key: Not set")
                print(f"Last Updated: {config.get('last_updated', 'Never')}")
            else:
                self.warning("No configuration file found")
                self.info("Use 'fiso auth login' to set up authentication")
        
        elif args.action == 'reset':
            if self.config_file.exists():
                self.config_file.unlink()
                self.success("Configuration reset")
            else:
                self.info("No configuration to reset")
    
    def cmd_watch(self, args):
        """Watch system status in real-time"""
        self.header("👀 Real-time System Monitor")
        
        interval = args.interval
        self.info(f"Monitoring every {interval} seconds (Press Ctrl+C to stop)")
        
        try:
            while True:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                self.print_banner()
                print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Refreshing every {interval}s")
                
                # Get status
                try:
                    data = self.make_request('GET', '/status')
                    if data.get('success'):
                        status_data = data['data']
                        health = status_data.get('multi_cloud_health', {})
                        
                        print(f"\n{FISOColors.BOLD}System Status: {FISOColors.END}", end="")
                        status = status_data.get('system_status', 'unknown')
                        if status == 'healthy':
                            print(f"{FISOColors.GREEN}🟢 HEALTHY{FISOColors.END}")
                        else:
                            print(f"{FISOColors.RED}🔴 {status.upper()}{FISOColors.END}")
                        
                        providers = health.get('providers', {})
                        print(f"\n{FISOColors.BOLD}Provider Status:{FISOColors.END}")
                        
                        for name, info in providers.items():
                            status = info.get('status', 'unknown')
                            response_time = info.get('response_time_ms', 'N/A')
                            
                            if status == 'healthy':
                                icon = "🟢"
                                color = FISOColors.GREEN
                            elif status == 'error':
                                icon = "🔴"
                                color = FISOColors.RED
                            else:
                                icon = "🟡"
                                color = FISOColors.YELLOW
                            
                            print(f"  {icon} {color}{name.upper():<6}{FISOColors.END} | {response_time:>6}ms | {status}")
                        
                        print(f"\n{FISOColors.BOLD}Healthy Providers: {FISOColors.END}{health.get('healthy_providers', '0/0')}")
                
                except Exception as e:
                    self.error(f"Monitor error: {e}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n{FISOColors.GREEN}Monitoring stopped{FISOColors.END}")

def main():
    """Main CLI entry point"""
    cli = FISOCLI()
    
    parser = argparse.ArgumentParser(
        description="FISO CLI - Professional Multi-Cloud Orchestration Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fiso auth login                    # Authenticate with FISO API
  fiso status                        # Get comprehensive system status
  fiso health                        # Check all provider health
  fiso health --provider aws         # Check specific provider
  fiso orchestrate                   # Auto-select best provider
  fiso orchestrate --provider azure  # Use specific provider
  fiso metrics                       # View performance metrics
  fiso watch                         # Real-time monitoring
  fiso config show                   # Show current configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authentication management')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_action', help='Auth actions')
    
    login_parser = auth_subparsers.add_parser('login', help='Login to FISO API')
    login_parser.add_argument('--key', help='Use existing API key')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check provider health')
    health_parser.add_argument('--provider', choices=['aws', 'azure', 'gcp'], help='Specific provider to check')
    
    # Orchestrate command
    orchestrate_parser = subparsers.add_parser('orchestrate', help='Run multi-cloud orchestration')
    orchestrate_parser.add_argument('--provider', choices=['aws', 'azure', 'gcp', 'auto'], default='auto', help='Provider to use')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Get system metrics')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('action', choices=['show', 'reset'], help='Configuration action')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Real-time monitoring')
    watch_parser.add_argument('--interval', type=int, default=5, help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    if not args.command:
        cli.print_banner()
        parser.print_help()
        return
    
    # Route to appropriate command
    if args.command == 'auth' and args.auth_action == 'login':
        cli.cmd_auth_login(args)
    elif args.command == 'status':
        cli.cmd_status(args)
    elif args.command == 'health':
        cli.cmd_health(args)
    elif args.command == 'orchestrate':
        cli.cmd_orchestrate(args)
    elif args.command == 'metrics':
        cli.cmd_metrics(args)
    elif args.command == 'config':
        cli.cmd_config(args)
    elif args.command == 'watch':
        cli.cmd_watch(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
