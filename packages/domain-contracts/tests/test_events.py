from datetime import UTC, datetime
from uuid import uuid4

import pytest
from aeo_contracts.events import EventEnvelope
from pydantic import ValidationError


def test_event_envelope_requires_timezone_aware_timestamps() -> None:
    common = {
        "event_id": uuid4(),
        "event_type": "observation.received",
        "event_version": 1,
        "aggregate_type": "observation",
        "aggregate_id": uuid4(),
        "aggregate_version": 1,
        "tenant_id": uuid4(),
        "actor": "service:connector",
        "correlation_id": uuid4(),
    }

    with pytest.raises(ValidationError):
        EventEnvelope(
            **common,
            occurred_at=datetime(2026, 11, 22),
            observed_at=datetime.now(UTC),
        )


def test_event_envelope_is_immutable_and_rejects_unknown_fields() -> None:
    event = EventEnvelope(
        event_id=uuid4(),
        event_type="observation.received",
        event_version=1,
        aggregate_type="observation",
        aggregate_id=uuid4(),
        aggregate_version=1,
        tenant_id=uuid4(),
        occurred_at=datetime.now(UTC),
        observed_at=datetime.now(UTC),
        actor="service:connector",
        correlation_id=uuid4(),
    )

    with pytest.raises(ValidationError):
        EventEnvelope.model_validate({**event.model_dump(), "unexpected": True})

    with pytest.raises(ValidationError):
        event.event_type = "goal.activated"
