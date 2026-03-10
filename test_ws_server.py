from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
import json
from datetime import datetime

app = FastAPI()

@app.websocket("/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected!")
    try:
        while True:
            # Send a test message every second
            data = {
                "timestamp": datetime.now().isoformat(),
                "message": "test",
                "counter": 0
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

