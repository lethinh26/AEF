from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aeo_platform.config import get_settings
from aeo_platform.models import Asset, Organization, SourceConnection

LOCAL_ORGANIZATION_ID: UUID = uuid5(NAMESPACE_URL, "https://aeo.local/organizations/default")
REPOSITORY_DISPLAY_NAMES = {
    "lethinh26/Clucky": "Clucky",
    "lethinh26/Llms-System": "New-API",
}


def parse_repository_slug(value: str) -> tuple[str, str]:
    parts = value.strip().split("/")
    if len(parts) != 2 or not all(parts) or any(part in {".", ".."} for part in parts):
        raise ValueError(f"Invalid GitHub repository slug: {value!r}")
    owner, repository = parts
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    if any(character not in allowed for character in owner + repository):
        raise ValueError(f"Invalid GitHub repository slug: {value!r}")
    return owner, repository


async def ensure_local_organization(session: AsyncSession) -> Organization:
    organization = await session.get(Organization, LOCAL_ORGANIZATION_ID)
    if organization is None:
        organization = Organization(
            id=LOCAL_ORGANIZATION_ID,
            slug="local-workspace",
            name="Local Engineering Workspace",
            status="active",
        )
        session.add(organization)
        await session.flush()
    return organization


async def ensure_configured_github_sources(session: AsyncSession) -> list[SourceConnection]:
    settings = get_settings()
    organization = await ensure_local_organization(session)
    connections: list[SourceConnection] = []

    for configured_slug in settings.github_repositories:
        owner, repository = parse_repository_slug(configured_slug)
        external_id = f"{owner}/{repository}"
        canonical_url = f"https://github.com/{external_id}"
        display_name = REPOSITORY_DISPLAY_NAMES.get(external_id, external_id)
        asset = await session.scalar(
            select(Asset).where(
                Asset.tenant_id == organization.id,
                Asset.canonical_ref == canonical_url,
            )
        )
        if asset is None:
            asset = Asset(
                id=uuid5(NAMESPACE_URL, f"aeo:asset:{canonical_url}"),
                tenant_id=organization.id,
                asset_type="repository",
                name=display_name,
                canonical_ref=canonical_url,
                metadata_json={"provider": "github", "external_id": external_id},
                status="active",
            )
            session.add(asset)
            await session.flush()
        else:
            asset.name = display_name
            asset.metadata_json = {"provider": "github", "external_id": external_id}

        connection = await session.scalar(
            select(SourceConnection).where(
                SourceConnection.tenant_id == organization.id,
                SourceConnection.provider == "github",
                SourceConnection.external_id == external_id,
            )
        )
        if connection is None:
            from datetime import UTC, datetime

            connection = SourceConnection(
                id=uuid5(NAMESPACE_URL, f"aeo:source:github:{external_id}"),
                tenant_id=organization.id,
                asset_id=asset.id,
                provider="github",
                external_id=external_id,
                canonical_url=canonical_url,
                access_mode="read_only",
                status="active",
                sync_status="idle",
                sync_interval_seconds=settings.github_sync_interval_seconds,
                next_sync_at=datetime.now(UTC),
            )
            session.add(connection)
        else:
            connection.sync_interval_seconds = settings.github_sync_interval_seconds
            connection.asset_id = asset.id
        connections.append(connection)

    await session.flush()
    return connections
