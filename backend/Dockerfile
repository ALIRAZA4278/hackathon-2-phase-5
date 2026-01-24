# =============================================================================
# Backend Dockerfile for Kubernetes Deployment
# Base: python:3.11-slim (explicit tag, no latest)
# Port: 8000 (standard FastAPI port for K8s)
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Kubernetes deployment uses port 8000
EXPOSE 8000

# Health check endpoint for Kubernetes probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the FastAPI server on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
