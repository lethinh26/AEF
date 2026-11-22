# ADR 0002: PostgreSQL is canonical state

- Status: Accepted
- Date: 2026-11-22

## Context

AEO needs durable goals, observations, findings, opportunities, decisions, audit records and job state. Early workloads do not justify operating a separate event broker or graph database.

## Decision

Use PostgreSQL for canonical structured state, transactional outbox records and durable background jobs. Store large artifacts in S3-compatible object storage and keep their metadata, digest and classification in PostgreSQL. Use append-only audit/outbox records without adopting full event sourcing.

## Consequences

- State changes and emitted events can commit atomically.
- Consumers must be idempotent and use inbox deduplication.
- Add a broker or specialized search/graph store only when measured workload requires it.
