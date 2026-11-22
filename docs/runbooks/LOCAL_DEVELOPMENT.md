# Local development runbook

## First-time setup

1. Install Python 3.12/3.13, uv, Node.js 22+, pnpm and Docker Compose.
2. Copy `.env.example` to `.env` and change the local passwords.
3. Run `docker compose up -d postgres minio minio-init`.
4. Run `uv sync --all-packages --all-groups` and `pnpm install`.
5. Run `uv run alembic -c infra/migrations/alembic.ini upgrade head`.
6. Start API, worker and web using the commands in the root README.

## Health checks

- API liveness: `GET /health/live`.
- API readiness: `GET /health/ready` (requires PostgreSQL).
- PostgreSQL: `docker compose exec postgres pg_isready -U aeo -d aeo`.
- MinIO: open `http://127.0.0.1:9001`.

## Reset local infrastructure

`docker compose down -v` deletes local PostgreSQL and MinIO data volumes. Use it only when intentionally discarding local development data.
