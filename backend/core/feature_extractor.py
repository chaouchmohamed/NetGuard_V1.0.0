import numpy as np
from typing import Dict, List, Optional

class FeatureExtractor:
    """Extracts ML features from network packets"""
    
    def __init__(self):
        self.feature_names = [
            'packet_size', 'inter_arrival_time', 'port_number', 'protocol_encoded',
            'packets_per_second', 'bytes_per_second', 'src_port', 'dst_port',
            'flag_syn', 'flag_ack', 'flag_fin', 'flag_rst', 'connection_duration'
        ]
        
        # Normalization constants (pre-computed from training data)
        self.max_packet_size = 65535
        self.max_port = 65535
        self.max_pps = 10000
        self.max_bps = 100000000
        self.max_duration = 60
        
    def extract(self, packet: Dict) -> np.ndarray:
        """
        Extract feature vector from packet dictionary
        
        Args:
            packet: Dictionary containing packet information
            
        Returns:
            Numpy array of 13 features normalized to appropriate ranges
        """
        features = np.zeros(len(self.feature_names))
        
        # Feature 0: packet_size (normalized)
        features[0] = min(packet.get('packet_size', 0) / self.max_packet_size, 1.0)
        
        # Feature 1: inter_arrival_time (log transformed)
        iat = packet.get('inter_arrival_time', 0)
        features[1] = min(np.log1p(iat * 1000) / 10, 1.0)  # Convert to ms, log, cap
        
        # Feature 2: port_number (normalized)
        features[2] = packet.get('dst_port', 0) / self.max_port
        
        # Feature 3: protocol_encoded (one-hot would be better, but we'll use encoding)
        protocol = packet.get('protocol', 6)
        if protocol == 6:  # TCP
            features[3] = 0.0
        elif protocol == 17:  # UDP
            features[3] = 0.5
        elif protocol == 1:  # ICMP
            features[3] = 1.0
        else:
            features[3] = 0.2
        
        # Feature 4: packets_per_second (log normalized)
        pps = packet.get('packets_per_second', 0)
        features[4] = min(np.log1p(pps) / 10, 1.0)
        
        # Feature 5: bytes_per_second (log normalized)
        bps = packet.get('bytes_per_second', 0)
        features[5] = min(np.log1p(bps) / 20, 1.0)
        
        # Feature 6: src_port (normalized)
        features[6] = packet.get('src_port', 0) / self.max_port
        
        # Feature 7: dst_port (normalized)
        features[7] = packet.get('dst_port', 0) / self.max_port
        
        # Features 8-11: TCP flags
        flags = packet.get('flags', {})
        features[8] = 1.0 if flags.get('syn', False) else 0.0  # flag_syn
        features[9] = 1.0 if flags.get('ack', False) else 0.0  # flag_ack
        features[10] = 1.0 if flags.get('fin', False) else 0.0  # flag_fin
        features[11] = 1.0 if flags.get('rst', False) else 0.0  # flag_rst
        
        # Feature 12: connection_duration (normalized)
        duration = packet.get('connection_duration', 0)
        features[12] = min(duration / self.max_duration, 1.0)
        
        return features
    
    def extract_batch(self, packets: List[Dict]) -> np.ndarray:
        """Extract features for multiple packets"""
        return np.array([self.extract(p) for p in packets])
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names"""
        return self.feature_names.copy()

# Example usage
if __name__ == "__main__":
    from traffic_simulator import TrafficSimulator
    
    simulator = TrafficSimulator()
    extractor = FeatureExtractor()
    
    # Test extraction
    packet = simulator.generate_packet()
    features = extractor.extract(packet)
    
    print("Packet:", packet['attack_type'] or 'normal')
    print("Features:", features)
    print("Feature names:", extractor.get_feature_names())
