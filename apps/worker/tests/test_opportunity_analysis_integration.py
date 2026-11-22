import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from aeo_platform.models import (
    Asset,
    AuditEvent,
    Finding,
    Observation,
    Opportunity,
    OpportunityEvidence,
    Organization,
    OutboxEvent,
    SourceConnection,
)
from aeo_worker.opportunity_analysis import handle_github_opportunity_analysis
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("AEO_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="Set AEO_TEST_DATABASE_URL to run PostgreSQL integration tests",
)


@pytest.mark.asyncio
async def test_analysis_expires_and_reopens_candidates_without_losing_triage_or_evidence(
    monkeypatch,
) -> None:
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    tenant_id = uuid4()
    asset_id = uuid4()
    source_id = uuid4()
    source_key = "github:aeo-test/opportunity-analysis"
    now = datetime.now(UTC)

    try:
        async with session_factory() as session:
            async with session.begin():
                session.add(
                    Organization(
                        id=tenant_id,
                        slug=f"opportunity-analysis-{tenant_id.hex}",
                        name="Opportunity Analysis Integration Test",
                    )
                )
                await session.flush()
                session.add(
                    Asset(
                        id=asset_id,
                        tenant_id=tenant_id,
                        asset_type="repository",
                        name="Opportunity Analysis Fixture",
                        canonical_ref="https://github.com/aeo-test/opportunity-analysis",
                        metadata_json={"provider": "github"},
                    )
                )
                await session.flush()
                session.add(
                    SourceConnection(
                        id=source_id,
                        tenant_id=tenant_id,
                        asset_id=asset_id,
                        provider="github",
                        external_id="aeo-test/opportunity-analysis",
                        canonical_url="https://github.com/aeo-test/opportunity-analysis",
                        access_mode="read_only",
                        status="active",
                        sync_status="idle",
                        sync_interval_seconds=900,
                        next_sync_at=now,
                    )
                )
                session.add_all(
                    [
                        Observation(
                            id=uuid4(),
                            tenant_id=tenant_id,
                            source_key=source_key,
                            source_event_id=f"run-{index}",
                            asset_id=asset_id,
                            event_type="github.workflow_run.observed",
                            title=f"Backend CI run {index}",
                            summary="Workflow Backend CI finished with failure on main",
                            external_url=f"https://github.com/aeo-test/opportunity-analysis/actions/runs/{index}",
                            occurred_at=now - timedelta(hours=index + 1),
                            observed_at=now,
                        )
                        for index in range(3)
                    ]
                )

        monkeypatch.setattr(
            "aeo_worker.opportunity_analysis.get_session_factory", lambda: session_factory
        )
        await handle_github_opportunity_analysis({"source_connection_id": str(source_id)})

        async with session_factory() as session:
            opportunity = await session.scalar(
                select(Opportunity).where(Opportunity.tenant_id == tenant_id)
            )
            finding = await session.scalar(select(Finding).where(Finding.tenant_id == tenant_id))
            assert opportunity is not None and opportunity.status == "proposed"
            assert finding is not None and finding.status == "proposed"
            opportunity_id = opportunity.id
            evidence_count = await session.scalar(
                select(func.count(OpportunityEvidence.id)).where(
                    OpportunityEvidence.tenant_id == tenant_id,
                    OpportunityEvidence.opportunity_id == opportunity_id,
                )
            )
            assert evidence_count == 3

        async with session_factory() as session:
            async with session.begin():
                observations = await session.scalars(
                    select(Observation).where(Observation.tenant_id == tenant_id)
                )
                for observation in observations:
                    if observation.source_event_id == "run-2":
                        observation.occurred_at = now - timedelta(days=8)

        await handle_github_opportunity_analysis({"source_connection_id": str(source_id)})

        async with session_factory() as session:
            opportunity = await session.get(Opportunity, opportunity_id)
            finding = await session.scalar(select(Finding).where(Finding.tenant_id == tenant_id))
            assert opportunity is not None and opportunity.status == "expired"
            assert finding is not None and finding.status == "expired"
            evidence_count = await session.scalar(
                select(func.count(OpportunityEvidence.id)).where(
                    OpportunityEvidence.tenant_id == tenant_id,
                    OpportunityEvidence.opportunity_id == opportunity_id,
                )
            )
            assert evidence_count == 3

        async with session_factory() as session:
            async with session.begin():
                observation = await session.scalar(
                    select(Observation).where(
                        Observation.tenant_id == tenant_id,
                        Observation.source_event_id == "run-2",
                    )
                )
                assert observation is not None
                observation.occurred_at = now - timedelta(hours=2)

        await handle_github_opportunity_analysis({"source_connection_id": str(source_id)})

        async with session_factory() as session:
            opportunity = await session.get(Opportunity, opportunity_id)
            assert opportunity is not None and opportunity.status == "proposed"
            evidence_count = await session.scalar(
                select(func.count(OpportunityEvidence.id)).where(
                    OpportunityEvidence.tenant_id == tenant_id,
                    OpportunityEvidence.opportunity_id == opportunity_id,
                )
            )
            assert evidence_count == 3
            opportunity.status = "accepted"
            await session.commit()

        await handle_github_opportunity_analysis({"source_connection_id": str(source_id)})

        async with session_factory() as session:
            opportunity = await session.get(Opportunity, opportunity_id)
            assert opportunity is not None and opportunity.status == "accepted"
            expired_audits = await session.scalar(
                select(func.count(AuditEvent.id)).where(
                    AuditEvent.tenant_id == tenant_id,
                    AuditEvent.action == "opportunity.expired",
                )
            )
            assert expired_audits == 1
    finally:
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    delete(OpportunityEvidence).where(OpportunityEvidence.tenant_id == tenant_id)
                )
                await session.execute(delete(Opportunity).where(Opportunity.tenant_id == tenant_id))
                await session.execute(delete(Finding).where(Finding.tenant_id == tenant_id))
                await session.execute(delete(Observation).where(Observation.tenant_id == tenant_id))
                await session.execute(delete(AuditEvent).where(AuditEvent.tenant_id == tenant_id))
                await session.execute(delete(OutboxEvent).where(OutboxEvent.tenant_id == tenant_id))
                await session.execute(
                    delete(SourceConnection).where(SourceConnection.tenant_id == tenant_id)
                )
                await session.execute(delete(Asset).where(Asset.tenant_id == tenant_id))
                await session.execute(
                    delete(Organization).where(Organization.id == tenant_id)
                )
        await engine.dispose()
