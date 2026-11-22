# ADR 0001: Start with a modular monolith

- Status: Accepted
- Date: 2026-11-22

## Context

The AEO reference architecture defines clear domain and trust boundaries but explicitly does not require microservices. The first team and workload are small, and the early product needs rapid changes across goals, ingestion, world state and opportunity discovery.

## Decision

Run one FastAPI application and one background worker process from a shared Python workspace. Keep domain ownership behind typed module interfaces and prohibit cross-module writes to another module's tables. Split a module into a service only when measured scaling, isolation or deployment needs justify the operational cost.

## Consequences

- Local development and transactions remain simple.
- API and worker can scale independently.
- Module boundaries and event contracts are established before service extraction.
- A module extraction requires an explicit API/event contract and data ownership plan.
