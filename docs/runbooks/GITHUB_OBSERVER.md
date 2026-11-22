# GitHub Shadow Observer runbook

## Selected repositories

- `lethinh26/Clucky` — public.
- `lethinh26/Llms-System` — private New-API repository.

The configured connector is read-only. It observes repository metadata, recent commits, pull requests, issues and GitHub Actions run metadata. It does not download source code, diffs, workflow logs or artifacts, and it cannot create branches, commits, issues or pull requests. Clucky is public and can be observed anonymously; New-API is private and requires the token below.

## Create the credential

Create a GitHub fine-grained personal access token for the account that can read both repositories:

1. Open GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens.
2. Select only `lethinh26/Clucky` and `lethinh26/Llms-System` under repository access.
3. Grant repository permissions:
   - Metadata: Read-only (GitHub requires this permission).
   - Contents: Read-only.
   - Issues: Read-only.
   - Pull requests: Read-only.
   - Actions: Read-only.
4. Do not grant any write permission. Set an expiry and rotate the token when it expires.
5. Add the token to the ignored local `.env` file as `AEO_GITHUB_TOKEN=...`. Do not paste it into chat, source files, command-line arguments or logs.

The existing `gh` CLI login is intentionally not reused: its `repo` scope is broader than the AEO observer needs.

## Start and sync

For local process development, restart the API and worker after editing `.env` so both load the new credential. For the container stack:

```powershell
docker compose -f compose.yaml -f compose.application.yaml up --build -d
```

Open `http://127.0.0.1:3210/sources` and choose **Sync repositories**. The worker also polls active sources every 15 minutes. Evidence appears at `http://127.0.0.1:3210/evidence`.

API checks:

```powershell
Invoke-RestMethod http://127.0.0.1:8100/v1/sources
Invoke-RestMethod http://127.0.0.1:8100/v1/observations?limit=20
Invoke-RestMethod http://127.0.0.1:8100/v1/opportunities
```

## Initial deterministic opportunity rule

The first inbox rule creates a candidate when the same repository/workflow has at least three failed runs in a rolling seven-day window. It groups across branches but retains each branch and observation as evidence. The score is a transparent heuristic, not an expected-value estimate; the confidence value is not calibrated. The candidate recommends read-only investigation only and must not be treated as a root-cause diagnosis or authorization to change code. See [ADR 0008](../adr/0008-deterministic-ci-opportunity-seeding.md).

Candidates that fall below the threshold as observations leave the seven-day window are marked `expired` only while still proposed. Their evidence remains available. If the signal returns, an expired candidate can reopen; accepted, deferred and rejected decisions are preserved. Recompute and sync scheduling skip an already active job for the same source.

## Troubleshooting

- `github_token_missing`: configure `AEO_GITHUB_TOKEN` and restart API/worker.
- `github_authentication_failed`: token expired, revoked or malformed.
- `github_permission_denied`: verify repository selection and read permissions, especially Actions for workflow runs.
- `github_resource_not_found`: verify repository spelling and that the token can access the private repository.
- `github_rate_limited`: wait for the GitHub rate-limit reset; the durable worker retries.
- `artifact_persistence_failed`: check PostgreSQL and the S3-compatible object store health.

Never solve an access problem by granting write permissions. If a permission is missing, add only the corresponding read-only permission.
