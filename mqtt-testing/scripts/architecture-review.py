#!/usr/bin/env python3
"""
Sonos Connection Architecture Review
Analyzes the current network setup and identifies issues
"""

import socket
import subprocess
import json
from pathlib import Path

def get_network_info():
    """Get comprehensive network information"""
    print("🌐 NETWORK ARCHITECTURE ANALYSIS")
    print("=" * 40)

    network_info = {}

    # Get all network interfaces
    try:
        result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, shell=True)
        network_info['ipconfig'] = result.stdout
    except:
        network_info['ipconfig'] = "ipconfig command failed"

    # Get routing table
    try:
        result = subprocess.run(['route', 'print'], capture_output=True, text=True, shell=True)
        network_info['routes'] = result.stdout
    except:
        network_info['routes'] = "route command failed"

    # Test connectivity to speakers
    speaker_ips = ['192.168.1.101', '192.168.1.102']
    connectivity = {}

    for ip in speaker_ips:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 1400))  # Sonos port
            sock.close()
            connectivity[ip] = "CONNECTED" if result == 0 else "BLOCKED"
        except:
            connectivity[ip] = "ERROR"

    network_info['speaker_connectivity'] = connectivity

    return network_info

def analyze_ip_mismatch():
    """Analyze IP address configuration issues"""
    print("\n🔍 IP ADDRESS ANALYSIS")
    print("-" * 25)

    # Get different IP detection methods
    ip_methods = {}

    # Method 1: socket.gethostbyname
    try:
        ip_methods['gethostbyname'] = socket.gethostbyname(socket.gethostname())
    except:
        ip_methods['gethostbyname'] = "FAILED"

    # Method 2: socket connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_methods['socket_connect'] = s.getsockname()[0]
        s.close()
    except:
        ip_methods['socket_connect'] = "FAILED"

    # Method 3: ipconfig parsing
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if 'IPv4 Address' in line and '192.168.1.' in line:
                ip_methods['ipconfig'] = line.split(':')[1].strip()
                break
    except:
        ip_methods['ipconfig'] = "FAILED"

    print("IP Detection Methods:")
    for method, ip in ip_methods.items():
        print(f"  {method}: {ip}")

    # Check for IP mismatch
    ips = [ip for ip in ip_methods.values() if ip != "FAILED"]
    if len(set(ips)) > 1:
        print("\n⚠️  IP MISMATCH DETECTED!")
        print("   Different methods return different IPs")
        print("   This can cause port forwarding to fail")
        print(f"   Port forwarding configured for: 192.168.1.100")
        print(f"   Current IPs detected: {list(set(ips))}")

        return False
    else:
        print("\n✅ IP addresses consistent")
        return True

def analyze_docker_networking():
    """Analyze Docker networking setup"""
    print("\n🐳 DOCKER NETWORK ANALYSIS")
    print("-" * 27)

    # Check if Docker is running
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
        else:
            print("❌ Docker not running or not accessible")
            return
    except:
        print("❌ Docker command failed")
        return

    # Check Docker networks
    try:
        result = subprocess.run(['docker', 'network', 'ls'], capture_output=True, text=True)
        networks = result.stdout.strip().split('\n')[1:]  # Skip header
        print(f"📋 Docker networks: {len(networks)}")
        for network in networks:
            print(f"   {network}")
    except:
        print("❌ Could not list Docker networks")

    # Check for Alicia containers
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=alicia'], capture_output=True, text=True)
        containers = result.stdout.strip().split('\n')
        if len(containers) > 1:  # More than header
            print("✅ Alicia containers found:")
            for container in containers[1:]:
                print(f"   {container}")
        else:
            print("❌ No Alicia containers running")
    except:
        print("❌ Could not check Alicia containers")

def analyze_port_forwarding_issues():
    """Analyze specific port forwarding problems"""
    print("\n🔀 PORT FORWARDING ANALYSIS")
    print("-" * 29)

    issues = []

    # Check if ports are actually listening
    ports_to_check = [8080, 8554]
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                print(f"✅ Port {port}: LISTENING locally")
            else:
                print(f"❌ Port {port}: NOT listening locally")
                issues.append(f"No service listening on port {port}")
        except:
            print(f"❌ Port {port}: ERROR checking")
            issues.append(f"Cannot check port {port}")

    # Check Windows Firewall rules
    print("\n🔥 WINDOWS FIREWALL CHECK")
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                               capture_output=True, text=True)
        rules = result.stdout
        sonos_rules = [line for line in rules.split('\n') if 'sonos' in line.lower()]
        if sonos_rules:
            print("✅ Found Sonos firewall rules:")
            for rule in sonos_rules[:3]:  # Show first 3
                print(f"   {rule.strip()}")
        else:
            print("❌ No Sonos firewall rules found")
            issues.append("Missing Windows firewall rules")
    except:
        print("❌ Cannot check Windows Firewall")
        issues.append("Cannot verify firewall configuration")

    return issues

def provide_architecture_recommendations():
    """Provide architecture improvement recommendations"""
    print("\n💡 ARCHITECTURE RECOMMENDATIONS")
    print("-" * 35)

    print("1. 🔧 FIX IP CONSISTENCY:")
    print("   - Ensure all network interfaces use same IP range")
    print("   - Configure static IP for development machine")
    print("   - Update port forwarding rules to match actual IP")

    print("\n2. 🐳 DOCKER NETWORKING:")
    print("   - Use host networking for Sonos access: --network host")
    print("   - Or use macvlan with proper subnet configuration")
    print("   - Avoid bridge networks that create IP conflicts")

    print("\n3. 🌐 NETWORK ARCHITECTURE:")
    print("   - Speakers: 192.168.1.101, 192.168.1.102")
    print("   - Development PC: 192.168.1.100 (static IP)")
    print("   - Router: 192.168.1.1")
    print("   - All on same subnet: 192.168.1.0/24")

    print("\n4. 🔀 PORT FORWARDING:")
    print("   - External 80 → Internal 192.168.1.100:8080")
    print("   - External 554 → Internal 192.168.1.100:8554")
    print("   - Test with: telnet 192.168.1.100 8080")

    print("\n5. 🧪 TESTING APPROACH:")
    print("   - Test local services first: curl http://localhost:8080")
    print("   - Test network access: curl http://192.168.1.100:8080")
    print("   - Test from speakers: Use Sonos app to verify connectivity")

def main():
    print("🔧 SONOS CONNECTION ARCHITECTURE REVIEW")
    print("=" * 45)

    # Get network information
    network_info = get_network_info()

    # Analyze IP consistency
    ip_consistent = analyze_ip_mismatch()

    # Analyze Docker setup
    analyze_docker_networking()

    # Analyze port forwarding
    issues = analyze_port_forwarding_issues()

    # Provide recommendations
    provide_architecture_recommendations()

    # Summary
    print("\n📊 ARCHITECTURE SUMMARY")
    print("-" * 23)

    if ip_consistent and not issues:
        print("✅ Architecture looks good!")
        print("💡 If ports still blocked, check router SPI firewall")
    else:
        print("❌ Architecture issues detected:")
        if not ip_consistent:
            print("   - IP address inconsistency")
        for issue in issues:
            print(f"   - {issue}")

        print("\n🔧 PRIORITY FIXES:")
        print("   1. Fix IP address consistency")
        print("   2. Ensure services are listening on correct ports")
        print("   3. Verify Windows firewall rules")
        print("   4. Check router SPI firewall settings")

if __name__ == '__main__':
    main()
