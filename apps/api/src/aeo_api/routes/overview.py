from typing import Annotated, Any

from aeo_platform.bootstrap import LOCAL_ORGANIZATION_ID, ensure_configured_github_sources
from aeo_platform.config import get_settings
from aeo_platform.db import get_session
from aeo_platform.models import Observation, Opportunity, SourceConnection
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1", tags=["overview"])


@router.get("/overview")
async def get_overview(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    async with session.begin():
        await ensure_configured_github_sources(session)

    sources_configured = await session.scalar(
        select(func.count(SourceConnection.id)).where(
            SourceConnection.tenant_id == LOCAL_ORGANIZATION_ID,
            SourceConnection.status == "active",
        )
    )
    sources_synced = await session.scalar(
        select(func.count(SourceConnection.id)).where(
            SourceConnection.tenant_id == LOCAL_ORGANIZATION_ID,
            SourceConnection.status == "active",
            SourceConnection.last_sync_completed_at.is_not(None),
        )
    )
    observation_count = await session.scalar(
        select(func.count(Observation.id)).where(
            Observation.tenant_id == LOCAL_ORGANIZATION_ID
        )
    )
    opportunity_count = await session.scalar(
        select(func.count(Opportunity.id)).where(
            Opportunity.tenant_id == LOCAL_ORGANIZATION_ID,
            Opportunity.status == "proposed",
        )
    )
    primary_source = await session.scalar(
        select(SourceConnection)
        .where(
            SourceConnection.tenant_id == LOCAL_ORGANIZATION_ID,
            SourceConnection.provider == "github",
        )
        .order_by(SourceConnection.external_id)
        .limit(1)
    )
    settings = get_settings()
    return {
        "sources_configured": sources_configured or 0,
        "sources_synced": sources_synced or 0,
        "sources_waiting_for_credential": (
            0 if settings.github_token_value else len(settings.github_repositories) - len(settings.github_public_repositories)
        ),
        "observations": observation_count or 0,
        "opportunities_pending": opportunity_count or 0,
        "primary_source_name": primary_source.external_id if primary_source else None,
        "primary_source_status": primary_source.status if primary_source else None,
        "primary_source_sync_status": primary_source.sync_status if primary_source else None,
        "mode": "read_only",
    }
