"""Create the initial AEO V0 foundation schema.

Revision ID: 0001_foundation
Revises:
Create Date: 2026-11-22
"""

from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    script = """
        CREATE SCHEMA IF NOT EXISTS identity;
        CREATE SCHEMA IF NOT EXISTS planning;
        CREATE SCHEMA IF NOT EXISTS world;
        CREATE SCHEMA IF NOT EXISTS analysis;
        CREATE SCHEMA IF NOT EXISTS portfolio;
        CREATE SCHEMA IF NOT EXISTS missions;
        CREATE SCHEMA IF NOT EXISTS execution;
        CREATE SCHEMA IF NOT EXISTS quality;
        CREATE SCHEMA IF NOT EXISTS knowledge;
        CREATE SCHEMA IF NOT EXISTS security;
        CREATE SCHEMA IF NOT EXISTS infra;

        CREATE TABLE identity.organizations (
            id UUID PRIMARY KEY,
            slug VARCHAR(100) NOT NULL UNIQUE,
            name VARCHAR(200) NOT NULL,
            status VARCHAR(24) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_organizations_id_slug UNIQUE (id, slug)
        );

        CREATE TABLE identity.users (
            id UUID PRIMARY KEY,
            email VARCHAR(320) NOT NULL UNIQUE,
            display_name VARCHAR(200) NOT NULL,
            status VARCHAR(24) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE identity.memberships (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            user_id UUID NOT NULL REFERENCES identity.users(id),
            role VARCHAR(40) NOT NULL,
            status VARCHAR(24) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, user_id)
        );

        CREATE TABLE identity.assets (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            asset_type VARCHAR(60) NOT NULL,
            name VARCHAR(240) NOT NULL,
            canonical_ref VARCHAR(1024) NOT NULL,
            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
            status VARCHAR(24) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, canonical_ref)
        );

        CREATE TABLE identity.asset_acl (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL,
            asset_id UUID NOT NULL,
            principal_type VARCHAR(40) NOT NULL,
            principal_id UUID NOT NULL,
            permission VARCHAR(40) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            FOREIGN KEY (tenant_id, asset_id)
                REFERENCES identity.assets(tenant_id, id) ON DELETE CASCADE,
            UNIQUE (tenant_id, asset_id, principal_type, principal_id, permission)
        );

        CREATE TABLE planning.goals (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            owner_id UUID NOT NULL REFERENCES identity.users(id),
            current_version INTEGER NOT NULL DEFAULT 1 CHECK (current_version > 0),
            status VARCHAR(24) NOT NULL DEFAULT 'draft',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id)
        );

        CREATE TABLE planning.goal_versions (
            tenant_id UUID NOT NULL,
            goal_id UUID NOT NULL,
            version INTEGER NOT NULL CHECK (version > 0),
            spec JSONB NOT NULL,
            created_by UUID NOT NULL REFERENCES identity.users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (goal_id, version),
            FOREIGN KEY (tenant_id, goal_id)
                REFERENCES planning.goals(tenant_id, id) ON DELETE CASCADE
        );

        CREATE TABLE planning.goal_measurements (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            goal_id UUID NOT NULL,
            metric_key VARCHAR(120) NOT NULL,
            observed_value JSONB NOT NULL,
            measured_at TIMESTAMPTZ NOT NULL,
            source_ref VARCHAR(1024),
            FOREIGN KEY (tenant_id, goal_id)
                REFERENCES planning.goals(tenant_id, id) ON DELETE CASCADE
        );
        CREATE INDEX ix_goal_measurements_goal_time
            ON planning.goal_measurements(tenant_id, goal_id, measured_at DESC);

        CREATE TABLE world.observations (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            source_key VARCHAR(200) NOT NULL,
            source_event_id VARCHAR(300),
            asset_id UUID,
            event_type VARCHAR(160) NOT NULL,
            occurred_at TIMESTAMPTZ,
            observed_at TIMESTAMPTZ NOT NULL,
            payload_ref VARCHAR(1024),
            payload_digest VARCHAR(80),
            classification VARCHAR(24) NOT NULL DEFAULT 'internal',
            status VARCHAR(24) NOT NULL DEFAULT 'accepted',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            FOREIGN KEY (tenant_id, asset_id)
                REFERENCES identity.assets(tenant_id, id),
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, source_key, source_event_id)
        );
        CREATE INDEX ix_observations_tenant_observed
            ON world.observations(tenant_id, observed_at DESC);
        CREATE INDEX ix_observations_asset_time
            ON world.observations(tenant_id, asset_id, observed_at DESC);

        CREATE TABLE world.claims (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            subject_ref VARCHAR(1024) NOT NULL,
            predicate VARCHAR(160) NOT NULL,
            object_value JSONB NOT NULL,
            confidence NUMERIC(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
            status VARCHAR(24) NOT NULL DEFAULT 'active',
            first_seen_at TIMESTAMPTZ NOT NULL,
            last_seen_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id)
        );

        CREATE TABLE world.claim_evidence (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL,
            claim_id UUID NOT NULL,
            observation_id UUID NOT NULL,
            evidence_role VARCHAR(40) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            FOREIGN KEY (tenant_id, claim_id)
                REFERENCES world.claims(tenant_id, id) ON DELETE CASCADE,
            FOREIGN KEY (tenant_id, observation_id)
                REFERENCES world.observations(tenant_id, id) ON DELETE CASCADE,
            UNIQUE (claim_id, observation_id, evidence_role)
        );

        CREATE TABLE world.source_cursors (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            source_key VARCHAR(200) NOT NULL,
            cursor JSONB NOT NULL DEFAULT '{}'::jsonb,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, source_key)
        );

        CREATE TABLE analysis.findings (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            finding_type VARCHAR(100) NOT NULL,
            fingerprint VARCHAR(200) NOT NULL,
            title VARCHAR(300) NOT NULL,
            summary TEXT NOT NULL,
            severity VARCHAR(24) NOT NULL,
            confidence NUMERIC(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
            status VARCHAR(24) NOT NULL DEFAULT 'proposed',
            first_seen_at TIMESTAMPTZ NOT NULL,
            last_seen_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, fingerprint),
            UNIQUE (tenant_id, id)
        );

        CREATE TABLE analysis.opportunities (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            goal_id UUID,
            title VARCHAR(300) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(24) NOT NULL DEFAULT 'proposed',
            score NUMERIC(8,4),
            risk_class VARCHAR(24),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, goal_id)
                REFERENCES planning.goals(tenant_id, id)
        );

        CREATE TABLE analysis.opportunity_evidence (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL,
            opportunity_id UUID NOT NULL,
            finding_id UUID,
            observation_id UUID,
            evidence_ref VARCHAR(1024),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            FOREIGN KEY (tenant_id, opportunity_id)
                REFERENCES analysis.opportunities(tenant_id, id) ON DELETE CASCADE,
            FOREIGN KEY (tenant_id, finding_id)
                REFERENCES analysis.findings(tenant_id, id),
            FOREIGN KEY (tenant_id, observation_id)
                REFERENCES world.observations(tenant_id, id),
            CHECK (finding_id IS NOT NULL OR observation_id IS NOT NULL OR evidence_ref IS NOT NULL)
        );

        CREATE TABLE infra.outbox_events (
            id UUID PRIMARY KEY,
            event_type VARCHAR(160) NOT NULL,
            event_version SMALLINT NOT NULL DEFAULT 1 CHECK (event_version > 0),
            aggregate_type VARCHAR(80) NOT NULL,
            aggregate_id UUID NOT NULL,
            aggregate_version INTEGER NOT NULL CHECK (aggregate_version > 0),
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            occurred_at TIMESTAMPTZ NOT NULL,
            observed_at TIMESTAMPTZ NOT NULL,
            actor VARCHAR(160) NOT NULL,
            correlation_id UUID NOT NULL,
            causation_id UUID,
            policy_decision_id UUID,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            payload_ref VARCHAR(1024),
            payload_digest VARCHAR(80),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            published_at TIMESTAMPTZ,
            CONSTRAINT uq_outbox_aggregate_version
                UNIQUE (aggregate_type, aggregate_id, aggregate_version)
        );
        CREATE INDEX ix_outbox_unpublished ON infra.outbox_events(created_at)
            WHERE published_at IS NULL;
        CREATE INDEX ix_outbox_event_type_created
            ON infra.outbox_events(event_type, created_at);

        CREATE TABLE infra.inbox_dedup (
            consumer_id VARCHAR(160) NOT NULL,
            event_id UUID NOT NULL,
            processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (consumer_id, event_id)
        );

        CREATE TABLE infra.jobs (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            job_type VARCHAR(160) NOT NULL,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            status VARCHAR(24) NOT NULL DEFAULT 'queued'
                CONSTRAINT ck_jobs_status
                CHECK (status IN ('queued', 'running', 'retrying', 'completed', 'dead')),
            attempts INTEGER NOT NULL DEFAULT 0
                CONSTRAINT ck_jobs_attempts_nonnegative CHECK (attempts >= 0),
            max_attempts INTEGER NOT NULL DEFAULT 5
                CONSTRAINT ck_jobs_max_attempts_positive CHECK (max_attempts > 0),
            available_at TIMESTAMPTZ NOT NULL,
            locked_at TIMESTAMPTZ,
            locked_by VARCHAR(160),
            last_error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            completed_at TIMESTAMPTZ
        );
        CREATE INDEX ix_jobs_claim ON infra.jobs(status, available_at, created_at);
        CREATE INDEX ix_jobs_tenant_status ON infra.jobs(tenant_id, status);

        CREATE TABLE infra.audit_events (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            actor VARCHAR(160) NOT NULL,
            action VARCHAR(160) NOT NULL,
            resource_type VARCHAR(80) NOT NULL,
            resource_id VARCHAR(160) NOT NULL,
            outcome VARCHAR(32) NOT NULL,
            reason_code VARCHAR(120),
            correlation_id UUID NOT NULL,
            details JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX ix_audit_tenant_created
            ON infra.audit_events(tenant_id, created_at DESC);
        CREATE INDEX ix_audit_resource
            ON infra.audit_events(resource_type, resource_id);

        CREATE TABLE infra.artifact_metadata (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES identity.organizations(id),
            storage_key VARCHAR(1024) NOT NULL,
            media_type VARCHAR(200) NOT NULL,
            size_bytes BIGINT NOT NULL CHECK (size_bytes >= 0),
            sha256 VARCHAR(64) NOT NULL,
            classification VARCHAR(24) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_artifact_metadata_tenant_storage_key UNIQUE (tenant_id, storage_key)
        );
        """
    for statement in script.split(";"):
        if statement.strip():
            op.execute(statement)


def downgrade() -> None:
    script = """
        DROP SCHEMA IF EXISTS infra CASCADE;
        DROP SCHEMA IF EXISTS analysis CASCADE;
        DROP SCHEMA IF EXISTS world CASCADE;
        DROP SCHEMA IF EXISTS planning CASCADE;
        DROP SCHEMA IF EXISTS identity CASCADE;
        DROP SCHEMA IF EXISTS portfolio CASCADE;
        DROP SCHEMA IF EXISTS missions CASCADE;
        DROP SCHEMA IF EXISTS execution CASCADE;
        DROP SCHEMA IF EXISTS quality CASCADE;
        DROP SCHEMA IF EXISTS knowledge CASCADE;
        DROP SCHEMA IF EXISTS security CASCADE;
        """
    for statement in script.split(";"):
        if statement.strip():
            op.execute(statement)
