# tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from services.api.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify that /health responds with valid structure and request ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "projectpulse-api"
        # Assert correlation ID is returned in headers
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time-Ms" in response.headers

@pytest.mark.asyncio
async def test_security_headers_present():
    """Verify security headers are attached to responses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

@pytest.mark.asyncio
async def test_custom_request_id_propagation():
    """Verify incoming X-Request-ID is preserved and echoed back."""
    custom_id = "test-custom-trace-12345"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.headers.get("X-Request-ID") == custom_id
