#!/usr/bin/env python3
"""
NetGuard REAL Traffic Attack Generator - SIMPLE VERSION
Uses standard Linux tools to generate real network traffic
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

# ============= CONFIG =============
INTERFACE = "wlan0"  # Your WiFi interface
TARGET_IP = "8.8.8.8"  # Google DNS (safe target)
YOUR_IP = None
STOP_ATTACK = False

# ============= GET YOUR IP =============
def get_my_ip():
    try:
        result = subprocess.run(['ip', '-4', 'addr', 'show', INTERFACE], 
                               capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line:
                ip = line.strip().split()[1].split('/')[0]
                print(f"✅ Your IP: {ip}")
                return ip
    except:
        pass
    return "192.168.1.100"

YOUR_IP = get_my_ip()

# ============= ATTACK FUNCTIONS =============
def ping_attack(target, duration=20):
    """Simple ping flood using system ping"""
    print(f"\n🔴 PING FLOOD on {target}")
    print("═" * 50)
    
    cmd = ['ping', target, '-i', '0.2']  # 5 pings per second
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        time.sleep(duration)
    finally:
        process.terminate()
        print(f"✅ Ping flood complete")

def curl_attack(target, duration=20):
    """HTTP requests using curl"""
    print(f"\n🔵 HTTP FLOOD on {target}")
    print("═" * 50)
    
    def curl_loop():
        while not STOP_ATTACK:
            try:
                subprocess.run(['curl', '-s', target, '-o', '/dev/null'], 
                             timeout=2, stderr=subprocess.DEVNULL)
            except:
                pass
    
    threads = []
    for i in range(10):  # 10 parallel threads
        t = threading.Thread(target=curl_loop, daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    print(f"✅ HTTP flood complete")

def dns_attack(duration=20):
    """DNS queries using dig"""
    print(f"\n🟡 DNS QUERY FLOOD")
    print("═" * 50)
    
    domains = ['google.com', 'github.com', 'stackoverflow.com', 
               'amazon.com', 'netflix.com', 'facebook.com']
    
    def dns_loop():
        while not STOP_ATTACK:
            for domain in domains:
                if STOP_ATTACK:
                    break
                try:
                    subprocess.run(['dig', domain, '+short'], 
                                 timeout=1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except:
                    pass
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=dns_loop, daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    print(f"✅ DNS flood complete")

def nmap_scan(target, duration=15):
    """Port scan using nmap"""
    print(f"\n🟠 PORT SCAN on {target}")
    print("═" * 50)
    
    cmd = ['nmap', '-p', '1-1000', '-T4', target]
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        time.sleep(duration)
    finally:
        process.terminate()
        print(f"✅ Port scan complete")

def hping_attack(target, attack_type='syn', duration=20):
    """hping3 attacks (if installed)"""
    if subprocess.run(['which', 'hping3'], capture_output=True).returncode != 0:
        print("❌ hping3 not installed. Install with: sudo apt install hping3")
        return
    
    print(f"\n🟣 HPING3 {attack_type.upper()} on {target}")
    print("═" * 50)
    
    if attack_type == 'syn':
        cmd = ['hping3', '-S', '--flood', '-p', '80', target]
    elif attack_type == 'udp':
        cmd = ['hping3', '--udp', '--flood', '-p', '53', target]
    elif attack_type == 'icmp':
        cmd = ['hping3', '--icmp', '--flood', target]
    else:
        return
    
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        time.sleep(duration)
    finally:
        process.terminate()
        print(f"✅ hping3 attack complete")

def iperf_attack(target, duration=20):
    """Bandwidth test using iperf3"""
    print(f"\n⚡ BANDWIDTH FLOOD on {target}")
    print("═" * 50)
    
    cmd = ['iperf3', '-c', target, '-t', str(duration), '-P', '5']
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(duration + 2)
    print(f"✅ Bandwidth test complete")

# ============= CHECK TOOLS =============
def check_tools():
    tools = {
        'ping': 'iputils-ping',
        'curl': 'curl',
        'dig': 'dnsutils',
        'nmap': 'nmap',
        'hping3': 'hping3',
        'iperf3': 'iperf3'
    }
    
    print("\n🔧 Checking required tools:")
    for tool, pkg in tools.items():
        if subprocess.run(['which', tool], capture_output=True).returncode == 0:
            print(f"  ✅ {tool} installed")
        else:
            print(f"  ❌ {tool} not installed (sudo apt install {pkg})")

# ============= MAIN =============
def print_banner():
    print("""
    ╔══════════════════════════════════════════════╗
    ║  NetGuard REAL Traffic Attack Generator      ║
    ║  Creates REAL network traffic for testing    ║
    ╚══════════════════════════════════════════════╝
    """)
    print(f"📡 Interface: {INTERFACE}")
    print(f"🖥️  Your IP: {YOUR_IP}")
    print("")

def main():
    global STOP_ATTACK
    
    # Check if running as root (needed for some attacks)
    if os.geteuid() != 0:
        print("⚠️  Some attacks need root. Run with: sudo python3 generate_attacks.py")
    
    print_banner()
    check_tools()
    
    while True:
        print(f"\n📋 Select attack type:")
        print("1. 🔴 Ping Flood (ICMP) - ping 8.8.8.8")
        print("2. 🔵 HTTP Flood - curl google.com")
        print("3. 🟡 DNS Flood - dig random domains")
        print("4. 🟠 Port Scan - nmap scan")
        print("5. 🟣 SYN Flood - hping3 (requires hping3)")
        print("6. ⚡ UDP Flood - hping3")
        print("7. 🎯 Mixed Attack - run all")
        print("8. 🛑 Stop attack")
        print("9. ❌ Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            target = input("Enter target IP (default 8.8.8.8): ") or "8.8.8.8"
            duration = int(input("Duration in seconds (default 20): ") or "20")
            STOP_ATTACK = False
            ping_attack(target, duration)
        
        elif choice == '2':
            target = input("Enter target URL (default google.com): ") or "google.com"
            duration = int(input("Duration in seconds (default 20): ") or "20")
            STOP_ATTACK = False
            curl_attack(f"http://{target}", duration)
        
        elif choice == '3':
            duration = int(input("Duration in seconds (default 20): ") or "20")
            STOP_ATTACK = False
            dns_attack(duration)
        
        elif choice == '4':
            target = input("Enter target IP (default 8.8.8.8): ") or "8.8.8.8"
            duration = int(input("Duration in seconds (default 15): ") or "15")
            STOP_ATTACK = False
            nmap_scan(target, duration)
        
        elif choice == '5':
            target = input("Enter target IP (default 8.8.8.8): ") or "8.8.8.8"
            duration = int(input("Duration in seconds (default 20): ") or "20")
            STOP_ATTACK = False
            hping_attack(target, 'syn', duration)
        
        elif choice == '6':
            target = input("Enter target IP (default 8.8.8.8): ") or "8.8.8.8"
            duration = int(input("Duration in seconds (default 20): ") or "20")
            STOP_ATTACK = False
            hping_attack(target, 'udp', duration)
        
        elif choice == '7':
            target = input("Enter target IP (default 8.8.8.8): ") or "8.8.8.8"
            duration = int(input("Duration per attack (default 10): ") or "10")
            STOP_ATTACK = False
            print("\n🎯 Starting mixed attack...")
            ping_attack(target, duration)
            curl_attack("http://google.com", duration)
            dns_attack(duration)
            print("✅ Mixed attack complete")
        
        elif choice == '8':
            print("\n🛑 Stopping attack...")
            STOP_ATTACK = True
            time.sleep(2)
        
        elif choice == '9':
            print("\n👋 Exiting")
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Attack generator stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")