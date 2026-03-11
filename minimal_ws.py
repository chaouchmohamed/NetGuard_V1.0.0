from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

# Create the absolute minimal app
app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple WebSocket endpoint - nothing else
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("🔵 WebSocket attempt received!")
    try:
        await websocket.accept()
        print("✅ Connection accepted!")
        await websocket.send_text("Connected!")
        
        count = 0
        while True:
            count += 1
            await websocket.send_json({"message": f"test {count}"})
            await asyncio.sleep(1)
    except Exception as e:
        print(f"❌ Error: {e}")

@app.get("/")
async def root():
    return {"message": "Test server running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9999)
