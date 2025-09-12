#!/usr/bin/env python3
"""
Remove health-check.py references from Dockerfiles
"""

import re
from pathlib import Path

def cleanup_dockerfiles():
    """Remove health-check.py references from all Dockerfiles."""
    bus_services_dir = Path("bus-services")
    updated_count = 0
    
    if not bus_services_dir.exists():
        print("❌ bus-services directory not found")
        return
    
    for service_dir in bus_services_dir.iterdir():
        if service_dir.is_dir() and service_dir.name != "__pycache__":
            dockerfile = service_dir / "Dockerfile"
            if dockerfile.exists():
                try:
                    with open(dockerfile, 'r') as f:
                        content = f.read()
                    
                    # Remove COPY health-check.py . line
                    if 'COPY health-check.py .' in content:
                        content = content.replace('COPY health-check.py .\n', '')
                        content = content.replace('COPY health-check.py .', '')
                        
                        with open(dockerfile, 'w') as f:
                            f.write(content)
                        
                        print(f"✅ Updated {dockerfile}")
                        updated_count += 1
                        
                except Exception as e:
                    print(f"❌ Error updating {dockerfile}: {e}")
    
    print(f"\n📊 Cleanup complete: Updated {updated_count} Dockerfiles")

if __name__ == "__main__":
    cleanup_dockerfiles()
