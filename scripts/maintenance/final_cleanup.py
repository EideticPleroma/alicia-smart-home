#!/usr/bin/env python3
"""
Final cleanup of the Alicia project
Remove temporary files, outdated documentation, and organize structure
"""

import os
import shutil
from pathlib import Path

def cleanup_temporary_files():
    """Remove temporary and development files."""
    files_to_remove = [
        # Temporary Python scripts
        "cleanup_health_checks.py",
        "cleanup_dockerfiles.py",
        "final_cleanup.py",
        
        # CLINE development files
        "CLINE_BUG_FIX_PROMPT.md",
        "CLINE_PROMPT_CODE_QUALITY_IMPROVEMENTS_CONCISE.md",
        "CLINE_PROMPT_CODE_QUALITY_IMPROVEMENTS.md",
        "CLINE_PROMPT_FINAL_FIXES.md",
        "CLINE_PROMPT_WEB_MONITORING_APP.md",
        
        # Implementation plans (keep in docs if needed)
        "WEB_MONITORING_APP_IMPLEMENTATION_PLAN.md",
        "WEB_MONITORING_APP_PLAN.md",
        "WEB_MONITORING_APP_SUMMARY.md",
        
        # Reports (keep main one, remove duplicates)
        "DOUBLE_CHECK_REPORT.md",
        
        # Other temporary files
        "CONFIG_SCHEMA_EXAMPLES.md",
        "FRONTEND_RULES_CONFIG_MANAGER.md",
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        if Path(file_path).exists():
            try:
                Path(file_path).unlink()
                print(f"✅ Removed {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")
    
    return removed_count

def cleanup_cline_files():
    """Remove CLINE development files from alicia-config-manager."""
    cline_files = [
        "alicia-config-manager/CLINE_ENHANCEMENTS_PROMPT.md",
        "alicia-config-manager/CLINE_IMPLEMENTATION_PROMPT.md",
        "alicia-config-manager/CLINE_PHASE_1_FIXES.md",
        "alicia-config-manager/CLINE_PHASE_1_SETUP.md",
        "alicia-config-manager/CLINE_PHASE_2_BACKEND.md",
        "alicia-config-manager/CLINE_PHASE_2_FIXES.md",
        "alicia-config-manager/CLINE_PHASE_3_FRONTEND.md",
        "alicia-config-manager/CLINE_PHASE_4_COMPONENTS.md",
        "alicia-config-manager/CLINE_PHASE_5_INTEGRATION.md",
        "alicia-config-manager/CLINE_PHASE_5B_COMPLETION_FIX.md",
        "alicia-config-manager/CLINE_PHASE_5B_COMPLETION_PROMPT.md",
        "alicia-config-manager/CLINE_TYPESCRIPT_FIXES.md",
    ]
    
    removed_count = 0
    for file_path in cline_files:
        if Path(file_path).exists():
            try:
                Path(file_path).unlink()
                print(f"✅ Removed {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")
    
    return removed_count

def organize_documentation():
    """Move important documentation to docs folder."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Move important files to docs
    files_to_move = {
        "ALICIA_PROJECT_REVIEW_REPORT.md": "docs/00-Project-Review-Report.md",
    }
    
    moved_count = 0
    for src, dst in files_to_move.items():
        if Path(src).exists():
            try:
                shutil.move(src, dst)
                print(f"✅ Moved {src} to {dst}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Error moving {src}: {e}")
    
    return moved_count

def cleanup_empty_directories():
    """Remove empty directories."""
    empty_dirs = [
        "-p",  # This seems to be an empty directory
    ]
    
    removed_count = 0
    for dir_path in empty_dirs:
        if Path(dir_path).exists() and Path(dir_path).is_dir():
            try:
                if not any(Path(dir_path).iterdir()):  # Check if empty
                    Path(dir_path).rmdir()
                    print(f"✅ Removed empty directory {dir_path}")
                    removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")
    
    return removed_count

def main():
    """Main cleanup function."""
    print("🧹 Starting final cleanup of Alicia project...")
    
    # Clean up temporary files
    print("\n📁 Cleaning up temporary files...")
    temp_removed = cleanup_temporary_files()
    
    # Clean up CLINE files
    print("\n📁 Cleaning up CLINE development files...")
    cline_removed = cleanup_cline_files()
    
    # Organize documentation
    print("\n📁 Organizing documentation...")
    docs_moved = organize_documentation()
    
    # Clean up empty directories
    print("\n📁 Cleaning up empty directories...")
    dirs_removed = cleanup_empty_directories()
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   - Removed {temp_removed} temporary files")
    print(f"   - Removed {cline_removed} CLINE development files")
    print(f"   - Moved {docs_moved} files to docs folder")
    print(f"   - Removed {dirs_removed} empty directories")
    
    print(f"\n✅ Final cleanup complete!")

if __name__ == "__main__":
    main()
