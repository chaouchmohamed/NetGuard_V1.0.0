from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db, SessionLocal
from database.models import TrafficLog, Alert
from models.isolation_forest import AnomalyDetector
from core.alert_manager import AlertManager
import subprocess
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Global model reference (will be set in main.py)
model: Optional[AnomalyDetector] = None
alert_manager: Optional[AlertManager] = None

def set_global_model(model_instance):
    """Set the global model reference"""
    global model
    model = model_instance

def set_global_alert_manager(manager_instance):
    """Set the global alert manager reference"""
    global alert_manager
    alert_manager = manager_instance

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database
        db.execute("SELECT 1").first()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "model_loaded": model is not None and model.is_trained if model else False,
        "model_path": str(Path(__file__).parent.parent / "models" / "detector.pkl")
    }

@router.get("/alerts")
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    attack_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated alerts with optional filters"""
    query = db.query(Alert)
    
    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if attack_type:
        query = query.filter(Alert.attack_type == attack_type)
    
    total = query.count()
    alerts = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "alerts": [alert.to_dict() for alert in alerts]
    }

@router.get("/alerts/recent")
async def get_recent_alerts(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Get most recent alerts"""
    alerts = db.query(Alert).order_by(desc(Alert.timestamp)).limit(limit).all()
    return [alert.to_dict() for alert in alerts]

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    # Time ranges
    now = datetime.now()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    
    # Basic counts
    total_packets = db.query(func.count(TrafficLog.id)).scalar() or 0
    total_anomalies = db.query(func.count(TrafficLog.id)).filter(TrafficLog.is_anomaly == True).scalar() or 0
    
    # Hourly stats
    packets_last_hour = db.query(func.count(TrafficLog.id)).filter(TrafficLog.timestamp >= last_hour).scalar() or 0
    anomalies_last_hour = db.query(func.count(TrafficLog.id)).filter(
        TrafficLog.timestamp >= last_hour,
        TrafficLog.is_anomaly == True
    ).scalar() or 0
    
    # Alert stats
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    alerts_by_severity = db.query(
        Alert.severity,
        func.count(Alert.id).label('count')
    ).group_by(Alert.severity).all()
    
    # Attack type distribution
    attack_types = db.query(
        TrafficLog.attack_type,
        func.count(TrafficLog.id).label('count')
    ).filter(
        TrafficLog.attack_type.isnot(None)
    ).group_by(TrafficLog.attack_type).all()
    
    # Top sources
    top_sources = db.query(
        TrafficLog.src_ip,
        func.count(TrafficLog.id).label('count')
    ).group_by(TrafficLog.src_ip).order_by(desc('count')).limit(10).all()
    
    # Top destinations
    top_destinations = db.query(
        TrafficLog.dst_ip,
        func.count(TrafficLog.id).label('count')
    ).group_by(TrafficLog.dst_ip).order_by(desc('count')).limit(10).all()
    
    return {
        "time_range": {
            "last_hour": last_hour.isoformat(),
            "last_24h": last_24h.isoformat()
        },
        "packets": {
            "total": total_packets,
            "last_hour": packets_last_hour,
            "anomalies_total": total_anomalies,
            "anomalies_last_hour": anomalies_last_hour,
            "anomaly_rate": (total_anomalies / max(total_packets, 1)) * 100
        },
        "alerts": {
            "total": total_alerts,
            "by_severity": {sev: count for sev, count in alerts_by_severity}
        },
        "attack_types": {atype: count for atype, count in attack_types if atype},
        "top_sources": [{"ip": ip, "count": count} for ip, count in top_sources],
        "top_destinations": [{"ip": ip, "count": count} for ip, count in top_destinations]
    }

@router.get("/traffic/history")
async def get_traffic_history(
    limit: int = Query(500, ge=1, le=5000),
    anomaly_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get recent traffic history"""
    query = db.query(TrafficLog)
    if anomaly_only:
        query = query.filter(TrafficLog.is_anomaly == True)
    
    packets = query.order_by(desc(TrafficLog.timestamp)).limit(limit).all()
    return [p.to_dict() for p in packets]

@router.post("/model/retrain")
async def retrain_model(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger model retraining"""
    global model
    
    def train_task():
        try:
            logger.info("Starting model retraining...")
            # Run training script
            script_path = Path(__file__).parent.parent / "models" / "train_model.py"
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Model retrained successfully")
                # Reload model
                model_path = Path(__file__).parent.parent / "models" / "detector.pkl"
                if model_path.exists():
                    new_model = AnomalyDetector()
                    new_model.load(str(model_path))
                    model = new_model
                    logger.info("New model loaded")
            else:
                logger.error(f"Training failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error during retraining: {str(e)}")
    
    background_tasks.add_task(train_task)
    return {"message": "Model retraining started", "status": "processing"}

@router.get("/model/info")
async def get_model_info():
    """Get model metadata and information"""
    global model
    
    if not model or not model.is_trained:
        return {"status": "not_trained", "message": "Model not trained yet"}
    
    model_path = Path(__file__).parent.parent / "models" / "detector.pkl"
    model_stats = {}
    
    if model_path.exists():
        model_stats = {
            "path": str(model_path),
            "size_bytes": model_path.stat().st_size,
            "modified": datetime.fromtimestamp(model_path.stat().st_mtime).isoformat()
        }
    
    return {
        "status": "loaded",
        "is_trained": model.is_trained,
        "contamination": model.contamination,
        "n_estimators": model.n_estimators,
        "feature_names": model.feature_names,
        "file_info": model_stats
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """Mark an alert as acknowledged"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    db.commit()
    
    return {"message": "Alert acknowledged", "alert_id": alert_id}

@router.delete("/alerts/clear")
async def clear_alerts(db: Session = Depends(get_db)):
    """Clear all alerts (for testing/demo purposes)"""
    try:
        db.query(Alert).delete()
        db.commit()
        return {"message": "All alerts cleared", "count": db.query(Alert).count()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Initialize routes
def init_routes(app):
    app.include_router(router)
