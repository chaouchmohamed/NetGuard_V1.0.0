#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ---------------------------------------------------------------------------
# Paths & logging
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("netguard")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="NetGuard API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load ML model
# ---------------------------------------------------------------------------
from models.isolation_forest import AnomalyDetector
from core.feature_extractor import FeatureExtractor
from core.alert_manager import AlertManager
from database.db import init_db
from api.routes import router, set_global_model, set_global_alert_manager

model = AnomalyDetector()
feature_extractor = FeatureExtractor()
alert_manager = AlertManager()

MODEL_PATH = BASE_DIR / "models" / "detector.pkl"

def load_model():
    global model
    if MODEL_PATH.exists():
        try:
            model.load(str(MODEL_PATH))
            logger.info(f"✅ Model loaded from {MODEL_PATH}")
        except Exception as e:
            logger.warning(f"Could not load model ({e}). Will train on first batch.")
    else:
        logger.warning("No saved model found. Run train_model.py first, or the system will train on live data.")

# ---------------------------------------------------------------------------
# Real traffic sniffer
# ---------------------------------------------------------------------------
from traffic_sniffer import RealTrafficSniffer

# Set your interface here, or leave None for scapy's default.
# Examples: 'eth0', 'wlan0', 'ens33', 'lo'
INTERFACE = os.getenv("NETGUARD_INTERFACE", None)

sniffer = RealTrafficSniffer(interface=INTERFACE)

# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    init_db()
    load_model()
    set_global_model(model)
    set_global_alert_manager(alert_manager)
    sniffer.start()
    logger.info("🚀 NetGuard started — sniffing real traffic")

@app.on_event("shutdown")
async def shutdown():
    sniffer.stop()
    logger.info("NetGuard stopped")

# ---------------------------------------------------------------------------
# Include REST routes
# ---------------------------------------------------------------------------
app.include_router(router)

# ---------------------------------------------------------------------------
# WebSocket — real traffic feed
# ---------------------------------------------------------------------------
@app.websocket("/ws/traffic")
async def websocket_traffic(websocket: WebSocket):
    logger.info(f"WebSocket connection from {websocket.client}")
    await websocket.accept()

    total_packets = 0
    total_anomalies = 0

    try:
        while True:
            # Pull next packet from the sniffer queue
            packet = sniffer.get_packet()

            if packet is None:
                # No packet yet — yield control and try again shortly
                await asyncio.sleep(0.05)
                continue

            total_packets += 1

            # Run ML inference
            prediction = {"is_anomaly": False, "anomaly_score": 0.0, "confidence": 0.0}
            if model.is_trained:
                try:
                    features = feature_extractor.extract(packet)
                    prediction = model.predict(features)
                except Exception as e:
                    logger.debug(f"Prediction error: {e}")

            # Annotate packet with ML result
            packet["is_anomaly"] = prediction["is_anomaly"]
            packet["anomaly_score"] = prediction.get("anomaly_score", 0.0)
            packet["confidence"] = prediction.get("confidence", 0.0)

            # Classify attack type from model score (heuristic)
            if prediction["is_anomaly"]:
                total_anomalies += 1
                packet["attack_type"] = _classify_attack(packet)
                alert_manager.process_alert(packet, prediction)

            # Build WebSocket message (same shape as before)
            message = {
                "type": "packet",
                "packet": packet,
                "stats": {
                    "total_packets": total_packets,
                    "total_anomalies": total_anomalies,
                    "anomaly_rate": round((total_anomalies / total_packets) * 100, 2),
                    "packets_per_second": packet.get("packets_per_second", 0),
                    "bytes_per_second": packet.get("bytes_per_second", 0),
                },
            }

            await websocket.send_json(message)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


def _classify_attack(packet: dict) -> str:
    """
    Heuristic attack classification based on packet features.
    Replace with a proper classifier if you have labelled data.
    """
    flags = packet.get("flags", {})
    dst_port = packet.get("dst_port", 0)
    pps = packet.get("packets_per_second", 0)
    packet_size = packet.get("packet_size", 0)

    if flags.get("syn") and not flags.get("ack") and pps > 100:
        return "syn_flood"
    if pps > 500:
        return "ddos"
    if dst_port in (22, 3389) and pps > 10:
        return "brute_force"
    if packet_size > 10000:
        return "data_exfiltration"
    if flags.get("syn") and not flags.get("ack"):
        return "port_scan"

    return "unknown_anomaly"


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "running", "message": "NetGuard — Real Traffic Mode"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mode": "real_traffic",
        "interface": INTERFACE or "default",
        "model_loaded": model.is_trained,
        "packets_captured": sniffer.packet_count,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,   # reload=True breaks scapy's background thread
    )