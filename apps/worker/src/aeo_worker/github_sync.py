import asyncio
import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import structlog
from aeo_contracts.events import EventEnvelope
from aeo_github import GitHubAPIError, GitHubClient, collect_repository_snapshot
from aeo_platform.config import get_settings
from aeo_platform.db import get_session_factory
from aeo_platform.models import (
    ArtifactMetadata,
    AuditEvent,
    Observation,
    SourceConnection,
    SourceCursor,
)
from aeo_platform.object_store import ArtifactStore
from aeo_platform.outbox import append_event
from aeo_platform.source_jobs import queue_github_opportunity_analysis
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

logger = structlog.get_logger(__name__)


async def _mark_source_failed(source_id: UUID, code: str) -> None:
    now = datetime.now(UTC)
    factory = get_session_factory()
    async with factory() as session:
        async with session.begin():
            source = await session.scalar(
                select(SourceConnection).where(SourceConnection.id == source_id).with_for_update()
            )
            if source is not None:
                source.sync_status = "failed"
                source.last_error_code = code[:120]
                source.next_sync_at = now + timedelta(minutes=5)


async def handle_github_sync(payload: dict[str, Any]) -> None:
    settings = get_settings()
    token = settings.github_token_value
    source_id = UUID(payload["source_connection_id"])
    factory = get_session_factory()

    async with factory() as session:
        async with session.begin():
            source = await session.scalar(
                select(SourceConnection).where(SourceConnection.id == source_id).with_for_update()
            )
            if source is None:
                raise ValueError("GitHub source connection does not exist")
            if source.status != "active":
                source.sync_status = "idle"
                return
            source.sync_status = "running"
            source.last_sync_started_at = datetime.now(UTC)
            source.last_error_code = None
            tenant_id = source.tenant_id
            asset_id = source.asset_id
            repository_slug = source.external_id
            source_key = f"github:{repository_slug}"
            previous_sync = source.last_sync_completed_at

    if not token and repository_slug not in settings.github_public_repositories:
        await _mark_source_failed(source_id, "github_token_missing")
        raise RuntimeError("A GitHub read-only credential is required for this private source")

    client = GitHubClient(token)
    try:
        records = await collect_repository_snapshot(
            client,
            repository_slug,
            since=(previous_sync - timedelta(days=2)) if previous_sync else None,
        )
    except GitHubAPIError as error:
        await _mark_source_failed(source_id, error.code)
        logger.warning(
            "github_source_sync_rejected",
            repository=repository_slug,
            error_code=error.code,
            status_code=error.status_code,
            retry_after_seconds=error.retry_after_seconds,
        )
        raise
    except Exception as error:
        await _mark_source_failed(source_id, "github_sync_failed")
        logger.warning(
            "github_source_sync_failed",
            repository=repository_slug,
            error_type=type(error).__name__,
        )
        raise
    finally:
        await client.aclose()

    observed_at = datetime.now(UTC)
    store = ArtifactStore()
    semaphore = asyncio.Semaphore(8)
    artifact_rows: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []

    async def prepare_record(record) -> tuple[dict[str, Any], dict[str, Any]]:
        payload_bytes = json.dumps(
            record.payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest = hashlib.sha256(payload_bytes).hexdigest()
        owner, repository = repository_slug.split("/", maxsplit=1)
        storage_key = f"github/{owner}/{repository}/observations/{digest[:2]}/{digest}.json"
        async with semaphore:
            await store.put_bytes(
                storage_key,
                payload_bytes,
                content_type="application/json",
                sha256=digest,
            )

        observation_id = uuid5(
            NAMESPACE_URL,
            f"aeo:observation:{tenant_id}:{source_key}:{record.source_event_id}",
        )
        artifact_id = uuid5(NAMESPACE_URL, f"aeo:artifact:{tenant_id}:{storage_key}")
        artifact = {
            "id": artifact_id,
            "tenant_id": tenant_id,
            "storage_key": storage_key,
            "media_type": "application/json",
            "size_bytes": len(payload_bytes),
            "sha256": digest,
            "classification": record.classification,
        }
        observation = {
            "id": observation_id,
            "tenant_id": tenant_id,
            "source_key": source_key,
            "source_event_id": record.source_event_id,
            "asset_id": asset_id,
            "event_type": record.event_type,
            "title": record.title,
            "summary": record.summary,
            "external_url": record.external_url,
            "occurred_at": record.occurred_at,
            "observed_at": observed_at,
            "payload_ref": f"artifact://{storage_key}",
            "payload_digest": f"sha256:{digest}",
            "classification": record.classification,
            "status": "accepted",
        }
        return artifact, observation

    try:
        prepared = await asyncio.gather(*(prepare_record(record) for record in records))
        artifact_rows = [item[0] for item in prepared]
        observation_rows = [item[1] for item in prepared]

        async with factory() as session:
            async with session.begin():
                await session.execute(
                    insert(ArtifactMetadata)
                    .values(artifact_rows)
                    .on_conflict_do_nothing(index_elements=["tenant_id", "storage_key"])
                )
                result = await session.execute(
                    insert(Observation)
                    .values(observation_rows)
                    .on_conflict_do_nothing(
                        index_elements=["tenant_id", "source_key", "source_event_id"]
                    )
                    .returning(Observation.id)
                )
                inserted_count = len(result.scalars().all())
                duplicate_count = len(observation_rows) - inserted_count

                cursor = await session.scalar(
                    select(SourceCursor).where(
                        SourceCursor.tenant_id == tenant_id,
                        SourceCursor.source_key == source_key,
                    )
                )
                cursor_data = {
                    "last_synced_at": observed_at.isoformat(),
                    "last_snapshot_count": len(records),
                    "last_inserted_count": inserted_count,
                    "last_duplicate_count": duplicate_count,
                }
                if cursor is None:
                    session.add(
                        SourceCursor(
                            id=uuid5(NAMESPACE_URL, f"aeo:cursor:{tenant_id}:{source_key}"),
                            tenant_id=tenant_id,
                            source_key=source_key,
                            cursor=cursor_data,
                        )
                    )
                else:
                    cursor.cursor = cursor_data
                    cursor.updated_at = observed_at

                source = await session.scalar(
                    select(SourceConnection)
                    .where(SourceConnection.id == source_id)
                    .with_for_update()
                )
                if source is not None:
                    source.sync_status = "idle"
                    source.last_sync_completed_at = observed_at
                    source.last_observation_at = observed_at if records else source.last_observation_at
                    source.next_sync_at = observed_at + timedelta(
                        seconds=source.sync_interval_seconds
                    )
                    source.last_error_code = None

                session.add(
                    AuditEvent(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        actor="service:github-observer",
                        action="source.sync.completed",
                        resource_type="source_connection",
                        resource_id=str(source_id),
                        outcome="success",
                        correlation_id=uuid4(),
                        details={
                            "provider": "github",
                            "repository": repository_slug,
                            "fetched": len(records),
                            "inserted": inserted_count,
                            "duplicates": duplicate_count,
                        },
                    )
                )
                await append_event(
                    session,
                    EventEnvelope(
                        event_id=uuid5(NAMESPACE_URL, f"aeo:event:source-sync:{source_id}:{observed_at.isoformat()}"),
                        event_type="observation.received",
                        event_version=1,
                        aggregate_type="source_sync",
                        aggregate_id=uuid5(
                            NAMESPACE_URL, f"aeo:source-sync:{source_id}:{observed_at.isoformat()}"
                        ),
                        aggregate_version=1,
                        tenant_id=tenant_id,
                        occurred_at=observed_at,
                        observed_at=observed_at,
                        actor="service:github-observer",
                        correlation_id=source_id,
                        payload={
                            "repository": repository_slug,
                            "fetched": len(records),
                            "inserted": inserted_count,
                            "duplicates": duplicate_count,
                        },
                    ),
                )
                await queue_github_opportunity_analysis(session, source_id)
    except Exception as error:
        await _mark_source_failed(source_id, "artifact_persistence_failed")
        logger.warning(
            "github_source_persistence_failed",
            repository=repository_slug,
            error_type=type(error).__name__,
        )
        raise

    logger.info(
        "github_source_sync_completed",
        repository=repository_slug,
        fetched=len(records),
        inserted=inserted_count,
        duplicates=duplicate_count,
    )
