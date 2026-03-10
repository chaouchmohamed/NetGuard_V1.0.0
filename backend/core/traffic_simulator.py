import random
import time
import numpy as np
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import uuid
import logging

logger = logging.getLogger(__name__)

class TrafficSimulator:
    """Simulates realistic network traffic with occasional attacks"""
    
    # Common IP ranges for simulation
    PRIVATE_IPS = [
        '192.168.1.{}',
        '10.0.0.{}',
        '172.16.{}',
        '192.168.0.{}'
    ]
    
    PUBLIC_IPS = [
        '8.8.8.8',      # Google DNS
        '1.1.1.1',      # Cloudflare DNS
        '13.107.21.200', # Microsoft
        '140.82.112.3',  # GitHub
        '151.101.1.140', # Fastly
        '104.16.0.0',    # Cloudflare
        '172.217.0.0',   # Google
        '31.13.79.246',  # Facebook
        '54.239.28.85',  # Amazon
        '52.58.78.16'    # AWS
    ]
    
    PROTOCOLS = {
        6: 'TCP',
        17: 'UDP',
        1: 'ICMP'
    }
    
    COMMON_PORTS = {
        80: 'HTTP',
        443: 'HTTPS',
        53: 'DNS',
        22: 'SSH',
        3389: 'RDP',
        21: 'FTP',
        25: 'SMTP',
        110: 'POP3',
        143: 'IMAP',
        8080: 'HTTP-ALT',
        8443: 'HTTPS-ALT'
    }
    
    ATTACK_TYPES = ['ddos', 'port_scan', 'syn_flood', 'brute_force', 'data_exfiltration', None]
    ATTACK_WEIGHTS = [0.1, 0.1, 0.1, 0.1, 0.1, 0.5]  # 50% attack probability    
    def __init__(self, attack_probability: float = 0.15):
        """
        Initialize traffic simulator
        
        Args:
            attack_probability: Probability of generating attack traffic (0-1)
        """
        self.attack_probability = attack_probability
        self.packet_count = 0
        self.src_ip_pool = self._generate_ip_pool(50)
        self.dst_ip_pool = self._generate_ip_pool(20, include_public=True)
        self.active_connections: Dict[str, Dict] = {}
        self.last_packet_time = time.time()
        self.packet_rate_window: List[float] = []
        self.byte_rate_window: List[Tuple[float, int]] = []
        
        # Attack-specific state
        self.port_scan_target = None
        self.port_scan_port = 1
        self.ddos_targets = []
        
    def _generate_ip_pool(self, count: int, include_public: bool = False) -> List[str]:
        """Generate a pool of IP addresses"""
        ips = []
        
        # Generate private IPs
        for i in range(count):
            template = random.choice(self.PRIVATE_IPS)
            if '{}' in template:
                ips.append(template.format(random.randint(2, 254)))
            else:
                ips.append(f"{template}.{random.randint(2, 254)}")
        
        # Add some public IPs
        if include_public:
            ips.extend(random.sample(self.PUBLIC_IPS, min(len(self.PUBLIC_IPS), count // 2)))
        
        return ips
    
    def _generate_flags(self, protocol: int, attack_type: Optional[str] = None) -> Dict[str, bool]:
        """Generate TCP flags based on protocol and attack type"""
        flags = {
            'syn': False,
            'ack': False,
            'fin': False,
            'rst': False,
            'psh': False,
            'urg': False
        }
        
        if protocol != 6:  # Not TCP
            return flags
        
        if attack_type == 'syn_flood':
            flags['syn'] = True
            flags['ack'] = False
        elif attack_type == 'port_scan':
            flags['syn'] = True
            flags['ack'] = False
        elif attack_type == 'ddos':
            flags['syn'] = random.random() > 0.5
            flags['ack'] = not flags['syn'] if random.random() > 0.3 else False
        else:
            # Normal TCP flags
            rand = random.random()
            if rand < 0.3:
                flags['syn'] = True
            elif rand < 0.6:
                flags['ack'] = True
            elif rand < 0.8:
                flags['syn'] = flags['ack'] = True
            elif rand < 0.9:
                flags['fin'] = flags['ack'] = True
            else:
                flags['rst'] = True
        
        return flags
    
    def _update_rate_windows(self, current_time: float, packet_size: int):
        """Update packet and byte rate windows"""
        # Maintain 1-second window
        self.packet_rate_window = [t for t in self.packet_rate_window if current_time - t < 1.0]
        self.packet_rate_window.append(current_time)
        
        self.byte_rate_window = [(t, s) for t, s in self.byte_rate_window if current_time - t < 1.0]
        self.byte_rate_window.append((current_time, packet_size))
    
    def get_current_rates(self) -> Tuple[float, float]:
        """Get current packets per second and bytes per second"""
        current_time = time.time()
        
        packets_per_second = len(self.packet_rate_window)
        bytes_per_second = sum(size for _, size in self.byte_rate_window)
        
        return packets_per_second, bytes_per_second
    
    def generate_packet(self) -> Dict:
        """
        Generate a single network packet (realistic simulation)
        
        Returns:
            Dictionary containing packet information
        """
        self.packet_count += 1
        current_time = time.time()
        time_since_last = current_time - self.last_packet_time
        self.last_packet_time = current_time
        
        # Determine if this packet is part of an attack
        attack_type = random.choices(
            self.ATTACK_TYPES, 
            weights=self.ATTACK_WEIGHTS,
            k=1
        )[0]
        
        # Select source and destination IPs
        if attack_type == 'ddos':
            # Multiple sources to one target
            src_ip = random.choice(self.src_ip_pool)
            dst_ip = random.choice(self.dst_ip_pool) if not self.ddos_targets else random.choice(self.ddos_targets)
            if len(self.ddos_targets) < 3:
                self.ddos_targets.append(dst_ip)
                
        elif attack_type == 'port_scan':
            # One source scanning multiple ports on a target
            if not self.port_scan_target:
                self.port_scan_target = random.choice(self.dst_ip_pool)
            src_ip = random.choice(self.src_ip_pool)
            dst_ip = self.port_scan_target
            
        elif attack_type == 'brute_force':
            # Repeated attempts from same source
            src_ip = random.choice(self.src_ip_pool)
            dst_ip = random.choice(self.dst_ip_pool)
            
        else:
            src_ip = random.choice(self.src_ip_pool)
            dst_ip = random.choice(self.dst_ip_pool)
        
        # Select ports
        if attack_type == 'port_scan':
            dst_port = self.port_scan_port
            self.port_scan_port = (self.port_scan_port % 65535) + 1
            src_port = random.randint(1024, 65535)
        elif attack_type == 'brute_force':
            dst_port = random.choice([22, 3389])  # SSH or RDP
            src_port = random.randint(1024, 65535)
        else:
            dst_port = random.choice(list(self.COMMON_PORTS.keys()) + [random.randint(1024, 65535)])
            src_port = random.randint(1024, 65535)
        
        # Select protocol
        if attack_type in ['syn_flood', 'port_scan']:
            protocol = 6  # TCP
        else:
            protocol = random.choice([6, 17, 1])
        
        # Generate packet size
        if attack_type == 'data_exfiltration':
            packet_size = random.randint(1000, 65000)
        elif attack_type == 'ddos':
            packet_size = random.randint(40, 200)
        else:
            packet_size = random.randint(40, 1500)
        
        # Generate flags
        flags = self._generate_flags(protocol, attack_type)
        
        # Update rate windows
        self._update_rate_windows(current_time, packet_size)
        packets_per_second, bytes_per_second = self.get_current_rates()
        
        # Create connection ID for tracking
        conn_id = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"
        
        # Track connection duration
        if conn_id not in self.active_connections:
            self.active_connections[conn_id] = {
                'start_time': current_time,
                'packets': 0
            }
        self.active_connections[conn_id]['packets'] += 1
        connection_duration = current_time - self.active_connections[conn_id]['start_time']
        
        # Clean up old connections
        if len(self.active_connections) > 1000:
            # Remove oldest connections
            old_conns = sorted(self.active_connections.items(), key=lambda x: x[1]['start_time'])[:500]
            for conn_id, _ in old_conns:
                del self.active_connections[conn_id]
        
        # Create packet dictionary
        packet = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'timestamp_epoch': current_time,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': protocol,
            'protocol_name': self.PROTOCOLS.get(protocol, 'UNKNOWN'),
            'packet_size': packet_size,
            'ttl': random.randint(32, 255),
            'flags': flags,
            'inter_arrival_time': time_since_last,
            'packets_per_second': packets_per_second,
            'bytes_per_second': bytes_per_second,
            'connection_duration': connection_duration,
            'attack_type': attack_type,
            'service': self.COMMON_PORTS.get(dst_port, 'unknown')
        }
        
        return packet
    
    def generate_batch(self, count: int) -> list:
        """Generate a batch of packets"""
        return [self.generate_packet() for _ in range(count)]

# Example usage
if __name__ == "__main__":
    simulator = TrafficSimulator()
    for i in range(10):
        packet = simulator.generate_packet()
        print(f"Packet {i+1}: {packet['attack_type'] or 'normal'} - {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']}")
