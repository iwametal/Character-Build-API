"""Main application entrypoint for Character Build API v2.

Configures lifespan (database initialization + seed), CORS middleware,
RFC 9457 exception handlers, and registers all API routers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import os
import threading
import time
from typing import AsyncGenerator
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

try:
    import psutil
except ImportError:
    psutil = None

from src.api.database import init_db
from src.api.exceptions import register_exception_handlers
from src.api.routers import (
    abilities,
    armors,
    auth,
    body_parts,
    characters,
    elements,
    genders,
    jobs,
    magics,
    monsters,
    projects,
    races,
    rarities,
    status_effects,
    tasks,
    weapons,
)

# Instance and environment metadata
START_TIME = time.time()
INSTANCE_ID = (
    os.getenv("INSTANCE_ID")
    or os.getenv("POD_NAME")
    or os.getenv("HOSTNAME")
    or f"instance-{str(uuid.uuid4())[:8]}"
)
ENVIRONMENT = (
    os.getenv("ENVIRONMENT")
    or ("kubernetes" if os.getenv("KUBERNETES_SERVICE_HOST") else ("docker" if os.path.exists("/.dockerenv") else "standalone"))
)
POD_NAME = os.getenv("POD_NAME")
POD_IP = os.getenv("POD_IP")
NODE_NAME = os.getenv("NODE_NAME")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Execute database schema creation and seed on application startup."""
    init_db()
    yield


app = FastAPI(
    title="Character Build API",
    description=(
        "Character Build API v2 with SQLAlchemy 2.0 ORM, Pydantic v2, "
        "and stateless JWT / RBAC authentication."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware: CORS & Instance Identification
# ---------------------------------------------------------------------------
class InstanceIdentifierMiddleware(BaseHTTPMiddleware):
    """Injects X-Instance-ID and X-Instance-PID headers for cluster load tracking."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Instance-ID"] = INSTANCE_ID
        response.headers["X-Instance-PID"] = str(os.getpid())
        return response


app.add_middleware(InstanceIdentifierMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# RFC 9457 Global Exception Handlers
# ---------------------------------------------------------------------------
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Router Registration
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(characters.router)
app.include_router(abilities.router)
app.include_router(armors.router)
app.include_router(weapons.router)
app.include_router(monsters.router)
app.include_router(magics.router)
app.include_router(elements.router)
app.include_router(genders.router)
app.include_router(jobs.router)
app.include_router(races.router)
app.include_router(rarities.router)
app.include_router(body_parts.router)
app.include_router(status_effects.router)
app.include_router(tasks.router)
app.include_router(projects.router)


# ---------------------------------------------------------------------------
# Health Check & Multi-Instance Cluster Introspection
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Cluster & Health"])
@app.get("/api/v1/health", tags=["Cluster & Health"])
def health_check() -> dict[str, str]:
    """Basic health check and probe endpoint."""
    return {
        "status": "healthy",
        "service": "character-build-api",
        "instanceId": INSTANCE_ID,
        "environment": ENVIRONMENT,
    }


@app.get("/api/v1/cluster/status", tags=["Cluster & Health"])
def cluster_status() -> dict[str, object]:
    """Introspect instance state, thread pool metrics, memory and process info."""
    threads = [t.name for t in threading.enumerate()]
    uptime = time.time() - START_TIME
    memory_rss_mb: float | None = None
    cpu_percent: float | None = None

    if psutil is not None:
        try:
            proc = psutil.Process()
            memory_rss_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
            cpu_percent = proc.cpu_percent(interval=0.0)
        except Exception:
            pass

    return {
        "status": "online",
        "instanceId": INSTANCE_ID,
        "environment": ENVIRONMENT,
        "podName": POD_NAME,
        "podIp": POD_IP,
        "nodeName": NODE_NAME,
        "pid": os.getpid(),
        "activeThreads": threading.active_count(),
        "threadNames": threads,
        "memoryRssMb": memory_rss_mb,
        "cpuPercent": cpu_percent,
        "uptimeSeconds": round(uptime, 2),
    }
