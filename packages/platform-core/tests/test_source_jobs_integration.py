import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from aeo_platform.models import Asset, Job, Organization, SourceConnection
from aeo_platform.source_jobs import queue_due_github_syncs, queue_github_opportunity_analysis
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("AEO_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="Set AEO_TEST_DATABASE_URL to run PostgreSQL integration tests",
)


@pytest.mark.asyncio
async def test_source_job_queues_are_deduplicated_in_postgresql() -> None:
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    tenant_id = uuid4()
    asset_id = uuid4()
    source_id = uuid4()
    repository_slug = f"aeo-test/source-jobs-{tenant_id.hex}"
    now = datetime.now(UTC)

    try:
        async with session_factory() as session:
            async with session.begin():
                session.add(
                    Organization(
                        id=tenant_id,
                        slug=f"source-jobs-{tenant_id.hex}",
                        name="Source Jobs Integration Test",
                    )
                )
                await session.flush()
                session.add(
                    Asset(
                        id=asset_id,
                        tenant_id=tenant_id,
                        asset_type="repository",
                        name="Source Jobs Fixture",
                        canonical_ref=f"https://github.com/{repository_slug}",
                        metadata_json={"provider": "github"},
                    )
                )
                await session.flush()
                session.add(
                    SourceConnection(
                        id=source_id,
                        tenant_id=tenant_id,
                        asset_id=asset_id,
                        provider="github",
                        external_id=repository_slug,
                        canonical_url=f"https://github.com/{repository_slug}",
                        access_mode="read_only",
                        status="active",
                        sync_status="idle",
                        sync_interval_seconds=900,
                        next_sync_at=now - timedelta(minutes=1),
                    )
                )

        async with session_factory() as session:
            async with session.begin():
                queued = await queue_due_github_syncs(
                    session, allowed_repositories=[repository_slug]
                )
                assert queued == [source_id]

        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    update(SourceConnection)
                    .where(SourceConnection.id == source_id)
                    .values(sync_status="failed", next_sync_at=now - timedelta(minutes=1))
                )
                await session.execute(
                    update(Job)
                    .where(
                        Job.job_type == "github.sync",
                        Job.payload["source_connection_id"].as_string() == str(source_id),
                    )
                    .values(status="retrying")
                )
                queued = await queue_due_github_syncs(
                    session, allowed_repositories=[repository_slug]
                )
                assert queued == []
                source = await session.get(SourceConnection, source_id)
                assert source is not None and source.sync_status == "queued"
                active_sync_count = await session.scalar(
                    select(func.count(Job.id)).where(
                        Job.job_type == "github.sync",
                        Job.status.in_(["queued", "running", "retrying"]),
                        Job.payload["source_connection_id"].as_string() == str(source_id),
                    )
                )
                assert active_sync_count == 1

        async with session_factory() as session:
            async with session.begin():
                first_job_id = await queue_github_opportunity_analysis(session, source_id)
                assert first_job_id is not None
                await session.flush()
                second_job_id = await queue_github_opportunity_analysis(session, source_id)
                assert second_job_id is None
                active_analysis_count = await session.scalar(
                    select(func.count(Job.id)).where(
                        Job.job_type == "opportunity.analyze_github",
                        Job.status.in_(["queued", "running", "retrying"]),
                        Job.payload["source_connection_id"].as_string() == str(source_id),
                    )
                )
                assert active_analysis_count == 1
    finally:
        async with session_factory() as session:
            async with session.begin():
                await session.execute(delete(Job).where(Job.tenant_id == tenant_id))
                await session.execute(
                    delete(SourceConnection).where(SourceConnection.tenant_id == tenant_id)
                )
                await session.execute(delete(Asset).where(Asset.tenant_id == tenant_id))
                await session.execute(delete(Organization).where(Organization.id == tenant_id))
        await engine.dispose()
