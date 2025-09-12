#!/usr/bin/env python3
"""
Clean up health-check.py files from all services
"""

import os
from pathlib import Path

def cleanup_health_checks():
    """Remove health-check.py files from all services."""
    bus_services_dir = Path("bus-services")
    removed_count = 0
    
    if not bus_services_dir.exists():
        print("❌ bus-services directory not found")
        return
    
    for service_dir in bus_services_dir.iterdir():
        if service_dir.is_dir() and service_dir.name != "__pycache__":
            health_check_file = service_dir / "health-check.py"
            if health_check_file.exists():
                try:
                    health_check_file.unlink()
                    print(f"✅ Removed {health_check_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing {health_check_file}: {e}")
    
    print(f"\n📊 Cleanup complete: Removed {removed_count} health-check.py files")

if __name__ == "__main__":
    cleanup_health_checks()
