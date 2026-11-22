import httpx
import pytest
from aeo_api.main import create_app


@pytest.mark.asyncio
async def test_liveness_does_not_depend_on_database() -> None:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "aeo-api"}


@pytest.mark.asyncio
async def test_readiness_reports_database_unavailable(monkeypatch) -> None:
    async def database_unavailable() -> bool:
        return False

    monkeypatch.setattr("aeo_api.routes.health.database_is_ready", database_unavailable)
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "dependency": "postgresql"}
