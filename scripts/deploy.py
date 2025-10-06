#!/usr/bin/env python3
"""
FISO Enterprise Intelligence Platform - Deployment Manager
Automated deployment orchestration for multiple environments
"""

import asyncio
import argparse
import json
import logging
import os
import subprocess
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    def __init__(self, environment: str, config_path: str = None):
        self.environment = environment
        self.config_path = config_path or f"config/{environment}.yaml"
        self.config = self.load_config()
        self.deployment_id = f"deploy-{int(time.time())}"
        
    def load_config(self) -> Dict:
        """Load environment-specific configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Config file {self.config_path} not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration for environment"""
        configs = {
            'local': {
                'type': 'local',
                'docker': {
                    'enabled': True,
                    'compose_file': 'docker-compose.yml'
                },
                'health_check': {
                    'enabled': True,
                    'endpoints': [
                        'http://localhost:5000/health',
                        'http://localhost:5001/health'
                    ]
                }
            },
            'staging': {
                'type': 'kubernetes',
                'kubernetes': {
                    'namespace': 'fiso-staging',
                    'context': 'staging-cluster',
                    'manifests_path': 'k8s/staging'
                },
                'health_check': {
                    'enabled': True,
                    'endpoints': [
                        'https://staging-api.fiso.enterprise.com/health'
                    ]
                },
                'monitoring': {
                    'enabled': True,
                    'prometheus_url': 'https://prometheus-staging.fiso.enterprise.com'
                }
            },
            'production': {
                'type': 'kubernetes',
                'kubernetes': {
                    'namespace': 'fiso-production',
                    'context': 'production-cluster',
                    'manifests_path': 'k8s/production'
                },
                'health_check': {
                    'enabled': True,
                    'endpoints': [
                        'https://api.fiso.enterprise.com/health'
                    ]
                },
                'monitoring': {
                    'enabled': True,
                    'prometheus_url': 'https://prometheus.fiso.enterprise.com'
                },
                'backup': {
                    'enabled': True,
                    'database_backup': True
                }
            }
        }
        return configs.get(self.environment, configs['local'])

    async def run_command(self, command: str, cwd: str = None, 
                         capture_output: bool = True) -> tuple:
        """Run shell command asynchronously"""
        logger.info(f"🔧 Running: {command}")
        
        try:
            if cwd:
                logger.debug(f"Working directory: {cwd}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            if capture_output:
                stdout_str = stdout.decode() if stdout else ""
                stderr_str = stderr.decode() if stderr else ""
            else:
                stdout_str = ""
                stderr_str = ""
            
            success = process.returncode == 0
            
            if not success:
                logger.error(f"Command failed with code {process.returncode}")
                if stderr_str:
                    logger.error(f"Error output: {stderr_str}")
            
            return success, stdout_str, stderr_str
            
        except Exception as e:
            logger.error(f"Failed to run command: {str(e)}")
            return False, "", str(e)

    async def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        logger.info("🔍 Checking deployment prerequisites...")
        
        prerequisites = []
        
        # Check Docker if needed
        if self.config.get('docker', {}).get('enabled', False):
            success, _, _ = await self.run_command("docker --version")
            prerequisites.append(('Docker', success))
            
            if success:
                success, _, _ = await self.run_command("docker-compose --version")
                prerequisites.append(('Docker Compose', success))
        
        # Check Kubernetes if needed
        if self.config.get('type') == 'kubernetes':
            success, _, _ = await self.run_command("kubectl version --client")
            prerequisites.append(('kubectl', success))
            
            # Check cluster connectivity
            if success:
                context = self.config.get('kubernetes', {}).get('context')
                if context:
                    success, _, _ = await self.run_command(f"kubectl config use-context {context}")
                    prerequisites.append((f'Kubernetes context ({context})', success))
        
        # Check Node.js for frontend build
        success, _, _ = await self.run_command("node --version")
        prerequisites.append(('Node.js', success))
        
        # Check Python
        success, _, _ = await self.run_command("python --version")
        prerequisites.append(('Python', success))
        
        # Report results
        all_passed = True
        for name, passed in prerequisites:
            status = "✅" if passed else "❌"
            logger.info(f"{status} {name}: {'Available' if passed else 'Missing'}")
            if not passed:
                all_passed = False
        
        if not all_passed:
            logger.error("❌ Prerequisites check failed")
        else:
            logger.info("✅ All prerequisites satisfied")
            
        return all_passed

    async def build_application(self) -> bool:
        """Build the application"""
        logger.info("🔨 Building application...")
        
        build_steps = []
        
        # Build frontend
        logger.info("📦 Building frontend...")
        success, stdout, stderr = await self.run_command("npm install", cwd="frontend")
        build_steps.append(('Frontend dependencies', success))
        
        if success:
            success, stdout, stderr = await self.run_command("npm run build", cwd="frontend")
            build_steps.append(('Frontend build', success))
        
        # Install Python dependencies
        logger.info("🐍 Installing Python dependencies...")
        success, stdout, stderr = await self.run_command("pip install -r requirements-production.txt")
        build_steps.append(('Python dependencies', success))
        
        # Build Docker images if needed
        if self.config.get('docker', {}).get('enabled', False):
            logger.info("🐳 Building Docker images...")
            success, stdout, stderr = await self.run_command("docker build -t fiso-enterprise:latest -f Dockerfile.production .")
            build_steps.append(('Docker image build', success))
        
        # Report results
        all_passed = True
        for name, passed in build_steps:
            status = "✅" if passed else "❌"
            logger.info(f"{status} {name}: {'Success' if passed else 'Failed'}")
            if not passed:
                all_passed = False
        
        return all_passed

    async def deploy_local(self) -> bool:
        """Deploy to local environment"""
        logger.info("🏠 Deploying to local environment...")
        
        compose_file = self.config.get('docker', {}).get('compose_file', 'docker-compose.yml')
        
        # Stop existing containers
        logger.info("🛑 Stopping existing containers...")
        await self.run_command(f"docker-compose -f {compose_file} down")
        
        # Start new containers
        logger.info("🚀 Starting containers...")
        success, stdout, stderr = await self.run_command(f"docker-compose -f {compose_file} up -d")
        
        if success:
            logger.info("✅ Local deployment successful")
            
            # Wait for services to be ready
            logger.info("⏳ Waiting for services to be ready...")
            await asyncio.sleep(10)
            
            return True
        else:
            logger.error("❌ Local deployment failed")
            if stderr:
                logger.error(f"Error: {stderr}")
            return False

    async def deploy_kubernetes(self) -> bool:
        """Deploy to Kubernetes environment"""
        logger.info(f"☸️ Deploying to Kubernetes ({self.environment})...")
        
        k8s_config = self.config.get('kubernetes', {})
        namespace = k8s_config.get('namespace', f'fiso-{self.environment}')
        manifests_path = k8s_config.get('manifests_path', f'k8s/{self.environment}')
        
        deployment_steps = []
        
        # Create namespace if it doesn't exist
        logger.info(f"📁 Creating namespace: {namespace}")
        success, _, _ = await self.run_command(f"kubectl create namespace {namespace} --dry-run=client -o yaml | kubectl apply -f -")
        deployment_steps.append(('Namespace creation', success))
        
        # Apply ConfigMaps and Secrets first
        if os.path.exists(f"{manifests_path}/configmap.yaml"):
            logger.info("⚙️ Applying ConfigMaps...")
            success, _, _ = await self.run_command(f"kubectl apply -f {manifests_path}/configmap.yaml -n {namespace}")
            deployment_steps.append(('ConfigMaps', success))
        
        if os.path.exists(f"{manifests_path}/secrets.yaml"):
            logger.info("🔐 Applying Secrets...")
            success, _, _ = await self.run_command(f"kubectl apply -f {manifests_path}/secrets.yaml -n {namespace}")
            deployment_steps.append(('Secrets', success))
        
        # Apply main deployment
        if os.path.exists(f"{manifests_path}/deployment.yaml"):
            logger.info("🚀 Applying Deployment...")
            success, _, _ = await self.run_command(f"kubectl apply -f {manifests_path}/deployment.yaml -n {namespace}")
            deployment_steps.append(('Deployment', success))
            
            if success:
                # Wait for rollout to complete
                logger.info("⏳ Waiting for rollout to complete...")
                success, _, _ = await self.run_command(f"kubectl rollout status deployment/fiso-enterprise -n {namespace} --timeout=300s")
                deployment_steps.append(('Rollout completion', success))
        
        # Apply monitoring if enabled
        if self.config.get('monitoring', {}).get('enabled', False):
            monitoring_path = "k8s/monitoring"
            if os.path.exists(f"{monitoring_path}/monitoring.yaml"):
                logger.info("📊 Applying monitoring configuration...")
                success, _, _ = await self.run_command(f"kubectl apply -f {monitoring_path}/monitoring.yaml -n {namespace}")
                deployment_steps.append(('Monitoring setup', success))
        
        # Report results
        all_passed = True
        for name, passed in deployment_steps:
            status = "✅" if passed else "❌"
            logger.info(f"{status} {name}: {'Success' if passed else 'Failed'}")
            if not passed:
                all_passed = False
        
        if all_passed:
            logger.info("✅ Kubernetes deployment successful")
            
            # Get deployment info
            logger.info("📋 Deployment information:")
            success, stdout, _ = await self.run_command(f"kubectl get pods -n {namespace}")
            if success and stdout:
                logger.info(f"Pods:\n{stdout}")
                
            success, stdout, _ = await self.run_command(f"kubectl get services -n {namespace}")
            if success and stdout:
                logger.info(f"Services:\n{stdout}")
        else:
            logger.error("❌ Kubernetes deployment failed")
        
        return all_passed

    async def run_health_checks(self) -> bool:
        """Run post-deployment health checks"""
        logger.info("🏥 Running health checks...")
        
        if not self.config.get('health_check', {}).get('enabled', False):
            logger.info("Health checks disabled, skipping...")
            return True
        
        endpoints = self.config.get('health_check', {}).get('endpoints', [])
        
        if not endpoints:
            logger.warning("No health check endpoints configured")
            return True
        
        # Wait for services to be ready
        logger.info("⏳ Waiting for services to be ready...")
        await asyncio.sleep(15)
        
        # Run health checks using the health_checks.py script
        success, stdout, stderr = await self.run_command(
            f"python tests/health_checks.py --environment {self.environment} --type health"
        )
        
        if success:
            logger.info("✅ Health checks passed")
            return True
        else:
            logger.error("❌ Health checks failed")
            if stderr:
                logger.error(f"Health check output: {stderr}")
            return False

    async def run_smoke_tests(self) -> bool:
        """Run post-deployment smoke tests"""
        logger.info("🔍 Running smoke tests...")
        
        # Run integration tests
        success, stdout, stderr = await self.run_command("python tests/integration_tests.py")
        
        if success:
            logger.info("✅ Smoke tests passed")
            return True
        else:
            logger.error("❌ Smoke tests failed")
            if stderr:
                logger.error(f"Smoke test output: {stderr}")
            return False

    async def setup_monitoring(self) -> bool:
        """Setup monitoring for the deployment"""
        logger.info("📊 Setting up monitoring...")
        
        if not self.config.get('monitoring', {}).get('enabled', False):
            logger.info("Monitoring disabled, skipping...")
            return True
        
        # Deploy monitoring stack if in Kubernetes
        if self.config.get('type') == 'kubernetes':
            monitoring_steps = []
            
            # Apply monitoring configuration
            monitoring_path = "k8s/monitoring"
            if os.path.exists(f"{monitoring_path}/monitoring.yaml"):
                success, _, _ = await self.run_command(f"kubectl apply -f {monitoring_path}/monitoring.yaml")
                monitoring_steps.append(('Monitoring deployment', success))
            
            # Check if Prometheus is accessible
            prometheus_url = self.config.get('monitoring', {}).get('prometheus_url')
            if prometheus_url:
                # Wait for Prometheus to be ready
                await asyncio.sleep(30)
                
                # This would typically check Prometheus endpoint
                logger.info(f"📈 Monitoring should be available at: {prometheus_url}")
        
        logger.info("✅ Monitoring setup completed")
        return True

    async def backup_if_needed(self) -> bool:
        """Backup data if needed (production only)"""
        if self.environment != 'production':
            return True
            
        backup_config = self.config.get('backup', {})
        if not backup_config.get('enabled', False):
            logger.info("Backup disabled, skipping...")
            return True
            
        logger.info("💾 Creating backup...")
        
        # Create database backup if enabled
        if backup_config.get('database_backup', False):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup/fiso_production_{timestamp}.db"
            
            # Ensure backup directory exists
            os.makedirs("backup", exist_ok=True)
            
            # Copy database file
            success, _, _ = await self.run_command(f"cp fiso_production.db {backup_file}")
            
            if success:
                logger.info(f"✅ Database backup created: {backup_file}")
            else:
                logger.error("❌ Database backup failed")
                return False
        
        logger.info("✅ Backup completed")
        return True

    async def deploy(self) -> bool:
        """Main deployment orchestration"""
        logger.info(f"🚀 Starting deployment to {self.environment} environment")
        logger.info(f"📋 Deployment ID: {self.deployment_id}")
        
        deployment_start = time.time()
        
        try:
            # Step 1: Check prerequisites
            if not await self.check_prerequisites():
                return False
            
            # Step 2: Backup if needed
            if not await self.backup_if_needed():
                return False
            
            # Step 3: Build application
            if not await self.build_application():
                return False
            
            # Step 4: Deploy based on environment type
            deployment_type = self.config.get('type', 'local')
            
            if deployment_type == 'local':
                if not await self.deploy_local():
                    return False
            elif deployment_type == 'kubernetes':
                if not await self.deploy_kubernetes():
                    return False
            else:
                logger.error(f"Unknown deployment type: {deployment_type}")
                return False
            
            # Step 5: Setup monitoring
            if not await self.setup_monitoring():
                logger.warning("Monitoring setup failed, but continuing...")
            
            # Step 6: Run health checks
            if not await self.run_health_checks():
                logger.error("Health checks failed - deployment may be unstable")
                return False
            
            # Step 7: Run smoke tests
            if not await self.run_smoke_tests():
                logger.warning("Smoke tests failed, but deployment succeeded")
            
            # Success!
            deployment_time = time.time() - deployment_start
            logger.info(f"🎉 Deployment to {self.environment} completed successfully!")
            logger.info(f"⏱️ Total deployment time: {deployment_time:.1f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Deployment failed with exception: {str(e)}")
            return False

async def main():
    parser = argparse.ArgumentParser(description='FISO Deployment Manager')
    parser.add_argument('environment', choices=['local', 'staging', 'production'],
                       help='Environment to deploy to')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--skip-tests', action='store_true', 
                       help='Skip health checks and smoke tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create deployment manager
    deployment_manager = DeploymentManager(
        environment=args.environment,
        config_path=args.config
    )
    
    # Override test settings if requested
    if args.skip_tests:
        deployment_manager.config['health_check'] = {'enabled': False}
    
    # Run deployment
    success = await deployment_manager.deploy()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    asyncio.run(main())