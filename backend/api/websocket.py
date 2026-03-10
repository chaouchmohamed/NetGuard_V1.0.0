from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
import json
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.traffic_simulator import TrafficSimulator
from core.feature_extractor import FeatureExtractor
from core.alert_manager import AlertManager
from models.isolation_forest import AnomalyDetector
from database import SessionLocal
from database.models import TrafficLog, Alert
import numpy as np

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stats = {
            "total_packets": 0,
            "total_anomalies": 0,
            "attack_type_counts": {},
            "packets_per_second_current": 0
        }
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        print(f"✅ WebSocket connected from {websocket.client.host}:{websocket.client.port}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
            print(f"❌ WebSocket disconnected")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    def update_stats(self, packet: Dict, is_anomaly: bool, attack_type: str = None):
        """Update connection statistics"""
        self.stats["total_packets"] += 1
        if is_anomaly:
            self.stats["total_anomalies"] += 1
            if attack_type:
                self.stats["attack_type_counts"][attack_type] = \
                    self.stats["attack_type_counts"].get(attack_type, 0) + 1

manager = ConnectionManager()

# Global instances (will be set in main.py)
traffic_simulator = TrafficSimulator()
feature_extractor = FeatureExtractor()
model: AnomalyDetector = None
alert_manager: AlertManager = None

def set_global_model(model_instance):
    """Set the global model reference"""
    global model
    model = model_instance

def set_global_alert_manager(manager_instance):
    """Set the global alert manager reference"""
    global alert_manager
    alert_manager = manager_instance

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time traffic streaming"""
    await manager.connect(websocket)
    
    try:
        db = SessionLocal()
        packet_count = 0
        
        while True:
            try:
                # Generate packet
                packet = traffic_simulator.generate_packet()
                packet_count += 1
                
                # Extract features and predict
                features = feature_extractor.extract(packet)
                
                if model and model.is_trained:
                    prediction = model.predict(features.reshape(1, -1))
                else:
                    # Fallback if model not trained
                    prediction = {
                        "is_anomaly": packet.get('attack_type') is not None,
                        "anomaly_score": 0.8 if packet.get('attack_type') else 0.1,
                        "confidence": 0.85,
                        "raw_score": 0
                    }
                
                # Override is_anomaly if attack_type is set
                is_anomaly = prediction["is_anomaly"] or packet.get('attack_type') is not None
                
                # Classify severity if anomaly
                severity = None
                if is_anomaly and alert_manager:
                    severity = alert_manager.classify_severity(
                        prediction["anomaly_score"],
                        packet.get('attack_type')
                    )
                
                # Save to database if anomaly
                if is_anomaly:
                    # Save traffic log
                    traffic_log = TrafficLog(
                        packet_id=packet['id'],
                        timestamp_epoch=packet['timestamp_epoch'],
                        src_ip=packet['src_ip'],
                        dst_ip=packet['dst_ip'],
                        src_port=packet['src_port'],
                        dst_port=packet['dst_port'],
                        protocol=packet['protocol'],
                        protocol_name=packet['protocol_name'],
                        packet_size=packet['packet_size'],
                        ttl=packet['ttl'],
                        flags_syn=packet['flags'].get('syn', False),
                        flags_ack=packet['flags'].get('ack', False),
                        flags_fin=packet['flags'].get('fin', False),
                        flags_rst=packet['flags'].get('rst', False),
                        inter_arrival_time=packet['inter_arrival_time'],
                        packets_per_second=packet['packets_per_second'],
                        bytes_per_second=packet['bytes_per_second'],
                        connection_duration=packet['connection_duration'],
                        attack_type=packet.get('attack_type'),
                        is_anomaly=True,
                        anomaly_score=prediction["anomaly_score"],
                        raw_data=packet
                    )
                    db.add(traffic_log)
                    
                    # Create and save alert
                    if alert_manager:
                        alert_dict = alert_manager.create_alert(packet, prediction)
                        alert = Alert(
                            alert_id=alert_dict['id'],
                            timestamp_epoch=alert_dict['timestamp_epoch'],
                            severity=alert_dict['severity'],
                            attack_type=alert_dict['attack_type'],
                            source_ip=alert_dict['source_ip'],
                            destination_ip=alert_dict['destination_ip'],
                            source_port=alert_dict['source_port'],
                            destination_port=alert_dict['destination_port'],
                            protocol=alert_dict['protocol'],
                            packet_size=alert_dict['packet_size'],
                            anomaly_score=alert_dict['anomaly_score'],
                            confidence=alert_dict['confidence'],
                            description=alert_dict['description'],
                            raw_packet=packet
                        )
                        db.add(alert)
                        db.commit()
                        print(f"⚠️ Alert created: {severity} - {packet.get('attack_type', 'unknown')}")
                
                # Update connection stats
                manager.update_stats(packet, is_anomaly, packet.get('attack_type'))
                
                # Prepare message for clients
                message = {
                    "type": "packet",
                    "packet": packet,
                    "prediction": {
                        "is_anomaly": is_anomaly,
                        "anomaly_score": prediction["anomaly_score"],
                        "confidence": prediction.get("confidence", 0.85),
                        "severity": severity,
                        "attack_type": packet.get('attack_type')
                    },
                    "stats": {
                        "total_packets": manager.stats["total_packets"],
                        "total_anomalies": manager.stats["total_anomalies"],
                        "anomaly_rate": (manager.stats["total_anomalies"] / max(manager.stats["total_packets"], 1)) * 100,
                        "attack_type_counts": manager.stats["attack_type_counts"],
                        "packets_per_second_current": packet['packets_per_second']
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                # Broadcast to all clients
                if manager.active_connections:
                    await manager.broadcast(message)
                    if packet_count % 10 == 0:
                        print(f"📊 Broadcasted {packet_count} packets")
                
                # Control rate (approx 2 packets per second)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in packet generation loop: {str(e)}")
                print(f"❌ Error: {e}")
                await asyncio.sleep(1)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        db.close()