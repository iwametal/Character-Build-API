"""Tests for multi-instance cluster introspection, health checks, and thread management."""

from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient) -> None:
    """Validate /health endpoint structure for container and Kubernetes probes."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "character-build-api"
    assert "instanceId" in data
    assert "environment" in data


def test_cluster_status_introspection(client: TestClient) -> None:
    """Validate /api/v1/cluster/status returns instance and thread pool metrics."""
    response = client.get("/api/v1/cluster/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "instanceId" in data
    assert "pid" in data
    assert isinstance(data["activeThreads"], int)
    assert data["activeThreads"] > 0
    assert isinstance(data["threadNames"], list)
    assert len(data["threadNames"]) > 0
    assert "uptimeSeconds" in data


def test_instance_identifier_middleware_headers(client: TestClient) -> None:
    """Validate X-Instance-ID and X-Instance-PID headers are present in all HTTP responses."""
    response = client.get("/health")
    assert "x-instance-id" in response.headers
    assert "x-instance-pid" in response.headers
    assert len(response.headers["x-instance-id"]) > 0

    # Check that another endpoint also has the instance headers
    response2 = client.get("/api/v1/genders")
    assert "x-instance-id" in response2.headers
    assert "x-instance-pid" in response2.headers
