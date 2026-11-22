# ADR 0006: Protected main and evidence-gated delivery pipeline

- Status: Accepted
- Date: 2026-11-22

## Context

The repository previously allowed direct pushes to `main`. Backend and frontend CI existed, but GitHub did not require those checks before merge. The repository also had no container packaging or image publication workflow.

The AEO architecture requires protected branches, independently reviewed changes, reproducible artifacts and evidence-backed verification. Production deployment remains outside the current V0/V1 scope.

## Decision

1. All changes to `main` must arrive through a pull request; direct pushes are blocked.
2. Two rulesets are layered on `main` to separate baseline branch protection from the review exception:
   - `Protect main - PR, review and CI` (ruleset `27829813`) requires a pull request, an up-to-date branch, resolved review conversations and all required status checks. It has no bypass actors. It also blocks force pushes, branch deletion and non-fast-forward updates, and requires linear history.
   - `Owner review exemption - main` (ruleset `27830084`) requires one approval from someone other than the latest pusher, dismisses stale approvals after new commits and requires approval of the latest push. Its only bypass actor is the `RepositoryRole` Admin role, with `pull_request` bypass mode.
3. The Admin bypass applies only to the approval ruleset and only while merging a pull request. It does not bypass the baseline ruleset, permit direct pushes, or waive required CI/security checks or review-conversation resolution. Non-admin contributors must obtain the independent approval described above.
4. The six required status checks are `backend`, `frontend`, `container-build`, `dependency-review`, `codeql` and `GitGuardian Security Checks`. The PR branch must be up to date with `main` before merge.
5. Squash merge is the only enabled merge strategy; merged feature branches are deleted automatically.
6. GitHub Actions use read-only permissions by default and third-party actions are pinned to full commit SHAs.
7. After merge, CI builds API, worker and web images and publishes immutable commit tags plus a moving `main` tag to GHCR. BuildKit provenance and SBOM attestations are enabled.
8. Production deployment is not automated. Staging deployment remains gated on a real deployment target, environment configuration and credentials.

## Consequences

- Non-admin collaborators must obtain an independent approval before merge. Repository Admins can merge their PRs without waiting for approval, but remain subject to the baseline PR and CI/security requirements.
- The approval exemption is role-based, not bound to a specific username. Any account granted Repository Admin will receive the same exemption; at the time of this decision, `lethinh26` is the only Repository Admin.
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
