# Implementation architecture map

The repository implements the architecture in `architechture/docs` as a modular monolith. Directories are ownership boundaries; they are not separate deployable services by default.

| Area | Owns | Current foundation |
|---|---|---|
| `apps/api` | HTTP boundary, request validation, health and control-plane routes | FastAPI app and liveness/readiness endpoints |
| `apps/worker` | Durable asynchronous work | PostgreSQL job claiming, leases, heartbeat and bounded retry |
| `apps/web` | Operator Control Center | Next.js shell with live API connection status |
| `packages/domain-contracts` | Versioned events and API error shapes | Immutable Pydantic event envelope |
| `packages/platform-core` | Configuration, database sessions, outbox, jobs and artifact storage | SQLAlchemy, PostgreSQL, S3-compatible adapter |
| `infra/migrations` | Canonical relational schema evolution | Initial V0 schemas and migration |

## Trust boundaries

- The API and worker are trusted application processes; external connector payloads remain untrusted data.
- Model output will not receive direct database, filesystem or host-shell access.
- Future side effects must pass through a policy enforcement gateway before a sandbox or connector executes them.
- Artifact bytes live in object storage; their tenant, classification, size and digest belong in PostgreSQL metadata.
- V0 source access is read-only. The current bootstrap does not expose repository write or production deployment operations.

## Transaction rules

- Domain state mutation and its outbox event are committed in the same database transaction.
- Job enqueueing can participate in the caller's transaction.
- Workers claim jobs with `FOR UPDATE SKIP LOCKED`; job handlers must be idempotent because a process can die after performing work and before recording completion.
- Expired worker leases are recovered and retried up to the job's configured attempt limit.
- Consumers must record inbox deduplication with `mark_event_processed` in the same transaction as their state mutation before acknowledging event processing.

## Current implementation boundary

This bootstrap is the platform foundation, not a completed V0 Shadow Brain. Repository/CI connectors, ingestion workflows, evidence-backed world-model analysis, opportunity scoring, authentication, policy decisions and the native model provider adapter are subsequent implementation work.
