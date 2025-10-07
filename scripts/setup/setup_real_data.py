"""
FISO Real Data Setup Script
Switches from mock data to real cloud provider APIs
"""

import os
import sys
import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDataSetup:
    """Setup script to transition from mock to real data"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.env_template = self.project_root / ".env.template"
        
        self.required_packages = [
            "boto3>=1.26.0",
            "azure-identity>=1.12.0", 
            "azure-mgmt-consumption>=10.0.0",
            "azure-mgmt-costmanagement>=4.0.0",
            "google-cloud-billing>=1.7.0",
            "google-auth>=2.16.0",
            "tenacity>=8.2.0",
            "aiohttp>=3.8.0",
            "pandas>=1.5.0"
        ]
        
        self.credentials_status = {
            'aws': {'configured': False, 'validated': False},
            'azure': {'configured': False, 'validated': False},
            'gcp': {'configured': False, 'validated': False}
        }

    async def run_setup(self):
        """Run the complete setup process"""
        
        print("🚀 FISO Real Data Setup - Eliminating Mock Data")
        print("=" * 60)
        
        try:
            # Step 1: Install dependencies
            await self.install_dependencies()
            
            # Step 2: Setup credentials
            await self.setup_credentials()
            
            # Step 3: Validate connections  
            await self.validate_connections()
            
            # Step 4: Test real data retrieval
            await self.test_real_data()
            
            # Step 5: Generate setup report
            await self.generate_setup_report()
            
            print("\n🎉 FISO Real Data Setup Complete!")
            print("✅ Mock data has been replaced with real cloud APIs")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            print(f"\n❌ Setup failed: {e}")
            return False
        
        return True

    async def install_dependencies(self):
        """Install required packages for real cloud integration"""
        
        print("\n📦 Installing Real Data Dependencies...")
        
        try:
            for package in self.required_packages:
                print(f"   Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"   ✅ {package} installed successfully")
            
            print("✅ All dependencies installed")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e.stderr}")
            raise Exception(f"Dependency installation failed: {package}")

    async def setup_credentials(self):
        """Setup cloud provider credentials"""
        
        print("\n🔐 Setting Up Cloud Provider Credentials...")
        
        # Copy template if .env doesn't exist
        if not self.env_file.exists():
            if self.env_template.exists():
                import shutil
                shutil.copy(self.env_template, self.env_file)
                print(f"📋 Created .env file from template")
            else:
                print("⚠️ No .env template found, creating basic .env file")
                self.create_basic_env_file()
        
        # Check existing credentials
        await self.check_existing_credentials()
        
        # Interactive credential setup
        await self.interactive_credential_setup()

    def create_basic_env_file(self):
        """Create a basic .env file"""
        
        basic_env = """# FISO Real Data Configuration
# Fill in your actual cloud credentials

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1

# Azure  
AZURE_SUBSCRIPTION_ID=
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# GCP
GCP_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
"""
        
        with open(self.env_file, 'w') as f:
            f.write(basic_env)

    async def check_existing_credentials(self):
        """Check which credentials are already configured"""
        
        # Load from .env file
        env_vars = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
        
        # Check AWS
        if env_vars.get('AWS_ACCESS_KEY_ID') and env_vars.get('AWS_SECRET_ACCESS_KEY'):
            self.credentials_status['aws']['configured'] = True
            print("   ✅ AWS credentials found in .env")
        
        # Check Azure
        if env_vars.get('AZURE_SUBSCRIPTION_ID') and env_vars.get('AZURE_TENANT_ID'):
            self.credentials_status['azure']['configured'] = True
            print("   ✅ Azure credentials found in .env")
        
        # Check GCP
        if env_vars.get('GCP_PROJECT_ID'):
            self.credentials_status['gcp']['configured'] = True
            print("   ✅ GCP credentials found in .env")

    async def interactive_credential_setup(self):
        """Interactive setup for missing credentials"""
        
        print("\n🔧 Interactive Credential Setup")
        print("Configure at least one cloud provider to replace mock data:")
        
        configured_any = False
        
        # AWS Setup
        if not self.credentials_status['aws']['configured']:
            setup_aws = input("\n❓ Configure AWS credentials? (y/n): ").lower() == 'y'
            if setup_aws:
                await self.setup_aws_credentials()
                configured_any = True
        
        # Azure Setup
        if not self.credentials_status['azure']['configured']:
            setup_azure = input("\n❓ Configure Azure credentials? (y/n): ").lower() == 'y'
            if setup_azure:
                await self.setup_azure_credentials()
                configured_any = True
        
        # GCP Setup
        if not self.credentials_status['gcp']['configured']:
            setup_gcp = input("\n❓ Configure GCP credentials? (y/n): ").lower() == 'y'
            if setup_gcp:
                await self.setup_gcp_credentials()
                configured_any = True
        
        if not configured_any and not any(cred['configured'] for cred in self.credentials_status.values()):
            print("\n⚠️ No cloud providers configured!")
            print("FISO will run in demo mode without real data.")
            print("Configure credentials later by editing the .env file.")

    async def setup_aws_credentials(self):
        """Setup AWS credentials interactively"""
        
        print("\n🔶 AWS Credential Setup")
        print("Get these from AWS Console > IAM > Users > Security Credentials")
        
        access_key = input("AWS Access Key ID: ").strip()
        secret_key = input("AWS Secret Access Key: ").strip()
        region = input("AWS Region (default: us-east-1): ").strip() or "us-east-1"
        
        if access_key and secret_key:
            # Update .env file
            self.update_env_file({
                'AWS_ACCESS_KEY_ID': access_key,
                'AWS_SECRET_ACCESS_KEY': secret_key,
                'AWS_DEFAULT_REGION': region
            })
            
            self.credentials_status['aws']['configured'] = True
            print("✅ AWS credentials configured")

    async def setup_azure_credentials(self):
        """Setup Azure credentials interactively"""
        
        print("\n🔷 Azure Credential Setup")
        print("Get these from Azure Portal > App Registrations")
        
        subscription_id = input("Azure Subscription ID: ").strip()
        tenant_id = input("Azure Tenant ID: ").strip()
        client_id = input("Azure Client ID: ").strip()
        client_secret = input("Azure Client Secret: ").strip()
        
        if subscription_id and tenant_id:
            self.update_env_file({
                'AZURE_SUBSCRIPTION_ID': subscription_id,
                'AZURE_TENANT_ID': tenant_id,
                'AZURE_CLIENT_ID': client_id,
                'AZURE_CLIENT_SECRET': client_secret
            })
            
            self.credentials_status['azure']['configured'] = True
            print("✅ Azure credentials configured")

    async def setup_gcp_credentials(self):
        """Setup GCP credentials interactively"""
        
        print("\n🟡 GCP Credential Setup")
        print("Get these from GCP Console > IAM & Admin > Service Accounts")
        
        project_id = input("GCP Project ID: ").strip()
        service_account_path = input("Path to service account JSON file: ").strip()
        
        if project_id:
            self.update_env_file({
                'GCP_PROJECT_ID': project_id,
                'GOOGLE_APPLICATION_CREDENTIALS': service_account_path
            })
            
            self.credentials_status['gcp']['configured'] = True
            print("✅ GCP credentials configured")

    def update_env_file(self, updates: Dict[str, str]):
        """Update the .env file with new values"""
        
        # Read existing content
        existing = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing[key] = value
        
        # Update with new values
        existing.update(updates)
        
        # Write back to file
        with open(self.env_file, 'w') as f:
            f.write("# FISO Real Data Configuration\n")
            f.write(f"# Updated: {datetime.utcnow().isoformat()}\n\n")
            
            for key, value in existing.items():
                f.write(f"{key}={value}\n")

    async def validate_connections(self):
        """Validate cloud provider connections"""
        
        print("\n🔍 Validating Cloud Provider Connections...")
        
        # Load environment variables
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if value:  # Only set non-empty values
                            os.environ[key] = value
        
        # Import and test the integrator
        try:
            sys.path.append(str(self.project_root))
            from api.real_cloud_data_integrator import RealCloudDataIntegrator, load_credentials_from_env
            
            credentials = load_credentials_from_env()
            
            if not credentials:
                print("⚠️ No valid credentials found")
                return
            
            integrator = RealCloudDataIntegrator(credentials)
            await integrator.initialize_connections()
            
            # Mark validated providers
            for provider in credentials.keys():
                if credentials[provider].enabled:
                    self.credentials_status[provider]['validated'] = True
                    print(f"   ✅ {provider.upper()} connection validated")
            
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            print(f"   ❌ Connection validation failed: {e}")

    async def test_real_data(self):
        """Test real data retrieval"""
        
        print("\n📊 Testing Real Data Retrieval...")
        
        try:
            # Import the integrator
            from api.real_cloud_data_integrator import RealCloudDataIntegrator, load_credentials_from_env
            
            credentials = load_credentials_from_env()
            
            if not credentials:
                print("   ⚠️ No credentials available for testing")
                return
            
            integrator = RealCloudDataIntegrator(credentials)
            await integrator.initialize_connections()
            
            # Test data retrieval for each provider
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            total_records = 0
            
            for provider in credentials.keys():
                try:
                    cost_data = await integrator.get_real_cost_data(provider, start_date, end_date)
                    total_records += len(cost_data)
                    print(f"   ✅ {provider.upper()}: Retrieved {len(cost_data)} real cost records")
                    
                except Exception as e:
                    print(f"   ⚠️ {provider.upper()}: {e}")
            
            print(f"\n📈 Total real data records retrieved: {total_records}")
            
            if total_records > 0:
                print("🎉 SUCCESS: Mock data successfully replaced with real cloud data!")
            else:
                print("⚠️ No data retrieved - check credentials and billing permissions")
            
        except Exception as e:
            logger.error(f"Real data test failed: {e}")
            print(f"   ❌ Real data test failed: {e}")

    async def generate_setup_report(self):
        """Generate a setup completion report"""
        
        print("\n📋 FISO Real Data Setup Report")
        print("=" * 50)
        
        report = {
            "setup_completed": datetime.utcnow().isoformat(),
            "providers_configured": [],
            "providers_validated": [],
            "mock_data_eliminated": False,
            "production_ready": False
        }
        
        for provider, status in self.credentials_status.items():
            if status['configured']:
                report['providers_configured'].append(provider)
            if status['validated']:
                report['providers_validated'].append(provider)
        
        report['mock_data_eliminated'] = len(report['providers_validated']) > 0
        report['production_ready'] = len(report['providers_validated']) >= 1
        
        # Print report
        print(f"Configured Providers: {', '.join(report['providers_configured']) or 'None'}")
        print(f"Validated Providers: {', '.join(report['providers_validated']) or 'None'}")
        print(f"Mock Data Eliminated: {'✅ Yes' if report['mock_data_eliminated'] else '❌ No'}")
        print(f"Production Ready: {'✅ Yes' if report['production_ready'] else '❌ No'}")
        
        # Save report
        report_file = self.project_root / "setup_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        # Next steps
        print("\n🚀 Next Steps:")
        if report['production_ready']:
            print("1. Run: python real_api_production.py")
            print("2. Visit: http://localhost:8000/docs")
            print("3. Test: http://localhost:8000/cost/summary")
        else:
            print("1. Configure cloud provider credentials in .env file")
            print("2. Re-run this setup script")
            print("3. Check setup_report.json for details")

# CLI Interface
async def main():
    """Main CLI interface"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
FISO Real Data Setup Script

Usage:
  python setup_real_data.py [options]

Options:
  --help     Show this help message
  --validate Test existing credentials only
  --report   Show current setup status

Description:
  This script replaces FISO's mock data with real cloud provider APIs.
  It will guide you through:
  - Installing required dependencies
  - Configuring cloud credentials
  - Validating connections
  - Testing real data retrieval

Requirements:
  - AWS: IAM user with Cost Explorer permissions
  - Azure: App registration with Cost Management permissions  
  - GCP: Service account with Cloud Billing permissions
        """)
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        setup = RealDataSetup()
        await setup.validate_connections()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        setup = RealDataSetup()
        await setup.generate_setup_report()
        return
    
    # Run full setup
    setup = RealDataSetup()
    success = await setup.run_setup()
    
    if success:
        print("\n🎊 FISO is now running with REAL cloud data!")
        print("Mock data has been eliminated.")
    else:
        print("\n❌ Setup incomplete. Check errors above.")

if __name__ == "__main__":
    asyncio.run(main())