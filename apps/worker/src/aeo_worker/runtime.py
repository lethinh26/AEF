import asyncio
import os
import socket
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import structlog
from aeo_platform.bootstrap import ensure_configured_github_sources
from aeo_platform.config import get_settings
from aeo_platform.db import get_session_factory
from aeo_platform.logging import configure_logging
from aeo_platform.models import Job, SourceConnection
from aeo_platform.source_jobs import queue_due_github_syncs
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from aeo_worker.github_sync import handle_github_sync
from aeo_worker.opportunity_analysis import handle_github_opportunity_analysis

logger = structlog.get_logger(__name__)
JobHandler = Callable[[dict[str, Any]], Awaitable[None]]
LEASE_DURATION = timedelta(minutes=5)
HEARTBEAT_INTERVAL_SECONDS = 30


@dataclass(frozen=True)
class ClaimedJob:
    id: UUID
    job_type: str
    payload: dict[str, Any]
    attempts: int
    max_attempts: int


async def _handle_system_echo(payload: dict[str, Any]) -> None:
    logger.info("system_echo_job", payload_keys=sorted(payload.keys()))


HANDLERS: dict[str, JobHandler] = {
    "system.echo": _handle_system_echo,
    "github.sync": handle_github_sync,
    "opportunity.analyze_github": handle_github_opportunity_analysis,
}


async def claim_job(
    session_factory: async_sessionmaker[AsyncSession], worker_id: str
) -> ClaimedJob | None:
    now = datetime.now(UTC)
    async with session_factory() as session:
        async with session.begin():
            expired = await session.scalars(
                select(Job)
                .where(Job.status == "running", Job.locked_at <= now - LEASE_DURATION)
                .order_by(Job.locked_at)
                .limit(50)
                .with_for_update(skip_locked=True)
            )
            for stale_job in expired:
                stale_job.locked_at = None
                stale_job.locked_by = None
                stale_job.last_error = "Worker lease expired; execution may be retried"
                if stale_job.job_type == "github.sync":
                    source_id = stale_job.payload.get("source_connection_id")
                    if source_id:
                        await session.execute(
                            update(SourceConnection)
                            .where(
                                SourceConnection.id == UUID(source_id),
                                SourceConnection.sync_status == "running",
                            )
                            .values(
                                sync_status="failed",
                                last_error_code="worker_lease_expired",
                                next_sync_at=now,
                            )
                        )
                if stale_job.attempts >= stale_job.max_attempts:
                    stale_job.status = "dead"
                else:
                    stale_job.status = "retrying"
                    stale_job.available_at = now

            eligible = and_(Job.status.in_(["queued", "retrying"]), Job.available_at <= now)
            job = await session.scalar(
                select(Job)
                .where(eligible)
                .order_by(Job.available_at, Job.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if job is None:
                return None

            job.status = "running"
            job.attempts += 1
            job.locked_at = now
            job.locked_by = worker_id
            await session.flush()
            return ClaimedJob(
                id=job.id,
                job_type=job.job_type,
                payload=job.payload,
                attempts=job.attempts,
                max_attempts=job.max_attempts,
            )


async def heartbeat_job(
    session_factory: async_sessionmaker[AsyncSession], job_id: UUID, worker_id: str
) -> None:
    async with session_factory() as session:
        async with session.begin():
            await session.execute(
                update(Job)
                .where(Job.id == job_id, Job.status == "running", Job.locked_by == worker_id)
                .values(locked_at=datetime.now(UTC))
            )


async def _heartbeat_loop(
    session_factory: async_sessionmaker[AsyncSession], job_id: UUID, worker_id: str
) -> None:
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
        await heartbeat_job(session_factory, job_id, worker_id)


async def finish_job(
    session_factory: async_sessionmaker[AsyncSession],
    job: ClaimedJob,
    worker_id: str,
    error: Exception | None = None,
) -> None:
    now = datetime.now(UTC)
    values: dict[str, Any] = {"locked_at": None, "locked_by": None}
    if error is None:
        values.update(status="completed", completed_at=now, last_error=None)
    elif job.attempts >= job.max_attempts:
        values.update(status="dead", last_error=f"{type(error).__name__}: handler failed")
    else:
        delay_seconds = min(300, 2 ** min(job.attempts, 8))
        values.update(
            status="retrying",
            available_at=now + timedelta(seconds=delay_seconds),
            last_error=f"{type(error).__name__}: handler failed",
        )

    async with session_factory() as session:
        async with session.begin():
            await session.execute(
                update(Job)
                .where(
                    Job.id == job.id,
                    Job.status == "running",
                    Job.locked_by == worker_id,
                )
                .values(**values)
            )


async def process_one(
    session_factory: async_sessionmaker[AsyncSession], worker_id: str
) -> bool:
    job = await claim_job(session_factory, worker_id)
    if job is None:
        return False

    heartbeat = asyncio.create_task(_heartbeat_loop(session_factory, job.id, worker_id))
    handler = HANDLERS.get(job.job_type)
    try:
        if handler is None:
            raise ValueError(f"No handler registered for job type: {job.job_type}")
        await handler(job.payload)
    except Exception as error:
        await finish_job(session_factory, job, worker_id, error)
        logger.error(
            "job_failed",
            job_id=str(job.id),
            job_type=job.job_type,
            error_type=type(error).__name__,
        )
    else:
        await finish_job(session_factory, job, worker_id)
        logger.info("job_completed", job_id=str(job.id), job_type=job.job_type)
    finally:
        heartbeat.cancel()
        try:
            await heartbeat
        except asyncio.CancelledError:
            pass
    return True


async def run_worker(
    poll_interval: float = 1.0,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    factory = session_factory or get_session_factory()
    worker_id = f"{socket.gethostname()}:{os.getpid()}"
    logger.info("worker_started", worker_id=worker_id, poll_interval=poll_interval)

    async with factory() as session:
        async with session.begin():
            await ensure_configured_github_sources(session)
    last_source_schedule = 0.0

    while True:
        now_monotonic = asyncio.get_running_loop().time()
        if now_monotonic - last_source_schedule >= 30:
            settings = get_settings()
            allowed_repositories = (
                settings.github_repositories
                if settings.github_token_value
                else settings.github_public_repositories
            )
            if settings.github_token_value or allowed_repositories:
                async with factory() as session:
                    async with session.begin():
                        queued = await queue_due_github_syncs(
                            session, allowed_repositories=allowed_repositories
                        )
                if queued:
                    logger.info("github_sync_jobs_scheduled", count=len(queued))
            last_source_schedule = now_monotonic
        did_work = await process_one(factory, worker_id)
        if not did_work:
            await asyncio.sleep(max(0.1, poll_interval))
