from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import uuid4

import pytest
from aeo_api.routes.opportunities import (
    OpportunityTriageRequest,
    recompute_opportunities,
    triage_opportunity,
)
from fastapi import HTTPException
from pydantic import ValidationError


class DummySession:
    def __init__(self, opportunity):
        self.opportunity = opportunity
        self.added = []

    @asynccontextmanager
    async def begin(self):
        yield

    async def scalar(self, _statement):
        return self.opportunity

    def add(self, item):
        self.added.append(item)


class DummyRecomputeSession:
    def __init__(self, sources, scalar_results):
        self.sources = sources
        self.scalar_results = list(scalar_results)
        self.added = []

    @asynccontextmanager
    async def begin(self):
        yield

    async def scalars(self, _statement):
        return self.sources

    async def scalar(self, _statement):
        return self.scalar_results.pop(0)

    def add(self, item):
        self.added.append(item)


@pytest.mark.asyncio
async def test_triage_updates_proposed_opportunity_and_writes_audit() -> None:
    opportunity_id = uuid4()
    opportunity = SimpleNamespace(status="proposed", updated_at=None)
    session = DummySession(opportunity)

    result = await triage_opportunity(
        opportunity_id,
        OpportunityTriageRequest(action="accept", reason="  Reviewed evidence  "),
        session,
    )

    assert result == {"id": str(opportunity_id), "status": "accepted"}
    assert opportunity.status == "accepted"
    assert len(session.added) == 1
    assert session.added[0].action == "opportunity.triaged"
    assert session.added[0].details == {"action": "accept", "reason": "Reviewed evidence"}


@pytest.mark.asyncio
async def test_triage_rejects_a_second_transition() -> None:
    session = DummySession(SimpleNamespace(status="accepted", updated_at=None))

    with pytest.raises(HTTPException) as error:
        await triage_opportunity(
            uuid4(),
            OpportunityTriageRequest(action="reject", reason="No longer relevant"),
            session,
        )

    assert error.value.status_code == 409
    assert session.added == []


@pytest.mark.asyncio
async def test_triage_returns_not_found_for_unknown_opportunity() -> None:
    with pytest.raises(HTTPException) as error:
        await triage_opportunity(
            uuid4(),
            OpportunityTriageRequest(action="defer", reason="Need more evidence"),
            DummySession(None),
        )

    assert error.value.status_code == 404


def test_triage_reason_must_not_be_blank() -> None:
    with pytest.raises(ValidationError):
        OpportunityTriageRequest(action="accept", reason="   ")


def test_triage_action_is_restricted_to_supported_values() -> None:
    with pytest.raises(ValidationError):
        OpportunityTriageRequest(action="merge", reason="Not an allowed triage action")


@pytest.mark.asyncio
async def test_recompute_skips_sources_without_observations() -> None:
    source_with_data = SimpleNamespace(
        id=uuid4(), tenant_id=uuid4(), asset_id=uuid4(), status="active"
    )
    source_without_data = SimpleNamespace(
        id=uuid4(), tenant_id=uuid4(), asset_id=uuid4(), status="active"
    )
    session = DummyRecomputeSession(
        [source_with_data, source_without_data],
        [uuid4(), source_with_data, None, None],
    )

    result = await recompute_opportunities(session)

    assert result["queued"] == 1
    assert result["skipped_active"] == 0
    assert result["skipped_no_observations"] == 1
    assert len(session.added) == 1
    assert session.added[0].job_type == "opportunity.analyze_github"


@pytest.mark.asyncio
async def test_recompute_skips_sources_with_an_active_analysis_job() -> None:
    source = SimpleNamespace(id=uuid4(), tenant_id=uuid4(), asset_id=uuid4(), status="active")
    active_job = SimpleNamespace(status="retrying")
    session = DummyRecomputeSession([source], [uuid4(), source, active_job])

    result = await recompute_opportunities(session)

    assert result["queued"] == 0
    assert result["skipped_active"] == 1
    assert result["skipped_no_observations"] == 0
    assert session.added == []
