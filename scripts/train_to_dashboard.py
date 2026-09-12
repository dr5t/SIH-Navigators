import requests
import json
import os

BACKEND_URL = "http://localhost:8000/api/v1/ml/registry"

def push_metrics_to_dashboard(version: str, dataset_name: str, mae: float, rmse: float, status: str = "TRAINING"):
    """
    Pushes model metrics to the backend dashboard.
    If backend is unavailable, logs the limitation as required by the prompt.
    """
    print(f"Pushing model {version} metrics to dashboard...")
    payload = {
        "version": version,
        "dataset": dataset_name,
        "mae": mae,
        "rmse": rmse,
        "status": status
    }
    
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=2.0)
        if response.status_code == 200:
            print("Successfully pushed to Model Registry.")
        else:
            print(f"Registry returned status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print("\n==================================================")
        print("WARNING: BACKEND DASHBOARD UNAVAILABLE")
        print("==================================================")
        print("The FastAPI backend is not running or unreachable.")
        print("Model metrics could not be pushed to the registry.")
        print(f"Payload: {json.dumps(payload)}")
        print("Please start the backend server to enable registry syncing.")

if __name__ == "__main__":
    # Test payload
    push_metrics_to_dashboard("v2.1", "IO-VNBD-Local", 0.5, 0.7, "VALIDATION")
