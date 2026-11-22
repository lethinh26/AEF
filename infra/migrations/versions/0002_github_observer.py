"""Add read-only GitHub source connections and richer observation metadata.

Revision ID: 0002_github_observer
Revises: 0001_foundation
Create Date: 2026-11-22
"""

from alembic import op

revision = "0002_github_observer"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE world.source_connections (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id) ON DELETE CASCADE,
            asset_id UUID NOT NULL,
            provider VARCHAR(40) NOT NULL,
            external_id VARCHAR(300) NOT NULL,
            canonical_url VARCHAR(1024) NOT NULL,
            access_mode VARCHAR(24) NOT NULL DEFAULT 'read_only'
                CONSTRAINT ck_source_connection_read_only CHECK (access_mode = 'read_only'),
            status VARCHAR(24) NOT NULL DEFAULT 'active'
                CONSTRAINT ck_source_connection_status CHECK (status IN ('active', 'paused', 'error')),
            sync_status VARCHAR(24) NOT NULL DEFAULT 'idle'
                CONSTRAINT ck_source_connection_sync_status CHECK (sync_status IN ('idle', 'queued', 'running', 'failed')),
            sync_interval_seconds INTEGER NOT NULL DEFAULT 900
                CONSTRAINT ck_source_connection_sync_interval CHECK (sync_interval_seconds BETWEEN 60 AND 86400),
            next_sync_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_sync_started_at TIMESTAMPTZ,
            last_sync_completed_at TIMESTAMPTZ,
            last_observation_at TIMESTAMPTZ,
            last_error_code VARCHAR(120),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_source_connection UNIQUE (tenant_id, provider, external_id),
            CONSTRAINT fk_source_connection_asset
                FOREIGN KEY (tenant_id, asset_id) REFERENCES identity.assets(tenant_id, id)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_source_connections_due ON world.source_connections(status, sync_status, next_sync_at)"
    )
    op.execute("ALTER TABLE world.observations ADD COLUMN title VARCHAR(500)")
    op.execute("ALTER TABLE world.observations ADD COLUMN summary TEXT")
    op.execute("ALTER TABLE world.observations ADD COLUMN external_url VARCHAR(1024)")


def downgrade() -> None:
    op.execute("ALTER TABLE world.observations DROP COLUMN IF EXISTS external_url")
    op.execute("ALTER TABLE world.observations DROP COLUMN IF EXISTS summary")
    op.execute("ALTER TABLE world.observations DROP COLUMN IF EXISTS title")
    op.execute("DROP TABLE IF EXISTS world.source_connections")
