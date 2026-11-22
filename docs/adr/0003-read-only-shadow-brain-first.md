# ADR 0003: Start with a read-only Shadow Brain

- Status: Accepted
- Date: 2026-11-22

## Context

The MVP specification puts V0 Shadow Brain before bounded mission execution. It observes a small number of repositories and CI sources, builds evidence-backed findings and opportunities, and lets a human triage them.

## Decision

The initial product milestone is read-only ingestion and analysis. Repository write tools, autonomous code execution, PR creation and production deployment are excluded from V0. Credentials for source connectors must be read-only and narrowly scoped.

## Consequences

- Discovery quality and evidence provenance can be evaluated before granting write authority.
- V1 execution requires a separate policy, sandbox, verifier and acceptance gate.
