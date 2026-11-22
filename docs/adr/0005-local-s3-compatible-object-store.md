# ADR 0005: Use a local S3-compatible object store

- Status: Accepted for local development
- Date: 2026-11-22

## Context

AEO stores large redacted observations, diffs, reports and evidence artifacts outside PostgreSQL. The application needs an S3-compatible API so local development can match a future managed object store.

The former MinIO Community Edition container is no longer a reliable default for fresh environments. PGSTY Silo is a separately maintained S3-compatible fork with a pinned container release and a compatible API.

## Decision

Use PGSTY Silo `RELEASE.2026-11-12T00-00-00Z` for local development. Keep the S3 endpoint, access key, secret and bucket configurable through environment settings. Store artifact metadata and digests in PostgreSQL.

## Consequences

- Local storage can be replaced with managed S3 without changing the artifact interface.
- Silo is AGPLv3-licensed and remains a separately operated development dependency. Review licensing and operational requirements before embedding, modifying or redistributing it as part of a product distribution.
- Production object storage selection remains an explicit deployment decision; local Silo is not a production architecture recommendation by itself.
