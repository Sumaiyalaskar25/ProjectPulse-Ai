# tests/test_security_auth.py
import pytest
from httpx import AsyncClient, ASGITransport
from services.api.main import app
from services.api.core.auth import create_jwt_token

@pytest.mark.asyncio
async def test_unauthenticated_state_mutations():
    """Verify unauthorized role cannot mutate critical operational state."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generate viewer token (not operator or admin)
        viewer_token = create_jwt_token("user-viewer", "viewer@test.local", role="viewer")
        headers = {"Authorization": f"Bearer {viewer_token}"}

        # Attempt acknowledge alert as viewer -> Should return 403 Forbidden
        res = await client.post("/api/v1/alerts/1/acknowledge", headers=headers, json={"assigned_to": "alice"})
        assert res.status_code == 403
        data = res.json()
        assert data["error"]["code"] == "FORBIDDEN"

@pytest.mark.asyncio
async def test_invalid_jwt_token():
    """Verify invalid token signature or malformed token is rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer invalid.jwt.token"}
        res = await client.post("/api/v1/alerts/1/acknowledge", headers=headers)
        assert res.status_code == 401
        data = res.json()
        assert data["error"]["code"] == "AUTHENTICATION_FAILED"

@pytest.mark.asyncio
async def test_rate_limiting_exceeded():
    """Verify rate limiter blocks burst calls exceeding threshold with 429."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Hit assistant endpoint repeatedly
        status_codes = []
        for _ in range(25):
            res = await client.post("/api/v1/assistant/query", json={"query": "Which projects are delayed?"})
            status_codes.append(res.status_code)
        
        # At least one request should have hit the 429 rate limit
        assert 429 in status_codes

@pytest.mark.asyncio
async def test_intervention_invalid_date_validation():
    """Verify malformed intervention date triggers 422 ValidationError (TC-004)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_token = create_jwt_token("admin-user", "admin@test.local", role="admin")
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "project_id": "PRJ_NON_EXISTENT",
            "owner": "Engineer Dave",
            "category": "schedule_review",
            "action_description": "Site mobilization speedup",
            "status": "pending",
            "due_date": "not-a-valid-date-format"
        }
        res = await client.post("/api/v1/interventions", headers=headers, json=payload)
        assert res.status_code == 422
        data = res.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
