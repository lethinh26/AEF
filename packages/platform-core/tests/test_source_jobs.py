from types import SimpleNamespace
from uuid import uuid4

import pytest
from aeo_platform.source_jobs import (
    queue_due_github_syncs,
    queue_github_opportunity_analysis,
)


class DummySession:
    def __init__(self, *, sources=None, scalar_results=None):
        self.sources = sources or []
        self.scalar_results = list(scalar_results or [])
        self.added = []

    async def scalars(self, _statement):
        return self.sources

    async def scalar(self, _statement):
        return self.scalar_results.pop(0)

    def add(self, item):
        self.added.append(item)


@pytest.mark.asyncio
async def test_sync_scheduler_does_not_enqueue_when_a_retry_is_already_active() -> None:
    source = SimpleNamespace(
        id=uuid4(),
        tenant_id=uuid4(),
        sync_status="failed",
        last_error_code="github_rate_limited",
    )
    active_job = SimpleNamespace(status="retrying")
    session = DummySession(sources=[source], scalar_results=[active_job])

    queued = await queue_due_github_syncs(session)

    assert queued == []
    assert source.sync_status == "queued"
    assert session.added == []


@pytest.mark.asyncio
async def test_sync_scheduler_enqueues_when_no_active_job_exists() -> None:
    source = SimpleNamespace(
        id=uuid4(), tenant_id=uuid4(), sync_status="idle", last_error_code=None
    )
    session = DummySession(sources=[source], scalar_results=[None])

    queued = await queue_due_github_syncs(session)

    assert queued == [source.id]
    assert source.sync_status == "queued"
    assert len(session.added) == 1
    assert session.added[0].job_type == "github.sync"
    assert session.added[0].payload == {"source_connection_id": str(source.id)}


@pytest.mark.asyncio
async def test_analysis_queue_skips_an_existing_active_job() -> None:
    source = SimpleNamespace(id=uuid4(), tenant_id=uuid4(), status="active")
    active_job = SimpleNamespace(status="running")
    session = DummySession(scalar_results=[source, active_job])

    queued = await queue_github_opportunity_analysis(session, source.id)

    assert queued is None
    assert session.added == []


@pytest.mark.asyncio
async def test_analysis_queue_creates_one_job_when_none_is_active() -> None:
    source = SimpleNamespace(id=uuid4(), tenant_id=uuid4(), status="active")
    session = DummySession(scalar_results=[source, None])

    queued = await queue_github_opportunity_analysis(session, source.id)

    assert queued is not None
    assert len(session.added) == 1
    assert session.added[0].id == queued
    assert session.added[0].job_type == "opportunity.analyze_github"
