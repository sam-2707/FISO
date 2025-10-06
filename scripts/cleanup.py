#!/usr/bin/env python3
"""
FISO Project Cleanup Script
Removes unnecessary files, optimizes imports, and cleans up the codebase
"""

import os
import shutil
import glob
import re
from pathlib import Path

def cleanup_pycache():
    """Remove all __pycache__ directories"""
    print("🧹 Cleaning __pycache__ directories...")
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # Copy list to avoid modification during iteration
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                print(f"   Removing {pycache_path}")
                shutil.rmtree(pycache_path)
                dirs.remove(dir_name)

def cleanup_temp_files():
    """Remove temporary files"""
    print("🧹 Cleaning temporary files...")
    temp_patterns = [
        '*.pyc', '*.pyo', '*.tmp', '*.log', '*.bak', '*.swp', '*.swo',
        '.DS_Store', 'Thumbs.db', '*.orig'
    ]
    
    for pattern in temp_patterns:
        for file_path in glob.glob(f"**/{pattern}", recursive=True):
            print(f"   Removing {file_path}")
            os.remove(file_path)

def cleanup_node_modules():
    """Clean and reinstall node modules"""
    print("🧹 Cleaning Node.js dependencies...")
    
    frontend_path = Path('frontend')
    if frontend_path.exists():
        node_modules = frontend_path / 'node_modules'
        package_lock = frontend_path / 'package-lock.json'
        
        if node_modules.exists():
            print("   Removing node_modules...")
            shutil.rmtree(node_modules)
        
        if package_lock.exists():
            print("   Removing package-lock.json...")
            os.remove(package_lock)

def cleanup_test_databases():
    """Remove test database files"""
    print("🧹 Cleaning test databases...")
    db_patterns = ['*.test.db', 'test*.db', '*_test.db']
    
    for pattern in db_patterns:
        for db_file in glob.glob(f"**/{pattern}", recursive=True):
            print(f"   Removing {db_file}")
            os.remove(db_file)

def optimize_imports():
    """Remove unused imports (basic cleanup)"""
    print("🔧 Optimizing Python imports...")
    
    python_files = glob.glob("**/*.py", recursive=True)
    for py_file in python_files:
        if '__pycache__' in py_file:
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove duplicate imports (basic)
            lines = content.split('\n')
            import_lines = set()
            cleaned_lines = []
            
            for line in lines:
                if line.strip().startswith(('import ', 'from ')):
                    if line not in import_lines:
                        import_lines.add(line)
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            if cleaned_content != content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                print(f"   Optimized imports in {py_file}")
                
        except Exception as e:
            print(f"   Warning: Could not process {py_file}: {e}")

def main():
    """Run all cleanup operations"""
    print("🚀 Starting FISO Project Cleanup...")
    print("=" * 50)
    
    cleanup_pycache()
    cleanup_temp_files()
    cleanup_test_databases()
    optimize_imports()
    
    print("=" * 50)
    print("✅ Cleanup completed successfully!")
    print("\nNext steps:")
    print("1. cd frontend && npm install  # Reinstall clean dependencies")
    print("2. python -m pytest tests/    # Run tests to verify everything works")
    print("3. npm start                   # Start the development server")

if __name__ == "__main__":
    main()