from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
import random
from datetime import datetime

# Global instances (simplified)
model = None
alert_manager = None

def set_global_model(model_instance):
    global model
    model = model_instance

def set_global_alert_manager(manager_instance):
    global alert_manager
    alert_manager = manager_instance

async def websocket_endpoint(websocket: WebSocket):
    print("="*50)
    print("🔥 WEBSOCKET ENDPOINT HIT!")
    print(f"📡 Client: {websocket.client}")
    print("="*50)
    
    # Try to accept immediately
    try:
        print("🟡 Attempting to accept connection...")
        await websocket.accept()
        print("✅ CONNECTION ACCEPTED!")
    except Exception as e:
        print(f"❌ ACCEPT FAILED: {e}")
        return
    
    # Send test messages
    count = 0
    try:
        while True:
            count += 1
            test_message = {
                "type": "packet",
                "packet": {
                    "id": f"test_{count}",
                    "timestamp": datetime.now().isoformat(),
                    "src_ip": f"192.168.1.{random.randint(2,254)}",
                    "dst_ip": f"10.0.0.{random.randint(2,254)}",
                    "attack_type": random.choice([None, 'ddos', 'port_scan']) if random.random() > 0.7 else None
                }
            }
            await websocket.send_json(test_message)
            print(f"📤 Sent test message {count}")
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("❌ Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")