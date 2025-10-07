#!/usr/bin/env python3
"""
Final Project Organization Script
Moves all .md files to documentation folder and cleans up unnecessary files
"""

import os
import shutil
import glob
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_documentation_structure():
    """Create organized documentation structure"""
    base_path = Path(".")
    
    # Create main documentation directory
    docs_structure = {
        "documentation": {
            "README": [],
            "guides": [],
            "reports": [],
            "project": [],
            "api": [],
            "deployment": []
        }
    }
    
    for main_dir, sub_dirs in docs_structure.items():
        main_path = base_path / main_dir
        main_path.mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {main_path}")
        
        if isinstance(sub_dirs, dict):
            for sub_dir in sub_dirs:
                sub_path = main_path / sub_dir
                sub_path.mkdir(exist_ok=True)
                logger.info(f"✅ Created subdirectory: {sub_path}")

def organize_md_files():
    """Move and organize all .md files"""
    
    # Define file mappings based on content/purpose
    md_mappings = {
        # README files
        "documentation/README": [
            "README.md",
            "README_PRODUCTION.md", 
            "README_ATHARMAN.md"
        ],
        
        # Project documentation
        "documentation/project": [
            "ROADMAP.md",
            "TRANSFORMATION_COMPLETE.md",
            "ATHARMAN_SUMMARY.md"
        ],
        
        # Reports
        "documentation/reports": [
            "AI_ACCURACY_REPORT.md"
        ],
        
        # Deployment guides
        "documentation/deployment": [
            "DEPLOYMENT_CHECKLIST.md"
        ],
        
        # Guides (from existing docs)
        "documentation/guides": [
            "docs/production/PRODUCTION_READINESS_CHECKLIST.md",
            "docs/production/PRODUCTION_IMPLEMENTATION.md",
            "docs/deployment/DEPLOYMENT_GUIDE.md",
            "docs/deployment/STARTUP_GUIDE.md"
        ],
        
        # API documentation
        "documentation/api": [
            "k8s/README-AWS.md"
        ]
    }
    
    moved_files = 0
    
    for target_dir, files in md_mappings.items():
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        for file_pattern in files:
            # Handle both direct files and glob patterns
            if "*" in file_pattern:
                matching_files = glob.glob(file_pattern)
            else:
                matching_files = [file_pattern] if os.path.exists(file_pattern) else []
            
            for file_path in matching_files:
                if os.path.exists(file_path):
                    source = Path(file_path)
                    destination = target_path / source.name
                    
                    try:
                        shutil.move(str(source), str(destination))
                        logger.info(f"📄 Moved: {file_path} → {destination}")
                        moved_files += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to move {file_path}: {e}")
    
    # Find and move any remaining .md files
    remaining_md_files = []
    for root, dirs, files in os.walk("."):
        # Skip the documentation directory we just created
        if "documentation" in root:
            continue
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                remaining_md_files.append(full_path)
    
    if remaining_md_files:
        misc_dir = Path("documentation/misc")
        misc_dir.mkdir(exist_ok=True)
        
        for md_file in remaining_md_files:
            source = Path(md_file)
            destination = misc_dir / source.name
            try:
                shutil.move(str(source), str(destination))
                logger.info(f"📄 Moved remaining: {md_file} → {destination}")
                moved_files += 1
            except Exception as e:
                logger.error(f"❌ Failed to move {md_file}: {e}")
    
    return moved_files

def cleanup_unnecessary_files():
    """Remove unnecessary and redundant files"""
    
    # Files to remove (keeping important ones)
    files_to_remove = [
        # Duplicate/backup files
        ".env.example.backup",
        ".env.template.backup",
        
        # Development scripts no longer needed
        "cleanup_and_organize.py",
        "api_demo.py",
        "executive_reporting.py",
        
        # Old startup scripts (we have better ones now)
        "start-atharman.ps1",
        "start-fiso.ps1",
        
        # Redundant requirement files (keep production and core)
        "requirements-enhanced.txt",
        "requirements-minimal.txt",
        
        # Development/demo files
        "docker-start.sh",
        "docker-fiso.ps1"
    ]
    
    # Directories to remove if empty or unnecessary
    dirs_to_check = [
        "public",  # If empty
        "__pycache__",  # Python cache
        "node_modules",  # Will be regenerated
    ]
    
    removed_files = 0
    
    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"🗑️  Removed file: {file_path}")
                removed_files += 1
            except Exception as e:
                logger.error(f"❌ Failed to remove {file_path}: {e}")
    
    # Remove or clean directories
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            try:
                if dir_path == "node_modules":
                    # Remove node_modules (will be regenerated with npm install)
                    shutil.rmtree(dir_path)
                    logger.info(f"🗑️  Removed directory: {dir_path}")
                    removed_files += 1
                elif dir_path == "__pycache__":
                    # Remove all __pycache__ directories
                    for root, dirs, files in os.walk(".", topdown=False):
                        if "__pycache__" in dirs:
                            cache_path = os.path.join(root, "__pycache__")
                            shutil.rmtree(cache_path)
                            logger.info(f"🗑️  Removed cache: {cache_path}")
                            removed_files += 1
                elif dir_path == "public":
                    # Check if public directory is empty or only has basic files
                    if os.path.isdir(dir_path):
                        contents = os.listdir(dir_path)
                        if len(contents) == 0 or all(f.startswith('.') for f in contents):
                            shutil.rmtree(dir_path)
                            logger.info(f"🗑️  Removed empty directory: {dir_path}")
                            removed_files += 1
            except Exception as e:
                logger.error(f"❌ Failed to remove {dir_path}: {e}")
    
    return removed_files

def cleanup_old_docs_structure():
    """Remove old docs structure after moving files"""
    old_docs_dirs = ["docs/production", "docs/deployment", "docs/api"]
    
    for dir_path in old_docs_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                # Check if empty
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logger.info(f"🗑️  Removed empty directory: {dir_path}")
            except Exception as e:
                logger.error(f"❌ Failed to remove {dir_path}: {e}")
    
    # Remove docs directory if it's empty
    if os.path.exists("docs") and os.path.isdir("docs"):
        try:
            remaining_items = os.listdir("docs")
            if not remaining_items:
                os.rmdir("docs")
                logger.info(f"🗑️  Removed empty docs directory")
        except Exception as e:
            logger.error(f"❌ Failed to remove docs directory: {e}")

def create_documentation_index():
    """Create an index file for the documentation"""
    
    index_content = """# FISO Project Documentation

This directory contains all project documentation organized by category.

## Directory Structure

### 📋 README Files
- **README.md** - Main project README
- **README_PRODUCTION.md** - Production deployment guide
- **README_ATHARMAN.md** - ATHARMAN system documentation

### 📊 Project Documentation
- **ROADMAP.md** - Project roadmap and future plans
- **TRANSFORMATION_COMPLETE.md** - Transformation summary
- **ATHARMAN_SUMMARY.md** - ATHARMAN system summary

### 📈 Reports
- **AI_ACCURACY_REPORT.md** - AI system accuracy analysis

### 🚀 Deployment
- **DEPLOYMENT_CHECKLIST.md** - Production deployment checklist

### 📖 Guides
- **PRODUCTION_READINESS_CHECKLIST.md** - Production readiness guide
- **PRODUCTION_IMPLEMENTATION.md** - Implementation guide
- **DEPLOYMENT_GUIDE.md** - Detailed deployment guide
- **STARTUP_GUIDE.md** - Quick start guide

### 🔌 API Documentation
- **README-AWS.md** - AWS deployment documentation

## Quick Links

- [Main README](README/README.md)
- [Production Guide](README/README_PRODUCTION.md)
- [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)
- [Project Roadmap](project/ROADMAP.md)

---

**FISO** - Financial Intelligence System Optimizer
*Production-ready cloud cost optimization platform*
"""
    
    index_path = Path("documentation/INDEX.md")
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        logger.info(f"📋 Created documentation index: {index_path}")
    except Exception as e:
        logger.error(f"❌ Failed to create index: {e}")

def main():
    """Main execution function"""
    logger.info("🚀 Starting final project organization...")
    
    # Step 1: Create documentation structure
    logger.info("\n📁 Creating documentation structure...")
    create_documentation_structure()
    
    # Step 2: Move all .md files
    logger.info("\n📄 Organizing markdown files...")
    moved_files = organize_md_files()
    
    # Step 3: Clean up unnecessary files
    logger.info("\n🗑️  Cleaning up unnecessary files...")
    removed_files = cleanup_unnecessary_files()
    
    # Step 4: Clean up old docs structure
    logger.info("\n🧹 Cleaning up old directory structure...")
    cleanup_old_docs_structure()
    
    # Step 5: Create documentation index
    logger.info("\n📋 Creating documentation index...")
    create_documentation_index()
    
    # Summary
    logger.info(f"\n✅ PROJECT ORGANIZATION COMPLETE!")
    logger.info(f"📄 Markdown files moved: {moved_files}")
    logger.info(f"🗑️  Files removed: {removed_files}")
    logger.info(f"📁 New structure: documentation/ directory created")
    logger.info(f"📋 Documentation index created at: documentation/INDEX.md")
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("1. Review documentation/INDEX.md for overview")
    print("2. Check documentation/ directory structure")
    print("3. Update any internal links in documentation")
    print("4. Run: npm install (in frontend/) to regenerate node_modules")
    print("5. Test the application to ensure all paths work")
    print("="*60)

if __name__ == "__main__":
    main()