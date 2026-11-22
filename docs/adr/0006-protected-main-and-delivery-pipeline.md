# ADR 0006: Protected main and evidence-gated delivery pipeline

- Status: Accepted
- Date: 2026-11-22

## Context

The repository previously allowed direct pushes to `main`. Backend and frontend CI existed, but GitHub did not require those checks before merge. The repository also had no container packaging or image publication workflow.

The AEO architecture requires protected branches, independently reviewed changes, reproducible artifacts and evidence-backed verification. Production deployment remains outside the current V0/V1 scope.

## Decision

1. All changes to `main` must arrive through a pull request.
2. A pull request needs one approval from someone other than its latest pusher. Stale approvals are dismissed after new commits, and review conversations must be resolved.
3. Backend, frontend, container-build, dependency-review and CodeQL checks are required before merge. The PR branch must be up to date with `main`.
4. Force pushes, branch deletion and ruleset bypass are disabled for `main`, including for administrators.
5. Squash merge is the only enabled merge strategy; merged feature branches are deleted automatically.
6. GitHub Actions use read-only permissions by default and third-party actions are pinned to full commit SHAs.
7. After merge, CI builds API, worker and web images and publishes immutable commit tags plus a moving `main` tag to GHCR. BuildKit provenance and SBOM attestations are enabled.
8. Production deployment is not automated. Staging deployment remains gated on a real deployment target, environment configuration and credentials.

## Consequences

- A second collaborator must review PRs authored by the repository owner. The repository currently has a second write-capable collaborator, so this policy is operable without an administrator bypass.
- A merge is blocked when any required check fails or is missing.
- Container images become traceable to the source commit. GHCR package visibility and staging pull credentials must be configured before remote deployment.
- The application can run as API, worker and web containers locally using `compose.application.yaml` layered over `compose.yaml`.
- No production credentials are required by PR CI or image publication.

## Staging activation prerequisites

- A dedicated staging host and deployment directory.
- A staging-only SSH identity or equivalent deployment mechanism.
- A host-side environment file containing database, object-store and application secrets.
- A read-only GHCR pull credential if the packages remain private.
- A TLS/reverse-proxy plan and a health-check/rollback procedure.

Until these prerequisites exist, the pipeline stops after verified image publication.
