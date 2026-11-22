# Release pipeline

## Pull request policy

- Work on a short-lived feature branch; do not push directly to `main`.
- Open a pull request targeting `main`.
- Keep the PR branch up to date with `main` and wait for all six required checks: `backend`, `frontend`, `container-build`, `dependency-review`, `codeql` and `GitGuardian Security Checks`.
- `container-build` scans every final image with Trivy and blocks HIGH/CRITICAL vulnerabilities when a fix is available.
- Resolve all review conversations before merge.
- For non-admin contributors, obtain one approval from someone other than the latest pusher. Stale approvals are dismissed after new commits, and the latest push must be approved.
- Repository Admins may bypass only this approval requirement when merging through a pull request. They cannot push directly to `main` or bypass the baseline PR, required checks, security gates or review-conversation resolution. The exemption is granted to the Repository Admin role, so it applies to every repository Admin (currently only `lethinh26`).
- Merge with squash merge. GitHub deletes the source branch after merge.

The policy is enforced by two active rulesets: `Protect main - PR, review and CI` (`27829813`) and `Owner review exemption - main` (`27830084`). The first ruleset has no bypass actors; the second grants `pull_request`-only bypass to the Repository Admin role for its approval rule.

## Image publication

Every successful push to `main` triggers `.github/workflows/publish-images.yml`. It builds and publishes:

- `ghcr.io/lethinh26/aeo-api`
- `ghcr.io/lethinh26/aeo-worker`
- `ghcr.io/lethinh26/aeo-web`

Each image receives `main` and `sha-<commit>` tags. BuildKit provenance and SBOM attestations are enabled. Deployments should pin the immutable `sha-<commit>` tag rather than relying on `main`.

The first GHCR publication may create private packages. Before a remote host can pull them, either make each package public deliberately or configure a least-privilege read-only GHCR credential on that host. Do not put a registry pull token in source control.

## Local container stack

The application overlay adds API, migration, worker and web containers to the PostgreSQL/object-store services in `compose.yaml`:

```powershell
docker compose -f compose.yaml -f compose.application.yaml up --build -d
```

The web UI is available at `http://127.0.0.1:3210`; the API is bound to `127.0.0.1:8100`. The API and worker wait for the migration service to complete. Use only local credentials from `.env.example` for isolated development; replace all defaults before any shared environment.

## Staging deployment status

Staging CD is intentionally not activated until a real host and environment are supplied. Do not infer a deployment target from the developer workstation or publish a workflow that silently deploys to an unverified destination.

To activate it, provision a dedicated staging host and configure a protected GitHub Environment named `staging`. Store deployment-only SSH credentials as environment secrets, keep application secrets in a host-side environment file, and configure a read-only GHCR pull credential if the images are private. The future deploy workflow must pull the exact commit SHA, run migrations as a separate one-shot step, wait for API/web health checks, run smoke tests, and preserve a known-good image tag for rollback.

Production remains a separate manually approved release path and is outside the current V0/V1 deployment scope.
