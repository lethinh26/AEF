from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class EventEnvelope(BaseModel):
    """Canonical event metadata; payloads must already be redacted and policy checked."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID
    event_type: str = Field(min_length=3, max_length=160, pattern=r"^[a-z][a-z0-9_.-]+$")
    event_version: int = Field(ge=1)
    aggregate_type: str = Field(min_length=1, max_length=80)
    aggregate_id: UUID
    aggregate_version: int = Field(ge=1)
    tenant_id: UUID
    occurred_at: AwareDatetime
    observed_at: AwareDatetime
    actor: str = Field(min_length=1, max_length=160)
    correlation_id: UUID
    causation_id: UUID | None = None
    policy_decision_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    payload_ref: str | None = Field(default=None, max_length=1024)
    payload_digest: str | None = Field(default=None, max_length=80)


class ApiError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=1000)
    retryable: bool = False
    correlation_id: UUID | None = None
    policy_reason: str | None = None
