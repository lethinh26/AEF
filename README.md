# AEO — Autonomous Engineering Organization

AEO is an engineering organization platform built around goals, evidence, decisions, bounded missions and independently verified outcomes.

The canonical architecture and product specifications live in [`architechture/docs`](./architechture/docs/README.md). This repository is the new implementation built from those specifications.

## Current stage

**V0 Shadow Brain — GitHub observer and first deterministic Opportunity Inbox.** The foundation includes a read-only GitHub connector, durable polling jobs, PostgreSQL observation metadata, S3-compatible evidence artifacts, Sources/Evidence views and a reproducible rule for repeated CI failures. The initial sources are `lethinh26/Clucky` and `lethinh26/Llms-System` (New-API). Clucky can sync anonymously; private New-API requires a dedicated fine-grained read-only token. See [`docs/runbooks/GITHUB_OBSERVER.md`](./docs/runbooks/GITHUB_OBSERVER.md).

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
- `docs/runbooks/GITHUB_OBSERVER.md`: GitHub read-only token setup and observer operations.

The initial deployment uses separate API and worker processes over a shared modular codebase. PostgreSQL is the canonical state store. A database-backed job queue and transactional outbox avoid introducing a broker before workload evidence requires one.

## Requirements

- Python 3.12 or 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 24 or newer
- [pnpm](https://pnpm.io/)
- Docker Engine/Desktop with Docker Compose

## Local development

1. Copy `.env.example` to `.env`. Change local-only passwords if needed.
   To configure the API URL used by the Next.js server-side health proxy, copy the web example and edit `AEO_API_INTERNAL_URL`:
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

   Clucky is public and can sync anonymously. To enable private New-API observation, configure `AEO_GITHUB_TOKEN` in `.env` using a fine-grained token restricted to the two selected repositories and read-only Metadata, Contents, Issues, Pull requests and Actions permissions. Restart API and worker after changing it.

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

## Containerized application stack

The base Compose file starts local infrastructure only. To run the API, migration step, worker and web app as containers as well:

```powershell
docker compose -f compose.yaml -f compose.application.yaml up --build -d
```

The application overlay binds the API and web ports to loopback only. The migration container must complete before the API and worker start. Use non-default credentials for any shared environment.

## GitHub delivery pipeline

All changes to `main` go through a pull request; direct pushes are blocked. The baseline main ruleset requires the PR branch to be up to date, all review conversations resolved, and six checks to pass: `backend`, `frontend`, `container-build` (including Trivy HIGH/CRITICAL image scanning), `dependency-review`, `codeql` and `GitGuardian Security Checks`.

Non-admin contributors need one approval from someone other than the latest pusher; stale approvals are dismissed and the latest push must be approved. Repository Admins may bypass this approval requirement only when merging through a pull request. This exemption does not allow direct pushes or bypass the baseline PR, CI/security or conversation-resolution requirements. The exemption is role-based and therefore applies to every Repository Admin; `lethinh26` is currently the repository's only Admin. Dependabot monitors Python, pnpm, Docker base images and GitHub Actions. After merge, GitHub Actions publishes API, worker and web images to GHCR with commit-specific tags, provenance and SBOM attestations. Staging deployment is not enabled until a real staging host and credentials are provisioned; production deployment is outside the current V0/V1 scope. See [`docs/runbooks/release-pipeline.md`](./docs/runbooks/release-pipeline.md).

## Safety boundaries

- Initial source connectors are read-only. The GitHub connector fetches metadata only; it does not download source files, diffs, workflow logs or artifacts. Production deployment is outside V0/V1 scope.
- Agent execution and repository writes are not enabled by this foundation bootstrap.
- Secrets must never enter prompts, events, logs or committed files.
- Future side-effecting tools must pass through policy enforcement and produce audit records.
- A successful mission must be supported by independent verification evidence.

## Decisions and runbooks

See [`docs/adr`](./docs/adr/) and [`docs/runbooks`](./docs/runbooks/).
