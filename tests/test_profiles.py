from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cloud.main import app

client = TestClient(app)
dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature"
headers = {"Authorization": f"Bearer {dummy_token}"}

def test_create_and_fetch_profile():
    # 1. Create a profile
    create_payload = {
        "name": "Test Car",
        "vehicle_type": "CAR",
        "phone_mounting": "DASHBOARD",
        "external_imu": False,
        "nav_prefs": {"avoid_tolls": True}
    }
    response = client.post("/profiles", json=create_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Car"
    assert data["is_calibrated"] == False
    profile_id = data["id"]
    
    # 2. Fetch profiles and verify
    response = client.get("/profiles", headers=headers)
    assert response.status_code == 200
    profiles = response.json()
    assert len([p for p in profiles if p["id"] == profile_id]) == 1
    
    # 3. Update profile to be calibrated
    update_payload = {
        "is_calibrated": True
    }
    response = client.put(f"/profiles/{profile_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["is_calibrated"] == True
    
    # 4. Delete profile
    response = client.delete(f"/profiles/{profile_id}", headers=headers)
    assert response.status_code == 200
    
    # 5. Verify deletion
    response = client.get("/profiles", headers=headers)
    assert response.status_code == 200
    profiles = response.json()
    assert len([p for p in profiles if p["id"] == profile_id]) == 0

if __name__ == "__main__":
    test_create_and_fetch_profile()
    print("Profile tests passed!")
