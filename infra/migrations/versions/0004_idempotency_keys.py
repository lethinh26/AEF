"""Add idempotency key storage for side-effecting API requests.

Revision ID: 0004_idempotency_keys
Revises: 0003_opportunity_indexes
Create Date: 2026-11-22
"""

from alembic import op

revision = "0004_idempotency_keys"
down_revision = "0003_opportunity_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE infra.idempotency_keys (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            key VARCHAR(255) NOT NULL,
            request_hash VARCHAR(64) NOT NULL,
            response_status INTEGER,
            response_body JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_idempotency_keys_tenant_key UNIQUE (tenant_id, key)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_idempotency_keys_tenant_created "
        "ON infra.idempotency_keys(tenant_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS infra.idempotency_keys")
