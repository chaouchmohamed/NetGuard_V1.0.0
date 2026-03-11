from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import random
from datetime import datetime

# Create a minimal test app
app = FastAPI()

# Allow all CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/test")
async def test_websocket(websocket: WebSocket):
    print("🔵 Test WebSocket connection attempt...")
    await websocket.accept()
    print("✅ Test WebSocket accepted!")
    
    try:
        count = 0
        while True:
            count += 1
            await websocket.send_json({
                "message": f"Test message {count}",
                "time": datetime.now().isoformat()
            })
            await asyncio.sleep(1)
    except Exception as e:
        print(f"❌ Test WebSocket error: {e}")

@app.get("/")
async def root():
    return {"status": "Test server running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
