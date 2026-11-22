import os
from uuid import uuid4

import pytest
from aeo_platform.jobs import enqueue_job
from aeo_platform.models import InboxDedup, Job, Organization
from aeo_platform.outbox import mark_event_processed
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("AEO_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="Set AEO_TEST_DATABASE_URL to run PostgreSQL integration tests",
)


@pytest.mark.asyncio
async def test_inbox_deduplication_accepts_an_event_once() -> None:
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    event_id = uuid4()

    try:
        async with session_factory() as session:
            async with session.begin():
                first_delivery = await mark_event_processed(
                    session, consumer_id="integration-test", event_id=event_id
                )
            async with session.begin():
                duplicate_delivery = await mark_event_processed(
                    session, consumer_id="integration-test", event_id=event_id
                )

        assert first_delivery is True
        assert duplicate_delivery is False
    finally:
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    InboxDedup.__table__.delete().where(
                        InboxDedup.consumer_id == "integration-test",
                        InboxDedup.event_id == event_id,
                    )
                )
        await engine.dispose()


@pytest.mark.asyncio
async def test_worker_claims_and_completes_a_durable_job() -> None:
    from aeo_worker.runtime import process_one

    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    tenant_id = uuid4()
    job_id = None

    try:
        async with session_factory() as session:
            async with session.begin():
                session.add(
                    Organization(
                        id=tenant_id,
                        slug=f"integration-{tenant_id.hex}",
                        name="Integration Test",
                    )
                )
                await session.flush()
                job_id = await enqueue_job(
                    session,
                    tenant_id=tenant_id,
                    job_type="system.echo",
                    payload={"integration_test": True},
                )

        assert await process_one(session_factory, worker_id=f"integration-{tenant_id.hex}")

        async with session_factory() as session:
            job = await session.get(Job, job_id)
            assert job is not None
            assert job.status == "completed"
            assert job.attempts == 1
    finally:
        async with session_factory() as session:
            async with session.begin():
                if job_id is not None:
                    await session.execute(Job.__table__.delete().where(Job.id == job_id))
                await session.execute(
                    Organization.__table__.delete().where(Organization.id == tenant_id)
                )
        await engine.dispose()


@pytest.mark.asyncio
async def test_worker_retries_failures_without_persisting_exception_text(monkeypatch) -> None:
    from aeo_worker import runtime

    async def failing_handler(_: dict) -> None:
        raise RuntimeError("provider_token=do-not-store-this")

    monkeypatch.setitem(runtime.HANDLERS, "integration.fail", failing_handler)
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    tenant_id = uuid4()
    job_id = None

    try:
        async with session_factory() as session:
            async with session.begin():
                session.add(
                    Organization(
                        id=tenant_id,
                        slug=f"integration-fail-{tenant_id.hex}",
                        name="Integration Failure Test",
                    )
                )
                await session.flush()
                job_id = await enqueue_job(
                    session,
                    tenant_id=tenant_id,
                    job_type="integration.fail",
                    max_attempts=3,
                )

        assert await runtime.process_one(
            session_factory, worker_id=f"integration-fail-{tenant_id.hex}"
        )

        async with session_factory() as session:
            job = await session.get(Job, job_id)
            assert job is not None
            assert job.status == "retrying"
            assert job.attempts == 1
            assert job.last_error == "RuntimeError: handler failed"
            assert "do-not-store-this" not in (job.last_error or "")
    finally:
        async with session_factory() as session:
            async with session.begin():
                if job_id is not None:
                    await session.execute(Job.__table__.delete().where(Job.id == job_id))
                await session.execute(
                    Organization.__table__.delete().where(Organization.id == tenant_id)
                )
        await engine.dispose()
