# AEO — Autonomous Engineering Organization

AEO is an engineering organization platform built around goals, evidence, decisions, bounded missions and independently verified outcomes.

The canonical architecture and product specifications live in [`architechture/docs`](./architechture/docs/README.md). This repository is the new implementation built from those specifications.

## Current stage

**Foundation bootstrap.** This stage establishes the modular-monolith backend, web shell, shared domain contracts, PostgreSQL, object storage, migrations and a durable worker foundation. The first product milestone is V0 Shadow Brain: read-only observation of a small number of repositories and CI sources.

The initial checkout contained architecture documents only; no earlier V1 source tree was present. Implementation code is being created directly in this repository.

## Repository map

- `apps/api`: FastAPI entrypoint (health endpoints in the current foundation stage).
- `apps/web`: Next.js Control Center.
- `apps/worker`: database-backed background worker.
- `packages/domain-contracts`: versioned domain and event contracts.
- `packages/platform-core`: configuration, database, outbox and job primitives.
- `infra/migrations`: Alembic database migrations.
- `infra/local`: local infrastructure notes and helpers.
- `examples`: synthetic fixtures and example contracts.
- `docs/adr`: implementation architecture decisions.
- `architechture/docs`: canonical architecture and product specifications.

The initial deployment uses separate API and worker processes over a shared modular codebase. PostgreSQL is the canonical state store. A database-backed job queue and transactional outbox avoid introducing a broker before workload evidence requires one.

## Requirements

- Python 3.12 or 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 22 or newer
- [pnpm](https://pnpm.io/)
- Docker Engine/Desktop with Docker Compose

## Local development

1. Copy `.env.example` to `.env`. Change local-only passwords if needed.
   To configure a different API URL, copy the web example and edit `NEXT_PUBLIC_AEO_API_URL`:
   ```powershell
   Copy-Item apps/web/.env.local.example apps/web/.env.local
   ```
2. Start PostgreSQL and the S3-compatible object store:

   ```powershell
   docker compose up -d postgres object-store object-store-init
   ```

3. Install dependencies:

   ```powershell
   uv sync --all-packages --all-groups
   pnpm install
   ```

4. Apply database migrations:

   ```powershell
   uv run alembic -c infra/migrations/alembic.ini upgrade head
   ```

5. Start the API, worker and web app in separate terminals:

   ```powershell
   uv run --package aeo-api uvicorn aeo_api.main:app --reload --host 127.0.0.1 --port 8100
   uv run --package aeo-worker python -m aeo_worker
   pnpm dev:web
   ```

   - PostgreSQL: `127.0.0.1:55432`
   - S3 API: `http://127.0.0.1:9000`
   - API liveness: `http://127.0.0.1:8100/health/live`
   - API readiness: `http://127.0.0.1:8100/health/ready`
   - Web app: `http://localhost:3210`
   - Silo console: `http://127.0.0.1:9001`

## Checks

```powershell
uv run ruff check apps packages infra/migrations
uv run pytest
pnpm typecheck:web
pnpm lint:web
pnpm build:web
docker compose config
```

## Safety boundaries

- Initial source connectors are read-only. Production deployment is outside V0/V1 scope.
- Agent execution and repository writes are not enabled by this foundation bootstrap.
- Secrets must never enter prompts, events, logs or committed files.
- Future side-effecting tools must pass through policy enforcement and produce audit records.
- A successful mission must be supported by independent verification evidence.

## Decisions and runbooks

See [`docs/adr`](./docs/adr/) and [`docs/runbooks`](./docs/runbooks/).
