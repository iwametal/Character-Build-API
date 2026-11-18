# ==============================================================================
# Dockerfile: Character Build API v2 (Multi-instance / Containerized)
# ==============================================================================
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=1

# Install curl for container health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Set working directory and create data directory for persistent SQLite
WORKDIR /app
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Copy dependency manifest and install dependencies
COPY src/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code and files
COPY src /app/src
COPY files /app/files
RUN chown -R appuser:appgroup /app

# Run as non-root user for security in Docker & Kubernetes
USER appuser

# Expose internal API port
EXPOSE 8000

# Docker healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command to run FastAPI with Uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
