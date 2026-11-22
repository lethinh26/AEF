"""Align the live foundation schema with the current ORM metadata.

Revision ID: 0003_opportunity_indexes
Revises: 0002_github_observer
Create Date: 2026-11-22
"""

from alembic import op

revision = "0003_opportunity_indexes"
down_revision = "0002_github_observer"
branch_labels = None
depends_on = None


def _rename_constraint(schema: str, table: str, old_name: str, new_name: str) -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conrelid = '{schema}.{table}'::regclass AND conname = '{old_name}'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conrelid = '{schema}.{table}'::regclass AND conname = '{new_name}'
            ) THEN
                ALTER TABLE {schema}.{table}
                    RENAME CONSTRAINT {old_name} TO {new_name};
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    # Older local volumes were created before these constraints received
    # explicit names. Normalize them without rebuilding or dropping data.
    _rename_constraint(
        "identity", "organizations", "organizations_id_slug_key", "uq_organizations_id_slug"
    )
    _rename_constraint(
        "infra",
        "artifact_metadata",
        "artifact_metadata_tenant_id_storage_key_key",
        "uq_artifact_metadata_tenant_storage_key",
    )
    _rename_constraint(
        "infra",
        "outbox_events",
        "outbox_events_aggregate_type_aggregate_id_aggregate_version_key",
        "uq_outbox_aggregate_version",
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_findings_tenant_status "
        "ON analysis.findings (tenant_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_opportunities_tenant_status "
        "ON analysis.opportunities (tenant_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_opportunity_evidence_tenant_opportunity "
        "ON analysis.opportunity_evidence (tenant_id, opportunity_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS analysis.ix_opportunity_evidence_tenant_opportunity")
    op.execute("DROP INDEX IF EXISTS analysis.ix_opportunities_tenant_status")
    op.execute("DROP INDEX IF EXISTS analysis.ix_findings_tenant_status")
