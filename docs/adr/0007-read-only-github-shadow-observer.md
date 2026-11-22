# ADR 0007: Use a read-only GitHub observer for the first Shadow Brain slice

- Status: Accepted
- Date: 2026-11-22

## Context

V0 starts with repository and CI observation, not code execution. The first sources are `lethinh26/Clucky` and `lethinh26/Llms-System` (New-API). The first repository is public; the second is private. AEO must not inherit broad developer credentials or gain repository write authority.

## Decision

- Use the GitHub REST API at the fixed `https://api.github.com` origin through a connector that exposes GET only.
- Configure a fine-grained token restricted to the two selected repositories, with Metadata, Contents, Issues, Pull requests and Actions set to Read-only. Never persist or log the token; provide it through `AEO_GITHUB_TOKEN` at runtime. The public Clucky repository may be observed anonymously; the private New-API repository is not scheduled until the token is configured.
- Observe repository metadata, recent commits, pull requests, issues and GitHub Actions run metadata. Do not fetch source files, diffs, workflow logs, artifacts or secrets in this milestone.
- Normalize allowlisted fields, redact token-like values and email addresses, and store sanitized payloads as content-addressed S3-compatible artifacts. PostgreSQL stores observation metadata, source cursors, digests and audit records.
- Use at-least-once polling with deterministic observation IDs and a unique `(tenant_id, source_key, source_event_id)` constraint. The initial snapshot is bounded to the latest 100 records per collection; later polls overlap the previous sync window to reconcile updates.
- Poll active sources every 15 minutes by default. Repository connections are read-only and branch/commit/PR write capabilities do not exist in this connector.

## Consequences

- Public and private repositories use the same ingestion path; the private repository remains unsynced until the dedicated read-only token is configured.
- GitHub rate limits and missing repository permissions are surfaced as source sync error codes and retried through the durable worker.
- Workflow run metadata is evidence of CI status, not proof of root cause. CI logs and test reports require a separate redaction and retention design before ingestion.
- The local API is intended for the loopback-bound development stack. Authentication and multi-user source authorization must be added before exposing it beyond the local trusted environment.
