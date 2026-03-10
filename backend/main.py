#!/usr/bin/env python3
"""
NetGuard - Network Attack Detection System
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import sys
from pathlib import Path
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from api.routes import router, set_global_model as set_routes_model, set_global_alert_manager as set_routes_alert
from api.websocket import websocket_endpoint, set_global_model as set_ws_model, set_global_alert_manager as set_ws_alert
from models.isolation_forest import AnomalyDetector
from models.train_model import main as train_model
from core.alert_manager import AlertManager
from database.db import init_db
from utils.logger import setup_logger

# Setup logging
logger = setup_logger('netguard', 'logs/netguard.log')

# Initialize FastAPI app
app = FastAPI(
    title="NetGuard - Network Attack Detection System",
    description="Real-time network attack detection using Isolation Forest",
    version="1.0.0"
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
model = None
alert_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    global model, alert_manager
    
    logger.info("Starting NetGuard...")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Initialize alert manager
    logger.info("Initializing alert manager...")
    alert_manager = AlertManager(max_alerts=1000)
    
    # Check if model exists, if not train it
    model_path = Path(__file__).parent / "models" / "detector.pkl"
    
    if model_path.exists():
        logger.info(f"Loading existing model from {model_path}")
        model = AnomalyDetector()
        model.load(str(model_path))
    else:
        logger.info("No trained model found. Training new model...")
        try:
            train_model()
            if model_path.exists():
                model = AnomalyDetector()
                model.load(str(model_path))
                logger.info("Model trained and loaded successfully")
            else:
                logger.error("Model training failed: model file not created")
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
    
    # Set global model references
    set_routes_model(model)
    set_ws_model(model)
    set_routes_alert(alert_manager)
    set_ws_alert(alert_manager)
    
    logger.info("NetGuard startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down NetGuard...")

# Include routers
app.include_router(router)

# WebSocket endpoint
@app.websocket("/ws/traffic")
async def websocket_traffic(websocket):
    await websocket_endpoint(websocket)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "NetGuard API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "websocket": "/ws/traffic"
        }
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None and model.is_trained if model else False
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )