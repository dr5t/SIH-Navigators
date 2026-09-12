# docker/backend.Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn gunicorn

# Copy application code
COPY cloud/ ./cloud/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Start server using Uvicorn (FastAPI)
CMD ["uvicorn", "cloud.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
