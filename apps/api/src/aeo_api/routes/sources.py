import json
from typing import Annotated, Any
from uuid import UUID

from aeo_platform.bootstrap import LOCAL_ORGANIZATION_ID, ensure_configured_github_sources
from aeo_platform.config import get_settings
from aeo_platform.db import get_session
from aeo_platform.models import Asset, Observation, SourceConnection
from aeo_platform.object_store import ArtifactStore
from aeo_platform.source_jobs import queue_due_github_syncs
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1", tags=["sources", "evidence"])


@router.get("/sources")
async def list_sources(session: Annotated[AsyncSession, Depends(get_session)]) -> dict[str, Any]:
    async with session.begin():
        await ensure_configured_github_sources(session)

    rows = await session.execute(
        select(SourceConnection, Asset)
        .join(
            Asset,
            (Asset.tenant_id == SourceConnection.tenant_id)
            & (Asset.id == SourceConnection.asset_id),
        )
        .where(
            SourceConnection.tenant_id == LOCAL_ORGANIZATION_ID,
            SourceConnection.provider == "github",
        )
        .order_by(SourceConnection.external_id)
    )
    sources = []
    settings = get_settings()
    for connection, asset in rows:
        sources.append(
            {
                "id": str(connection.id),
                "provider": connection.provider,
                "repository": connection.external_id,
                "name": asset.name,
                "display_name": asset.name,
                "url": connection.canonical_url,
                "access_mode": connection.access_mode,
                "status": connection.status,
                "sync_status": connection.sync_status,
                "sync_interval_seconds": connection.sync_interval_seconds,
                "last_sync_started_at": connection.last_sync_started_at,
                "last_sync_completed_at": connection.last_sync_completed_at,
                "last_observation_at": connection.last_observation_at,
                "next_sync_at": connection.next_sync_at,
                "last_error_code": connection.last_error_code,
                "credential_required": (
                    not bool(settings.github_token_value)
                    and connection.external_id not in settings.github_public_repositories
                ),
            }
        )

    return {
        "repositories": sources,
        "github_credential_configured": bool(settings.github_token_value),
        "github_public_repositories": settings.github_public_repositories,
        "sync_available": bool(settings.github_token_value or settings.github_public_repositories),
        "sync_interval_seconds": settings.github_sync_interval_seconds,
        "mode": "read_only",
    }


@router.post("/sources/github/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_github_sources(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    settings = get_settings()
    async with session.begin():
        connections = await ensure_configured_github_sources(session)
        allowed_repositories = (
            None if settings.github_token_value else settings.github_public_repositories
        )
        queued = await queue_due_github_syncs(
            session, force=True, allowed_repositories=allowed_repositories
        )
        requires_credential = [
            source.external_id
            for source in connections
            if not settings.github_token_value
            and source.external_id not in settings.github_public_repositories
        ]
    return {
        "queued": len(queued),
        "source_ids": [str(source_id) for source_id in queued],
        "requires_credential": requires_credential,
    }


@router.get("/observations")
async def list_observations(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    source_id: UUID | None = None,
) -> dict[str, Any]:
    statement = (
        select(Observation, Asset)
        .outerjoin(
            Asset,
            (Asset.tenant_id == Observation.tenant_id) & (Asset.id == Observation.asset_id),
        )
        .where(Observation.tenant_id == LOCAL_ORGANIZATION_ID)
        .order_by(Observation.observed_at.desc())
        .limit(limit)
    )
    if source_id is not None:
        connection = await session.scalar(
            select(SourceConnection).where(
                SourceConnection.id == source_id,
                SourceConnection.tenant_id == LOCAL_ORGANIZATION_ID,
            )
        )
        if connection is None:
            raise HTTPException(status_code=404, detail="Source not found")
        statement = statement.where(Observation.asset_id == connection.asset_id)

    rows = await session.execute(statement)
    observations = []
    for observation, asset in rows:
        observations.append(
            {
                "id": str(observation.id),
                "source": asset.name if asset else observation.source_key,
                "source_key": observation.source_key,
                "event_type": observation.event_type,
                "title": observation.title or observation.event_type,
                "summary": observation.summary or "",
                "external_url": observation.external_url,
                "occurred_at": observation.occurred_at,
                "observed_at": observation.observed_at,
                "payload_ref": observation.payload_ref,
                "payload_digest": observation.payload_digest,
                "classification": observation.classification,
                "status": observation.status,
            }
        )
    return {"observations": observations, "count": len(observations)}


@router.get("/observations/{observation_id}")
async def get_observation(
    observation_id: UUID, session: Annotated[AsyncSession, Depends(get_session)]
) -> dict[str, Any]:
    observation = await session.scalar(
        select(Observation).where(
            Observation.id == observation_id,
            Observation.tenant_id == LOCAL_ORGANIZATION_ID,
        )
    )
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    if not observation.payload_ref or not observation.payload_ref.startswith("artifact://"):
        raise HTTPException(status_code=404, detail="Observation payload is unavailable")

    storage_key = observation.payload_ref.removeprefix("artifact://")
    try:
        payload = json.loads(await ArtifactStore().get_bytes(storage_key))
    except Exception as error:
        raise HTTPException(
            status_code=503, detail="Observation payload store is temporarily unavailable"
        ) from error
    return {
        "id": str(observation.id),
        "source_key": observation.source_key,
        "event_type": observation.event_type,
        "title": observation.title,
        "summary": observation.summary,
        "external_url": observation.external_url,
        "occurred_at": observation.occurred_at,
        "observed_at": observation.observed_at,
        "payload_digest": observation.payload_digest,
        "classification": observation.classification,
        "payload": payload,
    }
