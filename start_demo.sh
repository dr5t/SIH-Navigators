#!/usr/bin/env bash
# Navigators - SIH Demo Startup Script

echo "=================================================="
echo "    Navigators: AI/ML Intelligent Dead Reckoning  "
echo "    SIH26168 - Demo Initialization                "
echo "=================================================="

# Ensure virtual environment is active
if [[ -z "${VIRTUAL_ENV}" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "[ERROR] Virtual environment not found. Run 'python3 -m venv venv && source venv/bin/activate && pip install fastapi httpx pydantic uvicorn'"
        exit 1
    fi
fi

# Ensure uvicorn is installed for serving the backend
pip install -q uvicorn

# Start FastAPI backend in the background
echo "[INFO] Starting FastAPI Backend on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to initialize
sleep 2

# Start Python HTTP Server for Dashboard in the background
echo "[INFO] Starting Dashboard on port 8080..."
cd dashboard && python3 -m http.server 8080 &
DASHBOARD_PID=$!
cd ..

# Run a simulation run to populate the backend with data
echo "[INFO] Running End-to-End Showcase Demo (Phase 19)..."
PYTHONPATH=. python3 scripts/run_demo_scenario.py

echo "=================================================="
echo "    SYSTEM ONLINE                                 "
echo "    Dashboard: http://localhost:8080/             "
echo "    API Docs:  http://localhost:8000/docs         "
echo "=================================================="
echo "Press Ctrl+C to stop all services."

# Trap SIGINT to kill background processes
trap "echo 'Shutting down services...'; kill $BACKEND_PID $DASHBOARD_PID; exit" SIGINT SIGTERM

# Wait indefinitely
wait
