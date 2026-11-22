from uuid import UUID

from aeo_contracts.events import EventEnvelope
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from aeo_platform.models import InboxDedup, OutboxEvent


async def append_event(session: AsyncSession, event: EventEnvelope) -> None:
    """Append an event in the caller's transaction with the related state change."""

    session.add(
        OutboxEvent(
            id=event.event_id,
            event_type=event.event_type,
            event_version=event.event_version,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            aggregate_version=event.aggregate_version,
            tenant_id=event.tenant_id,
            occurred_at=event.occurred_at,
            observed_at=event.observed_at,
            actor=event.actor,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            policy_decision_id=event.policy_decision_id,
            payload=event.payload,
            payload_ref=event.payload_ref,
            payload_digest=event.payload_digest,
        )
    )


async def mark_event_processed(
    session: AsyncSession, *, consumer_id: str, event_id: UUID
) -> bool:
    """Record inbox deduplication; return False when this consumer already handled the event."""

    statement = (
        insert(InboxDedup)
        .values(consumer_id=consumer_id, event_id=event_id)
        .on_conflict_do_nothing(index_elements=[InboxDedup.consumer_id, InboxDedup.event_id])
        .returning(InboxDedup.event_id)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none() is not None
