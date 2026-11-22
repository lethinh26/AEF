import hashlib
import json
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from aeo_platform.models import IdempotencyKey


class IdempotencyConflict(ValueError):
    pass


def request_hash(operation: str, payload: dict[str, Any] | None = None) -> str:
    canonical = json.dumps(
        {"operation": operation, "payload": payload or {}},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


async def claim_idempotency_key(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    key: str,
    request_digest: str,
) -> tuple[IdempotencyKey, dict[str, Any] | None]:
    normalized_key = key.strip()
    if not normalized_key or len(normalized_key) > 255:
        raise ValueError("Idempotency-Key must contain 1 to 255 non-whitespace characters")

    inserted = await session.execute(
        insert(IdempotencyKey)
        .values(
            id=uuid4(),
            tenant_id=tenant_id,
            key=normalized_key,
            request_hash=request_digest,
        )
        .on_conflict_do_nothing(index_elements=["tenant_id", "key"])
        .returning(IdempotencyKey.id)
    )
    created = inserted.scalar_one_or_none() is not None
    record = await session.scalar(
        select(IdempotencyKey)
        .where(IdempotencyKey.tenant_id == tenant_id, IdempotencyKey.key == normalized_key)
        .with_for_update()
    )
    if record is None:
        raise IdempotencyConflict("Idempotency-Key could not be claimed")
    if record.request_hash != request_digest:
        raise IdempotencyConflict("Idempotency-Key was already used for a different request")
    if not created and record.response_body is None:
        raise IdempotencyConflict("A request with this Idempotency-Key is already in progress")
    return record, record.response_body


def complete_idempotency(
    record: IdempotencyKey,
    *,
    response_status: int,
    response_body: dict[str, Any],
) -> None:
    record.response_status = response_status
    record.response_body = response_body
