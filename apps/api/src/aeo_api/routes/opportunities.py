from collections import defaultdict
from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from aeo_contracts.events import EventEnvelope
from aeo_platform.bootstrap import LOCAL_ORGANIZATION_ID
from aeo_platform.db import get_session
from aeo_platform.idempotency import (
    IdempotencyConflict,
    claim_idempotency_key,
    complete_idempotency,
    request_hash,
)
from aeo_platform.models import (
    Asset,
    AuditEvent,
    Finding,
    Observation,
    Opportunity,
    OpportunityEvidence,
    SourceConnection,
)
from aeo_platform.outbox import append_event
from aeo_platform.source_jobs import queue_github_opportunity_analysis
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1", tags=["opportunities"])


class OpportunityTriageRequest(BaseModel):
    action: Literal["accept", "defer", "reject"]
    reason: str = Field(min_length=1, max_length=1_000)

    @field_validator("reason")
    @classmethod
    def reason_must_contain_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Review reason must contain non-whitespace text")
        return normalized


@router.get("/opportunities")
async def list_opportunities(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> dict[str, Any]:
    evidence_count = (
        select(func.count(OpportunityEvidence.id))
        .where(
            OpportunityEvidence.tenant_id == Opportunity.tenant_id,
            OpportunityEvidence.opportunity_id == Opportunity.id,
        )
        .correlate(Opportunity)
        .scalar_subquery()
    )
    rows = await session.execute(
        select(Opportunity, evidence_count)
        .where(Opportunity.tenant_id == LOCAL_ORGANIZATION_ID)
        .order_by(Opportunity.updated_at.desc())
        .limit(limit)
    )
    opportunities = list(rows)
    opportunity_ids = [opportunity.id for opportunity, _ in opportunities]
    evidence_by_opportunity: dict[UUID, list[dict[str, Any]]] = defaultdict(list)

    if opportunity_ids:
        evidence_rows = await session.execute(
            select(OpportunityEvidence, Observation, Asset, Finding)
            .join(
                Observation,
                (Observation.tenant_id == OpportunityEvidence.tenant_id)
                & (Observation.id == OpportunityEvidence.observation_id),
            )
            .outerjoin(
                Asset,
                (Asset.tenant_id == Observation.tenant_id) & (Asset.id == Observation.asset_id),
            )
            .outerjoin(
                Finding,
                (Finding.tenant_id == OpportunityEvidence.tenant_id)
                & (Finding.id == OpportunityEvidence.finding_id),
            )
            .where(
                OpportunityEvidence.tenant_id == LOCAL_ORGANIZATION_ID,
                OpportunityEvidence.opportunity_id.in_(opportunity_ids),
            )
            .order_by(Observation.occurred_at.desc())
        )
        for evidence, observation, asset, finding in evidence_rows:
            evidence_by_opportunity[evidence.opportunity_id].append(
                {
                    "observation_id": str(observation.id),
                    "source": asset.name if asset else observation.source_key,
                    "event_type": observation.event_type,
                    "title": observation.title or observation.event_type,
                    "summary": observation.summary or "",
                    "occurred_at": observation.occurred_at,
                    "external_url": observation.external_url,
                    "finding_title": finding.title if finding else None,
                    "finding_severity": finding.severity if finding else None,
                }
            )

    items = []
    for opportunity, count in opportunities:
        items.append(
            {
                "id": str(opportunity.id),
                "title": opportunity.title,
                "description": opportunity.description,
                "status": opportunity.status,
                "score": float(opportunity.score) if opportunity.score is not None else None,
                "risk_class": opportunity.risk_class,
                "created_at": opportunity.created_at,
                "updated_at": opportunity.updated_at,
                "evidence_count": count,
                "evidence": evidence_by_opportunity[opportunity.id],
            }
        )
    return {"opportunities": items, "count": len(items)}


@router.post("/opportunities/recompute", status_code=status.HTTP_202_ACCEPTED)
async def recompute_opportunities(
    session: Annotated[AsyncSession, Depends(get_session)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, Any]:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    async with session.begin():
        try:
            record, previous_response = await claim_idempotency_key(
                session,
                tenant_id=LOCAL_ORGANIZATION_ID,
                key=idempotency_key,
                request_digest=request_hash("opportunities.recompute"),
            )
        except (ValueError, IdempotencyConflict) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        if previous_response is not None:
            return previous_response
        sources = list(
            await session.scalars(
                select(SourceConnection).where(
                    SourceConnection.tenant_id == LOCAL_ORGANIZATION_ID,
                    SourceConnection.provider == "github",
                    SourceConnection.status == "active",
                )
            )
        )
        queued = []
        skipped_active = 0
        skipped_no_observations = 0
        for source in sources:
            has_observations = await session.scalar(
                select(Observation.id)
                .where(
                    Observation.tenant_id == source.tenant_id,
                    Observation.asset_id == source.asset_id,
                    Observation.event_type == "github.workflow_run.observed",
                )
                .limit(1)
            )
            if has_observations is None:
                skipped_no_observations += 1
                continue
            job_id = await queue_github_opportunity_analysis(session, source.id)
            if job_id is None:
                skipped_active += 1
            else:
                queued.append(job_id)
        response = {
            "queued": len(queued),
            "skipped_active": skipped_active,
            "skipped_no_observations": skipped_no_observations,
            "job_ids": [str(job_id) for job_id in queued],
        }
        complete_idempotency(record, response_status=status.HTTP_202_ACCEPTED, response_body=response)
        await append_event(
            session,
            EventEnvelope(
                event_id=uuid4(),
                event_type="opportunity.analysis.requested",
                event_version=1,
                aggregate_type="opportunity_analysis_request",
                aggregate_id=uuid4(),
                aggregate_version=1,
                tenant_id=LOCAL_ORGANIZATION_ID,
                occurred_at=datetime.now(UTC),
                observed_at=datetime.now(UTC),
                actor="local-user",
                correlation_id=LOCAL_ORGANIZATION_ID,
                payload={"queued": len(queued), "source_count": len(list(sources))},
            ),
        )
    return response


@router.post("/opportunities/{opportunity_id}/triage")
async def triage_opportunity(
    opportunity_id: UUID,
    request: OpportunityTriageRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, Any]:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    status_by_action = {
        "accept": "accepted",
        "defer": "deferred",
        "reject": "rejected",
    }
    async with session.begin():
        try:
            record, previous_response = await claim_idempotency_key(
                session,
                tenant_id=LOCAL_ORGANIZATION_ID,
                key=idempotency_key,
                request_digest=request_hash(
                    "opportunities.triage",
                    {"opportunity_id": str(opportunity_id), **request.model_dump()},
                ),
            )
        except (ValueError, IdempotencyConflict) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        if previous_response is not None:
            return previous_response
        opportunity = await session.scalar(
            select(Opportunity)
            .where(
                Opportunity.id == opportunity_id,
                Opportunity.tenant_id == LOCAL_ORGANIZATION_ID,
            )
            .with_for_update()
        )
        if opportunity is None:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        if opportunity.status != "proposed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Opportunity cannot be triaged from status '{opportunity.status}'",
            )
        opportunity.status = status_by_action[request.action]
        opportunity.updated_at = func.now()
        session.add(
            AuditEvent(
                id=uuid4(),
                tenant_id=LOCAL_ORGANIZATION_ID,
                actor="local-user",
                action="opportunity.triaged",
                resource_type="opportunity",
                resource_id=str(opportunity_id),
                outcome="success",
                correlation_id=uuid4(),
                details={"action": request.action, "reason": request.reason},
            )
        )
        response = {"id": str(opportunity_id), "status": status_by_action[request.action]}
        complete_idempotency(record, response_status=status.HTTP_200_OK, response_body=response)
        await append_event(
            session,
            EventEnvelope(
                event_id=uuid4(),
                event_type="opportunity.deferred" if request.action == "defer" else "opportunity.triaged",
                event_version=1,
                aggregate_type="opportunity",
                aggregate_id=opportunity_id,
                aggregate_version=1,
                tenant_id=LOCAL_ORGANIZATION_ID,
                occurred_at=datetime.now(UTC),
                observed_at=datetime.now(UTC),
                actor="local-user",
                correlation_id=opportunity_id,
                payload={"action": request.action, "reason": request.reason},
            ),
        )
    return response
