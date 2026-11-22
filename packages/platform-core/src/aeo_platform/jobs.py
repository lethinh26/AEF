from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from aeo_platform.models import Job


async def enqueue_job(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    job_type: str,
    payload: dict[str, Any] | None = None,
    max_attempts: int = 5,
) -> UUID:
    """Add a durable job to the caller's transaction."""

    job_id = uuid4()
    session.add(
        Job(
            id=job_id,
            tenant_id=tenant_id,
            job_type=job_type,
            payload=payload or {},
            status="queued",
            attempts=0,
            max_attempts=max_attempts,
            available_at=datetime.now(UTC),
        )
    )
    return job_id
