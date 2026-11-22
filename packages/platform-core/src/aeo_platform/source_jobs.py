from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aeo_platform.jobs import enqueue_job
from aeo_platform.models import Job, SourceConnection

ACTIVE_JOB_STATUSES = ("queued", "running", "retrying")


async def find_active_source_job(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    source_id: UUID,
    job_type: str,
) -> Job | None:
    return await session.scalar(
        select(Job)
        .where(
            Job.tenant_id == tenant_id,
            Job.job_type == job_type,
            Job.status.in_(ACTIVE_JOB_STATUSES),
            Job.payload["source_connection_id"].as_string() == str(source_id),
        )
        .order_by(Job.created_at.desc())
        .limit(1)
    )


async def queue_github_opportunity_analysis(
    session: AsyncSession, source_id: UUID
) -> UUID | None:
    source = await session.scalar(
        select(SourceConnection).where(SourceConnection.id == source_id).with_for_update()
    )
    if source is None or source.status != "active":
        return None

    active_job = await find_active_source_job(
        session,
        tenant_id=source.tenant_id,
        source_id=source.id,
        job_type="opportunity.analyze_github",
    )
    if active_job is not None:
        return None

    return await enqueue_job(
        session,
        tenant_id=source.tenant_id,
        job_type="opportunity.analyze_github",
        payload={"source_connection_id": str(source.id)},
    )


async def queue_due_github_syncs(
    session: AsyncSession,
    *,
    force: bool = False,
    allowed_repositories: list[str] | None = None,
    limit: int = 20,
) -> list[UUID]:
    now = datetime.now(UTC)
    statement = select(SourceConnection).where(
        SourceConnection.provider == "github",
        SourceConnection.status == "active",
        SourceConnection.sync_status.in_(["idle", "failed"]),
    )
    if not force:
        statement = statement.where(SourceConnection.next_sync_at <= now)
    if allowed_repositories is not None:
        if not allowed_repositories:
            return []
        statement = statement.where(SourceConnection.external_id.in_(allowed_repositories))
    sources = await session.scalars(
        statement.order_by(SourceConnection.next_sync_at).limit(limit).with_for_update(skip_locked=True)
    )

    queued: list[UUID] = []
    for source in sources:
        active_job = await find_active_source_job(
            session,
            tenant_id=source.tenant_id,
            source_id=source.id,
            job_type="github.sync",
        )
        if active_job is not None:
            source.sync_status = "running" if active_job.status == "running" else "queued"
            continue

        source.sync_status = "queued"
        source.last_error_code = None
        await enqueue_job(
            session,
            tenant_id=source.tenant_id,
            job_type="github.sync",
            payload={"source_connection_id": str(source.id)},
            max_attempts=5,
        )
        queued.append(source.id)
    return queued
