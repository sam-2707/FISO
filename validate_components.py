#!/usr/bin/env python3
"""
FISO Frontend Component Validator
Check if all React components are properly implemented and accessible
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class ComponentValidator:
    def __init__(self):
        self.frontend_path = Path("frontend/src/components")
        self.issues = []
        
    def check_component_exists(self, component_path):
        """Check if component file exists"""
        full_path = self.frontend_path / component_path
        if not full_path.exists():
            self.issues.append(f"❌ Missing component: {component_path}")
            return False
        else:
            print(f"✅ Found component: {component_path}")
            return True
            
    def check_component_exports(self, component_path):
        """Check if component has proper default export"""
        full_path = self.frontend_path / component_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'export default' in content:
                    print(f"✅ {component_path} has default export")
                    return True
                else:
                    self.issues.append(f"⚠️  {component_path} missing default export")
                    return False
        except Exception as e:
            self.issues.append(f"❌ Error reading {component_path}: {e}")
            return False
            
    def validate_ai_components(self):
        """Validate AI-related components"""
        ai_components = [
            "AI/AutoMLIntegration.js",
            "AI/AnomalyDetection.js", 
            "AI/PredictiveAnalytics.js",
            "AI/NaturalLanguageInterface.js"
        ]
        
        print("🤖 Validating AI Components:")
        for component in ai_components:
            exists = self.check_component_exists(component)
            if exists:
                self.check_component_exports(component)
                
    def validate_dashboard_components(self):
        """Validate dashboard-related components"""
        dashboard_components = [
            "CloudDashboard.js",
            "SystemMetrics.js",
            "ExecutiveReporting.js",
            "IntegrationTest.js",
            "RealTimeStatus.js",
            "ConnectionStatus.js",
            "LoadingComponent.js",
            "ErrorBoundary.js"
        ]
        
        print("\n📊 Validating Dashboard Components:")
        for component in dashboard_components:
            exists = self.check_component_exists(component)
            if exists:
                self.check_component_exports(component)
                
    def check_utilities(self):
        """Check utility files"""
        utils_path = Path("frontend/src/utils")
        utils_files = [
            "apiUtils.js"
        ]
        
        print("\n🔧 Validating Utility Files:")
        for util_file in utils_files:
            full_path = utils_path / util_file
            if full_path.exists():
                print(f"✅ Found utility: {util_file}")
            else:
                self.issues.append(f"❌ Missing utility: {util_file}")
                
    def check_package_json(self):
        """Check if package.json has required dependencies"""
        package_path = Path("frontend/package.json")
        if package_path.exists():
            try:
                with open(package_path, 'r') as f:
                    package_data = json.load(f)
                    
                required_deps = [
                    '@mui/material',
                    '@mui/icons-material',
                    'react',
                    'react-dom',
                    'react-router-dom',
                    'recharts'
                ]
                
                dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                
                print("\n📦 Checking Dependencies:")
                missing_deps = []
                for dep in required_deps:
                    if dep in dependencies:
                        print(f"✅ {dep}: {dependencies[dep]}")
                    else:
                        missing_deps.append(dep)
                        print(f"❌ Missing: {dep}")
                        
                if missing_deps:
                    self.issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
                    
            except Exception as e:
                self.issues.append(f"Error reading package.json: {e}")
        else:
            self.issues.append("Missing package.json in frontend directory")
            
    def run_lint_check(self):
        """Run basic syntax checking"""
        print("\n🔍 Running Syntax Check:")
        try:
            os.chdir("frontend")
            result = subprocess.run(
                ["npm", "run", "build", "--dry-run"], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                print("✅ No syntax errors detected")
            else:
                print("⚠️  Build warnings/errors detected:")
                print(result.stdout)
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("⚠️  Build check timed out")
        except Exception as e:
            print(f"⚠️  Could not run build check: {e}")
        finally:
            os.chdir("..")
            
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("🎯 COMPONENT VALIDATION REPORT")
        print("="*60)
        
        if not self.issues:
            print("🎉 ALL COMPONENTS VALIDATED SUCCESSFULLY!")
            print("\n✨ Your FISO dashboard should have:")
            print("   📊 Dashboard Overview (Tab 0)")
            print("   🤖 AI Predictions (Tab 1)")
            print("   💬 Natural Language Interface (Tab 2)")
            print("   ⚠️  Anomaly Detection (Tab 3)")
            print("   🎛️  AutoML Integration (Tab 4)")  
            print("   📈 Executive Reports (Tab 5)")
            print("   🔧 System Metrics (Tab 6)")
            print("   🧪 Integration Test (Tab 7)")
            print("\n🚀 Try clicking on different tabs in your browser!")
            
        else:
            print(f"❌ Found {len(self.issues)} issues:")
            for issue in self.issues:
                print(f"   {issue}")
                
        return len(self.issues) == 0
        
    def run_validation(self):
        """Run complete validation"""
        print("🚀 FISO Frontend Component Validation")
        print("="*50)
        
        self.validate_ai_components()
        self.validate_dashboard_components()
        self.check_utilities()
        self.check_package_json()
        
        return self.generate_report()

if __name__ == "__main__":
    validator = ComponentValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Open browser to http://localhost:3000")
        print("2. Click on different tabs to see all features:")
        print("   - Tab 2: Natural Language (Chatbot)")
        print("   - Tab 3: Anomaly Detection (Graphs & Alerts)")
        print("   - Tab 4: AutoML (Machine Learning)")
        print("   - Tab 1: AI Predictions (Analytics)")
        print("3. If you don't see tabs, refresh the page")
        
    sys.exit(0 if success else 1)