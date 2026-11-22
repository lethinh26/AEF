from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from aeo_api.main import create_app
from aeo_platform.db import get_session


@pytest.mark.asyncio
async def test_github_sync_queues_public_sources_without_private_token(monkeypatch) -> None:
    class DummySession:
        @asynccontextmanager
        async def begin(self):
            yield

    async def unused_session():
        yield DummySession()

    async def configured_sources(_session):
        return [
            SimpleNamespace(external_id="lethinh26/Clucky"),
            SimpleNamespace(external_id="lethinh26/Llms-System"),
        ]

    async def queue_sources(_session, *, force, allowed_repositories):
        assert force is True
        assert allowed_repositories == ["lethinh26/Clucky"]
        return [uuid4()]

    async def claim_idempotency(*_args, **_kwargs):
        return SimpleNamespace(response_body=None), None

    monkeypatch.setattr("aeo_api.routes.sources.claim_idempotency_key", claim_idempotency)
    monkeypatch.setattr("aeo_api.routes.sources.complete_idempotency", lambda *_args, **_kwargs: None)

    monkeypatch.setattr(
        "aeo_api.routes.sources.get_settings",
        lambda: SimpleNamespace(
            github_token_value=None,
            github_public_repositories=["lethinh26/Clucky"],
            github_repositories=["lethinh26/Clucky", "lethinh26/Llms-System"],
        ),
    )
    monkeypatch.setattr("aeo_api.routes.sources.ensure_configured_github_sources", configured_sources)
    monkeypatch.setattr("aeo_api.routes.sources.queue_due_github_syncs", queue_sources)
    application = create_app()
    application.dependency_overrides[get_session] = unused_session
    transport = httpx.ASGITransport(app=application)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/sources/github/sync",
            headers={"Idempotency-Key": "test-sync-1"},
        )

    assert response.status_code == 202
    assert response.json()["queued"] == 1
    assert response.json()["requires_credential"] == ["lethinh26/Llms-System"]
