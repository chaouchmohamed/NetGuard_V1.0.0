#!/usr/bin/env python3
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import random
from datetime import datetime

# Create FastAPI app
app = FastAPI(title="NetGuard API", version="1.0.0")

# CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SIMPLE WEBSOCKET - exactly like the test
@app.websocket("/ws/traffic")
async def websocket_traffic(websocket: WebSocket):
    print("🔵 WebSocket attempt received!")
    try:
        await websocket.accept()
        print("✅ Connection accepted!")
        
        count = 0
        while True:
            count += 1
            
            # Simple packet
            packet = {
                "type": "packet",
                "packet": {
                    "id": f"pkt_{count}",
                    "timestamp": datetime.now().isoformat(),
                    "src_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
                    "dst_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
                    "attack_type": random.choice([None, 'ddos', 'port_scan']) if random.random() > 0.7 else None
                },
                "stats": {
                    "total_packets": count,
                    "total_anomalies": count // 3,
                    "anomaly_rate": 33.3
                }
            }
            
            await websocket.send_json(packet)
            print(f"📤 Sent packet {count}")
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Simple routes
@app.get("/")
async def root():
    return {"status": "running", "message": "NetGuard API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "database": "healthy", "model_loaded": True}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )