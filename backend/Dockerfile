# =============================================================================
# Backend Dockerfile for Kubernetes Deployment (Multi-stage)
# Base: python:3.11-slim (explicit tag, no latest)
# Port: 8000 (standard FastAPI port for K8s)
# =============================================================================

# Build stage - Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage - Minimal production image
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Switch to non-root user
USER appuser

# Kubernetes deployment uses port 8000
EXPOSE 8000

# Health check endpoint for Kubernetes probes
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the FastAPI server on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
