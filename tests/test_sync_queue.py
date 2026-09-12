import asyncio
import websockets
import json
import threading
import time
import requests
import uvicorn
from cloud.main import app

# This test spins up the FastAPI server in a thread and tests pushing telemetry
# and receiving it via websocket

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def test_cloud_sync_pipeline():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2) # Wait for server to boot

    async def listen_ws():
        async with websockets.connect("ws://127.0.0.1:8000/telemetry/live") as ws:
            # Tell the background thread to send the post request NOW
            threading.Thread(target=send_post, daemon=True).start()
            
            # Wait for data
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            assert data["type"] == "telemetry_batch"
            assert data["session_id"] == "test_session_xyz"
            assert len(data["data"]) == 2
            print("WebSocket received correct broadcast!")

    def send_post():
        batch = [
            {"timestamp": 1000, "lat": 12.0, "lon": 13.0, "speed": 10.5, "mode": "GNSS + INS"},
            {"timestamp": 1001, "lat": 12.0001, "lon": 13.0, "speed": 11.0, "mode": "GNSS + INS"}
        ]
        time.sleep(1) # Give WS a moment to register
        print("Sending POST request from mocked Android worker...")
        res = requests.post("http://127.0.0.1:8000/telemetry/batch?session_id=test_session_xyz", json=batch)
        assert res.status_code == 200
        print(f"Server response: {res.json()}")

    asyncio.run(listen_ws())
    print("Cloud sync pipeline test passed!")

if __name__ == "__main__":
    test_cloud_sync_pipeline()
