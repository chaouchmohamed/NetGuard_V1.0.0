#!/usr/bin/env python3
"""
NetGuard Attack Generator
Run this in a separate terminal while NetGuard is running to test the system
"""

import os
import sys
import time
from pathlib import Path

# Get the absolute path to the netguard directory
NETGUARD_DIR = Path(__file__).parent.parent.absolute()
BACKEND_DIR = NETGUARD_DIR / 'backend'

# Add backend directory to Python path
sys.path.insert(0, str(BACKEND_DIR))

print(f"📂 NetGuard directory: {NETGUARD_DIR}")
print(f"📂 Backend directory: {BACKEND_DIR}")

try:
    from core.traffic_simulator import TrafficSimulator
    from core.feature_extractor import FeatureExtractor
    from models.isolation_forest import AnomalyDetector
    import numpy as np
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("\n🔧 Please install dependencies first:")
    print("   cd ~/Documents/netguard/backend")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
    sys.exit(1)

def print_banner():
    """Print attack generator banner"""
    print("""
    ╔══════════════════════════════════════════╗
    ║     NetGuard Attack Generator v1.0       ║
    ║     Generate attacks to test the system  ║
    ╚══════════════════════════════════════════╝
    """)

def simulate_ddos(duration=20):
    """Simulate DDoS attack"""
    print("\n🔴 STARTING DDoS ATTACK SIMULATION")
    print("═" * 40)
    
    simulator = TrafficSimulator()
    original_weights = simulator.ATTACK_WEIGHTS
    simulator.ATTACK_WEIGHTS = [1.0, 0, 0, 0, 0, 0]  # Only DDoS
    
    try:
        for i in range(duration * 2):  # 2 packets per second
            packet = simulator.generate_packet()
            print(f"⚡ DDoS Packet {i+1:3d}: {packet['src_ip']:15} → {packet['dst_ip']:15} "
                  f"[Size: {packet['packet_size']:4d} bytes] [Rate: {packet['packets_per_second']:5.1f} pps]")
            
            if (i + 1) % 10 == 0:
                print(f"   📊 Current attack stats: {i+1} packets sent")
            
            time.sleep(0.5)
    finally:
        simulator.ATTACK_WEIGHTS = original_weights
    
    print(f"\n✅ DDoS simulation complete! {duration*2} packets sent")

def simulate_port_scan(duration=15):
    """Simulate port scan attack"""
    print("\n🔵 STARTING PORT SCAN SIMULATION")
    print("═" * 40)
    
    simulator = TrafficSimulator()
    original_weights = simulator.ATTACK_WEIGHTS
    simulator.ATTACK_WEIGHTS = [0, 1.0, 0, 0, 0, 0]  # Only port scan
    
    try:
        for i in range(duration * 4):  # 4 packets per second (faster scan)
            packet = simulator.generate_packet()
            print(f"🔍 Port Scan {i+1:3d}: {packet['src_ip']:15} scanning port {packet['dst_port']:5d} "
                  f"[Protocol: {packet['protocol_name']}]")
            time.sleep(0.25)
    finally:
        simulator.ATTACK_WEIGHTS = original_weights
    
    print(f"\n✅ Port scan simulation complete! {duration*4} packets sent")

def simulate_syn_flood(duration=10):
    """Simulate SYN flood attack"""
    print("\n🟡 STARTING SYN FLOOD SIMULATION")
    print("═" * 40)
    
    simulator = TrafficSimulator()
    original_weights = simulator.ATTACK_WEIGHTS
    simulator.ATTACK_WEIGHTS = [0, 0, 1.0, 0, 0, 0]  # Only SYN flood
    
    try:
        for i in range(duration * 10):  # 10 packets per second (very fast)
            packet = simulator.generate_packet()
            flags = packet['flags']
            print(f"🌊 SYN Flood {i+1:3d}: {packet['src_ip']:15} → {packet['dst_ip']:15} "
                  f"[SYN: {flags.get('syn', False)}] [ACK: {flags.get('ack', False)}]")
            time.sleep(0.1)
    finally:
        simulator.ATTACK_WEIGHTS = original_weights
    
    print(f"\n✅ SYN flood simulation complete! {duration*10} packets sent")

def simulate_brute_force(duration=20):
    """Simulate brute force attack"""
    print("\n🟠 STARTING BRUTE FORCE SIMULATION")
    print("═" * 40)
    
    simulator = TrafficSimulator()
    original_weights = simulator.ATTACK_WEIGHTS
    simulator.ATTACK_WEIGHTS = [0, 0, 0, 1.0, 0, 0]  # Only brute force
    
    try:
        ports = [22, 3389]  # SSH and RDP ports
        for i in range(duration * 2):
            packet = simulator.generate_packet()
            print(f"🔑 Brute Force {i+1:3d}: {packet['src_ip']:15} trying port {packet['dst_port']} "
                  f"[Service: {packet['service']}]")
            time.sleep(0.5)
    finally:
        simulator.ATTACK_WEIGHTS = original_weights
    
    print(f"\n✅ Brute force simulation complete! {duration*2} packets sent")

def simulate_data_exfiltration(duration=15):
    """Simulate data exfiltration"""
    print("\n🟣 STARTING DATA EXFILTRATION SIMULATION")
    print("═" * 40)
    
    simulator = TrafficSimulator()
    original_weights = simulator.ATTACK_WEIGHTS
    simulator.ATTACK_WEIGHTS = [0, 0, 0, 0, 1.0, 0]  # Only data exfiltration
    
    try:
        for i in range(duration):
            packet = simulator.generate_packet()
            size_mb = packet['packet_size'] / (1024 * 1024)
            print(f"📤 Data Exfil {i+1:3d}: {packet['src_ip']:15} → {packet['dst_ip']:15} "
                  f"[Size: {packet['packet_size']:6d} bytes ({size_mb:.2f} MB)]")
            time.sleep(1)
    finally:
        simulator.ATTACK_WEIGHTS = original_weights
    
    print(f"\n✅ Data exfiltration simulation complete! {duration} packets sent")

def simulate_all_attacks(duration_per_attack=10):
    """Run all attacks sequentially"""
    print("\n🎯 RUNNING ALL ATTACK TYPES")
    print("═" * 50)
    
    attacks = [
        (simulate_ddos, "DDoS", duration_per_attack),
        (simulate_port_scan, "Port Scan", duration_per_attack),
        (simulate_syn_flood, "SYN Flood", duration_per_attack),
        (simulate_brute_force, "Brute Force", duration_per_attack),
        (simulate_data_exfiltration, "Data Exfiltration", duration_per_attack)
    ]
    
    for attack_func, attack_name, duration in attacks:
        print(f"\n▶ Next attack: {attack_name} (in 3 seconds...)")
        time.sleep(3)
        attack_func(duration)
        print(f"\n⏸ Pausing before next attack...")
        time.sleep(2)
    
    print("\n✅ All attack simulations complete!")

def mixed_traffic_with_attacks(duration=60):
    """Run mixed normal traffic with random attacks"""
    print("\n🎲 RUNNING MIXED TRAFFIC WITH RANDOM ATTACKS")
    print("═" * 50)
    
    simulator = TrafficSimulator()
    attack_types = ['ddos', 'port_scan', 'syn_flood', 'brute_force', 'data_exfiltration', None]
    attack_weights = [0.1, 0.1, 0.1, 0.1, 0.1, 0.5]  # 50% attack probability
    
    simulator.ATTACK_TYPES = attack_types
    simulator.ATTACK_WEIGHTS = attack_weights
    
    print("Generating mixed traffic with 50% attack probability...")
    print("Watch the NetGuard dashboard to see detection in real-time!\n")
    
    attack_count = 0
    for i in range(duration * 2):
        packet = simulator.generate_packet()
        if packet['attack_type']:
            attack_count += 1
            print(f"⚠️ ATTACK DETECTED [{packet['attack_type']}]: {packet['src_ip']} → {packet['dst_ip']}")
        else:
            print(f"✓ Normal traffic: {packet['src_ip']} → {packet['dst_ip']}")
        
        if (i + 1) % 20 == 0:
            print(f"\n📊 Stats so far: {attack_count}/{i+1} attacks ({attack_count/(i+1)*100:.1f}%)\n")
        
        time.sleep(0.5)
    
    print(f"\n✅ Mixed traffic complete! {attack_count} attacks generated")

def main():
    """Main menu"""
    print_banner()
    
    while True:
        print("\n📋 Select attack type to simulate:")
        print("1. 🔴 DDoS Attack")
        print("2. 🔵 Port Scan")
        print("3. 🟡 SYN Flood")
        print("4. 🟠 Brute Force")
        print("5. 🟣 Data Exfiltration")
        print("6. 🎯 All Attacks (sequential)")
        print("7. 🎲 Mixed Traffic (50% attacks)")
        print("8. ❌ Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            duration = int(input("Enter duration in seconds (default 20): ") or "20")
            simulate_ddos(duration)
        
        elif choice == '2':
            duration = int(input("Enter duration in seconds (default 15): ") or "15")
            simulate_port_scan(duration)
        
        elif choice == '3':
            duration = int(input("Enter duration in seconds (default 10): ") or "10")
            simulate_syn_flood(duration)
        
        elif choice == '4':
            duration = int(input("Enter duration in seconds (default 20): ") or "20")
            simulate_brute_force(duration)
        
        elif choice == '5':
            duration = int(input("Enter duration in seconds (default 15): ") or "15")
            simulate_data_exfiltration(duration)
        
        elif choice == '6':
            duration = int(input("Enter duration per attack in seconds (default 10): ") or "10")
            simulate_all_attacks(duration)
        
        elif choice == '7':
            duration = int(input("Enter total duration in seconds (default 60): ") or "60")
            mixed_traffic_with_attacks(duration)
        
        elif choice == '8':
            print("\n👋 Exiting NetGuard Attack Generator")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-8")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Attack generator stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")