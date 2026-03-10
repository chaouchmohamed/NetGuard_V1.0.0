from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from .db import Base
import json

class TrafficLog(Base):
    """Model for storing network traffic logs"""
    
    __tablename__ = "traffic_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    packet_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    timestamp_epoch = Column(Float)
    
    src_ip = Column(String, index=True)
    dst_ip = Column(String, index=True)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(Integer)
    protocol_name = Column(String)
    
    packet_size = Column(Integer)
    ttl = Column(Integer)
    
    flags_syn = Column(Boolean, default=False)
    flags_ack = Column(Boolean, default=False)
    flags_fin = Column(Boolean, default=False)
    flags_rst = Column(Boolean, default=False)
    
    inter_arrival_time = Column(Float)
    packets_per_second = Column(Float)
    bytes_per_second = Column(Float)
    connection_duration = Column(Float)
    
    attack_type = Column(String, nullable=True, index=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    
    raw_data = Column(JSON)  # Store full packet for reference
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_timestamp_attack', 'timestamp', 'attack_type'),
        Index('idx_src_dst', 'src_ip', 'dst_ip'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'packet_id': self.packet_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'src_port': self.src_port,
            'dst_port': self.dst_port,
            'protocol': self.protocol,
            'protocol_name': self.protocol_name,
            'packet_size': self.packet_size,
            'attack_type': self.attack_type,
            'is_anomaly': self.is_anomaly,
            'anomaly_score': self.anomaly_score
        }


class Alert(Base):
    """Model for storing security alerts"""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    timestamp_epoch = Column(Float)
    
    severity = Column(String, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    attack_type = Column(String, nullable=True, index=True)
    
    source_ip = Column(String, index=True)
    destination_ip = Column(String, index=True)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String)
    
    packet_size = Column(Integer)
    anomaly_score = Column(Float)
    confidence = Column(Float)
    
    description = Column(Text)
    raw_packet = Column(JSON)
    
    acknowledged = Column(Boolean, default=False)
    mitigated = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_severity_time', 'severity', 'timestamp'),
        Index('idx_alert_attack_time', 'attack_type', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.alert_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'severity': self.severity,
            'attack_type': self.attack_type,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'description': self.description,
            'anomaly_score': self.anomaly_score,
            'confidence': self.confidence,
            'acknowledged': self.acknowledged
        }
