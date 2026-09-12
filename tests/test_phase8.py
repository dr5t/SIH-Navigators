import unittest
from fastapi.testclient import TestClient
from backend.main import app, db

client = TestClient(app)

class TestPhase8(unittest.TestCase):
    def setUp(self):
        # Clear DB before each test
        db.clear()

    def test_sync_and_retrieve_session(self):
        payload = {
            "session_id": "sess_123",
            "device_id": "dev_456",
            "trajectory": [
                {
                    "timestamp": 1690000000.0,
                    "lat": 37.7,
                    "lon": -122.4,
                    "alt": 10.0,
                    "speed": 15.0,
                    "heading": 90.0
                }
            ]
        }
        
        # 1. Sync
        response = client.post("/api/v1/sync", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # 2. List
        list_resp = client.get("/api/v1/sessions")
        self.assertEqual(list_resp.status_code, 200)
        self.assertIn("sess_123", list_resp.json()["sessions"])
        
        # 3. Retrieve
        get_resp = client.get("/api/v1/sessions/sess_123")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["device_id"], "dev_456")

if __name__ == '__main__':
    unittest.main()
