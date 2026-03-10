from typing import Dict, List, Optional, Deque
from collections import deque
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alerts, severity classification, and alert history"""
    
    SEVERITY_LEVELS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    # Attack type to base severity mapping
    ATTACK_SEVERITY = {
        'ddos': 'HIGH',
        'port_scan': 'MEDIUM',
        'syn_flood': 'HIGH',
        'brute_force': 'MEDIUM',
        'data_exfiltration': 'CRITICAL'
    }
    
    def __init__(self, max_alerts: int = 100):
        """
        Initialize alert manager
        
        Args:
            max_alerts: Maximum number of alerts to keep in memory
        """
        self.alerts: Deque[Dict] = deque(maxlen=max_alerts)
        self.alert_count = 0
        self.severity_counts = {level: 0 for level in self.SEVERITY_LEVELS}
        self.attack_type_counts = {}
        
    def classify_severity(self, anomaly_score: float, attack_type: Optional[str] = None) -> str:
        """
        Classify alert severity based on anomaly score and attack type
        
        Args:
            anomaly_score: Normalized anomaly score (0-1)
            attack_type: Type of attack detected
            
        Returns:
            Severity level string
        """
        # Base severity on attack type if available
        if attack_type and attack_type in self.ATTACK_SEVERITY:
            base_severity = self.ATTACK_SEVERITY[attack_type]
            base_score = self.SEVERITY_LEVELS.index(base_severity) / (len(self.SEVERITY_LEVELS) - 1)
        else:
            base_score = 0.5
        
        # Combine with anomaly score
        combined_score = (anomaly_score * 0.7) + (base_score * 0.3)
        
        # Map to severity level
        if combined_score < 0.3:
            return 'LOW'
        elif combined_score < 0.5:
            return 'MEDIUM'
        elif combined_score < 0.8:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def create_alert(self, packet: Dict, prediction: Dict) -> Dict:
        """
        Create an alert from packet and prediction
        
        Args:
            packet: Packet dictionary
            prediction: Prediction result from model
            
        Returns:
            Alert dictionary
        """
        attack_type = packet.get('attack_type')
        anomaly_score = prediction.get('anomaly_score', 0)
        confidence = prediction.get('confidence', 0)
        
        severity = self.classify_severity(anomaly_score, attack_type)
        
        alert = {
            'id': f"alert_{self.alert_count}_{packet['id']}",
            'timestamp': datetime.now().isoformat(),
            'timestamp_epoch': packet.get('timestamp_epoch', datetime.now().timestamp()),
            'severity': severity,
            'attack_type': attack_type,
            'source_ip': packet.get('src_ip'),
            'destination_ip': packet.get('dst_ip'),
            'source_port': packet.get('src_port'),
            'destination_port': packet.get('dst_port'),
            'protocol': packet.get('protocol_name'),
            'packet_size': packet.get('packet_size'),
            'anomaly_score': anomaly_score,
            'confidence': confidence,
            'description': self._generate_description(packet, attack_type, severity),
            'raw_packet': packet,
            'acknowledged': False,
            'mitigated': False
        }
        
        # Update counts
        self.alerts.append(alert)
        self.alert_count += 1
        self.severity_counts[severity] = self.severity_counts.get(severity, 0) + 1
        
        if attack_type:
            self.attack_type_counts[attack_type] = self.attack_type_counts.get(attack_type, 0) + 1
        
        logger.info(f"Alert created: {severity} - {attack_type or 'unknown'} from {packet.get('src_ip')}")
        
        return alert
    
    def _generate_description(self, packet: Dict, attack_type: Optional[str], severity: str) -> str:
        """Generate human-readable alert description"""
        if attack_type:
            descriptions = {
                'ddos': f"Potential DDoS attack detected: High volume traffic from {packet.get('src_ip')} to {packet.get('dst_ip')}",
                'port_scan': f"Port scan detected: {packet.get('src_ip')} scanning port {packet.get('dst_port')}",
                'syn_flood': f"SYN flood attack: Repeated SYN packets from {packet.get('src_ip')}",
                'brute_force': f"Brute force attempt: Multiple connections to {packet.get('dst_port')} from {packet.get('src_ip')}",
                'data_exfiltration': f"Possible data exfiltration: Large packet ({packet.get('packet_size')} bytes) to unusual port"
            }
            return descriptions.get(attack_type, f"Anomalous traffic detected from {packet.get('src_ip')}")
        else:
            return f"Anomaly detected: {packet.get('src_ip')} -> {packet.get('dst_ip')} (score: {packet.get('anomaly_score', 0):.2f})"
    
    def get_recent_alerts(self, count: int = 20) -> List[Dict]:
        """Get most recent alerts"""
        return list(self.alerts)[-count:]
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict]:
        """Get alerts filtered by severity"""
        return [a for a in self.alerts if a['severity'] == severity]
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics"""
        return {
            'total_alerts': self.alert_count,
            'alerts_in_memory': len(self.alerts),
            'severity_counts': self.severity_counts,
            'attack_type_counts': self.attack_type_counts,
            'critical_percentage': (self.severity_counts.get('CRITICAL', 0) / max(self.alert_count, 1)) * 100
        }
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                return True
        return False
    
    def clear_alerts(self):
        """Clear all alerts from memory"""
        self.alerts.clear()
        self.severity_counts = {level: 0 for level in self.SEVERITY_LEVELS}
        self.attack_type_counts = {}
        logger.info("All alerts cleared")

# Example usage
if __name__ == "__main__":
    from traffic_simulator import TrafficSimulator
    
    simulator = TrafficSimulator()
    manager = AlertManager()
    
    # Test alert creation
    for i in range(10):
        packet = simulator.generate_packet()
        prediction = {
            'is_anomaly': True,
            'anomaly_score': 0.7 + (i * 0.03),
            'confidence': 0.85
        }
        
        alert = manager.create_alert(packet, prediction)
        print(f"Alert {i+1}: {alert['severity']} - {alert['description']}")
    
    print("\nStatistics:", manager.get_alert_statistics())
