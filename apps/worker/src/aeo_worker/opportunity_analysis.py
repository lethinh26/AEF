import hashlib
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import structlog
from aeo_contracts.events import EventEnvelope
from aeo_platform.db import get_session_factory
from aeo_platform.models import (
    AuditEvent,
    Finding,
    Observation,
    Opportunity,
    OpportunityEvidence,
    SourceConnection,
)
from aeo_platform.outbox import append_event
from sqlalchemy import case, select
from sqlalchemy.dialects.postgresql import insert

logger = structlog.get_logger(__name__)
CI_FAILURE_WINDOW = timedelta(days=7)
MINIMUM_REPEATED_FAILURES = 3


@dataclass(frozen=True)
class CIFailureCluster:
    asset_id: UUID
    workflow_name: str
    branches: frozenset[str]
    observations: tuple[Observation, ...]

    @property
    def first_seen_at(self) -> datetime:
        return min(item.occurred_at for item in self.observations if item.occurred_at)

    @property
    def last_seen_at(self) -> datetime:
        return max(item.occurred_at for item in self.observations if item.occurred_at)


def build_ci_failure_clusters(
    observations: Iterable[Observation],
    *,
    minimum_failures: int = MINIMUM_REPEATED_FAILURES,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> list[CIFailureCluster]:
    grouped: dict[tuple[UUID, str], list[tuple[Observation, str]]] = defaultdict(list)
    seen_events: set[tuple[UUID, str, str]] = set()
    for observation in observations:
        if observation.asset_id is None or not observation.summary:
            continue
        occurred_at = getattr(observation, "occurred_at", None)
        if occurred_at is None:
            continue
        if window_start is not None and occurred_at < window_start:
            continue
        if window_end is not None and occurred_at > window_end:
            continue
        prefix, separator, branch = observation.summary.partition(" finished with failure on ")
        if not separator or not prefix.startswith("Workflow ") or not branch:
            continue
        workflow_name = prefix.removeprefix("Workflow ").strip()
        if workflow_name:
            event_key = getattr(observation, "source_event_id", None) or str(observation.id)
            dedup_key = (observation.asset_id, workflow_name, event_key)
            if dedup_key in seen_events:
                continue
            seen_events.add(dedup_key)
            grouped[(observation.asset_id, workflow_name)].append((observation, branch.strip()))

    clusters: list[CIFailureCluster] = []
    for (asset_id, workflow_name), entries in grouped.items():
        if len(entries) < minimum_failures:
            continue
        clusters.append(
            CIFailureCluster(
                asset_id=asset_id,
                workflow_name=workflow_name,
                branches=frozenset(branch for _, branch in entries),
                observations=tuple(item for item, _ in entries),
            )
        )
    return sorted(clusters, key=lambda cluster: len(cluster.observations), reverse=True)


def _fingerprint(asset_id: UUID, workflow_name: str) -> str:
    workflow_digest = hashlib.sha256(workflow_name.casefold().encode("utf-8")).hexdigest()[:20]
    return f"ci-failure-cluster:{asset_id}:{workflow_digest}"


def ci_failure_severity(failure_count: int) -> str:
    return "high" if failure_count >= 10 else "medium"


def ci_failure_score(failure_count: int) -> float:
    return min(100.0, 40.0 + (failure_count * 5.0))


def _evidence_id(opportunity_id: UUID, observation_id: UUID) -> UUID:
    return uuid5(NAMESPACE_URL, f"aeo:opportunity-evidence:{opportunity_id}:{observation_id}")


async def handle_github_opportunity_analysis(payload: dict) -> None:
    source_id = UUID(payload["source_connection_id"])
    factory = get_session_factory()
    now = datetime.now(UTC)
    window_start = now - CI_FAILURE_WINDOW

    async with factory() as session:
        async with session.begin():
            source = await session.scalar(
                select(SourceConnection).where(SourceConnection.id == source_id)
            )
            if source is None:
                raise ValueError("GitHub source connection does not exist")
            tenant_id = source.tenant_id
            repository = source.external_id
            observations = await session.scalars(
                select(Observation).where(
                    Observation.tenant_id == tenant_id,
                    Observation.asset_id == source.asset_id,
                    Observation.event_type == "github.workflow_run.observed",
                    Observation.occurred_at >= window_start,
                    Observation.summary.like("% finished with failure on %"),
                )
            )
            clusters = build_ci_failure_clusters(
                observations, window_start=window_start, window_end=now
            )

            active_fingerprints = {
                _fingerprint(cluster.asset_id, cluster.workflow_name) for cluster in clusters
            }

            for cluster in clusters:
                count = len(cluster.observations)
                branch_count = len(cluster.branches)
                fingerprint = _fingerprint(cluster.asset_id, cluster.workflow_name)
                finding_id = uuid5(NAMESPACE_URL, f"aeo:finding:{tenant_id}:{fingerprint}")
                opportunity_id = uuid5(
                    NAMESPACE_URL, f"aeo:opportunity:{tenant_id}:{fingerprint}"
                )
                severity = ci_failure_severity(count)
                finding_title = f"Recurring CI failures: {cluster.workflow_name}"
                finding_summary = (
                    f"Observed {count} failed workflow runs in the last 7 days across "
                    f"{branch_count} branch(es) in {repository}. This is a repeated-failure "
                    "signal, not a root-cause determination."
                )
                opportunity_title = f"Investigate recurring CI failures in {cluster.workflow_name}"
                opportunity_description = (
                    f"Why now: {count} failed runs were observed within seven days across "
                    f"{branch_count} branch(es). The evidence establishes repetition only; "
                    "it does not establish why the workflow failed.\n\n"
                    "Recommended next step: perform a read-only investigation by comparing "
                    "failed run metadata and commit timelines. Do not make "
                    "code changes or create a branch from this opportunity.\n\n"
                    "Competing hypotheses: flaky tests; dependency or runner/environment "
                    "instability; a genuine code regression. Missing evidence: redacted job "
                    "logs, test reports and a known-good comparison run."
                )
                score = ci_failure_score(count)

                await session.execute(
                    insert(Finding)
                    .values(
                        id=finding_id,
                        tenant_id=tenant_id,
                        finding_type="recurring_ci_failure",
                        fingerprint=fingerprint,
                        title=finding_title,
                        summary=finding_summary,
                        severity=severity,
                        confidence=0.65,
                        status="proposed",
                        first_seen_at=cluster.first_seen_at,
                        last_seen_at=cluster.last_seen_at,
                    )
                    .on_conflict_do_update(
                        index_elements=["tenant_id", "fingerprint"],
                        set_={
                            "title": finding_title,
                            "summary": finding_summary,
                            "severity": severity,
                            "confidence": 0.65,
                            "last_seen_at": cluster.last_seen_at,
                            "status": case(
                                (Finding.status == "expired", "proposed"),
                                else_=Finding.status,
                            ),
                        },
                    )
                )
                await session.execute(
                    insert(Opportunity)
                    .values(
                        id=opportunity_id,
                        tenant_id=tenant_id,
                        title=opportunity_title,
                        description=opportunity_description,
                        status="proposed",
                        score=score,
                        risk_class="R0",
                    )
                    .on_conflict_do_update(
                        index_elements=["id"],
                        set_={
                            "title": opportunity_title,
                            "description": opportunity_description,
                            "score": score,
                            "updated_at": now,
                            "status": case(
                                (Opportunity.status == "expired", "proposed"),
                                else_=Opportunity.status,
                            ),
                        },
                    )
                )

                evidence_rows = [
                    {
                        "id": _evidence_id(opportunity_id, observation.id),
                        "tenant_id": tenant_id,
                        "opportunity_id": opportunity_id,
                        "finding_id": finding_id,
                        "observation_id": observation.id,
                    }
                    for observation in cluster.observations
                ]
                await session.execute(
                    insert(OpportunityEvidence).values(evidence_rows).on_conflict_do_nothing(
                        index_elements=["id"]
                    )
                )
                await append_event(
                    session,
                    EventEnvelope(
                        event_id=uuid5(
                            NAMESPACE_URL,
                            f"aeo:event:opportunity-proposed:{opportunity_id}:{cluster.last_seen_at.isoformat()}",
                        ),
                        event_type="opportunity.proposed",
                        event_version=1,
                        aggregate_type="opportunity",
                        aggregate_id=opportunity_id,
                        aggregate_version=1,
                        tenant_id=tenant_id,
                        occurred_at=cluster.last_seen_at,
                        observed_at=now,
                        actor="service:opportunity-engine",
                        correlation_id=opportunity_id,
                        payload={
                            "finding_id": str(finding_id),
                            "repository": repository,
                            "finding_type": "recurring_ci_failure",
                            "workflow": cluster.workflow_name,
                            "failed_runs": count,
                            "branches": branch_count,
                        },
                    ),
                )
                session.add(
                    AuditEvent(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        actor="service:opportunity-engine",
                        action="opportunity.generated",
                        resource_type="opportunity",
                        resource_id=str(opportunity_id),
                        outcome="success",
                        correlation_id=uuid4(),
                        details={
                            "repository": repository,
                            "finding_type": "recurring_ci_failure",
                            "workflow": cluster.workflow_name,
                            "failed_runs": count,
                            "branches": branch_count,
                            "window_days": 7,
                            "generation_mode": "deterministic_rule",
                        },
                    )
                )

            existing_findings = await session.scalars(
                select(Finding).where(
                    Finding.tenant_id == tenant_id,
                    Finding.finding_type == "recurring_ci_failure",
                    Finding.fingerprint.like(f"ci-failure-cluster:{source.asset_id}:%"),
                )
            )
            for finding in existing_findings:
                if finding.fingerprint in active_fingerprints:
                    continue
                if finding.status == "proposed":
                    finding.status = "expired"

                related_opportunities = await session.scalars(
                    select(Opportunity)
                    .join(
                        OpportunityEvidence,
                        (OpportunityEvidence.tenant_id == Opportunity.tenant_id)
                        & (OpportunityEvidence.opportunity_id == Opportunity.id),
                    )
                    .where(
                        Opportunity.tenant_id == tenant_id,
                        OpportunityEvidence.finding_id == finding.id,
                    )
                )
                for opportunity in related_opportunities:
                    if opportunity.status != "proposed":
                        continue
                    opportunity.status = "expired"
                    opportunity.updated_at = now
                    await append_event(
                        session,
                        EventEnvelope(
                            event_id=uuid4(),
                            event_type="opportunity.expired",
                            event_version=1,
                            aggregate_type="opportunity",
                            aggregate_id=opportunity.id,
                            aggregate_version=1,
                            tenant_id=tenant_id,
                            occurred_at=now,
                            observed_at=now,
                            actor="service:opportunity-engine",
                            correlation_id=opportunity.id,
                            payload={
                                "finding_id": str(finding.id),
                                "repository": repository,
                                "reason": "failure_threshold_no_longer_met_in_rolling_window",
                            },
                        ),
                    )
                    session.add(
                        AuditEvent(
                            id=uuid4(),
                            tenant_id=tenant_id,
                            actor="service:opportunity-engine",
                            action="opportunity.expired",
                            resource_type="opportunity",
                            resource_id=str(opportunity.id),
                            outcome="success",
                            correlation_id=uuid4(),
                            details={
                                "repository": repository,
                                "finding_type": "recurring_ci_failure",
                                "fingerprint": finding.fingerprint,
                                "reason": "failure_threshold_no_longer_met_in_rolling_window",
                                "window_days": 7,
                            },
                        )
                    )

    logger.info(
        "github_opportunity_analysis_completed",
        repository=repository,
        clusters=len(clusters),
        candidates=sum(len(cluster.observations) for cluster in clusters),
    )
