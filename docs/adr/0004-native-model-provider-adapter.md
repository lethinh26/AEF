# ADR 0004: Use a native OpenAI-compatible provider adapter

- Status: Accepted
- Date: 2026-11-22

## Context

AEO's provider boundary is configured by `base_url`, `api_key` and `model`. Provider compatibility varies, especially for tool calling, streaming and structured outputs.

## Decision

Implement provider transport inside AEO behind a typed adapter. Probe required capabilities before enabling an execution workflow. Never delegate runtime control to Codex CLI or parse free-form model text as executable commands.

## Consequences

- Provider credentials and requests remain under AEO policy and audit.
- Provider-specific differences are handled behind a replaceable adapter.
- Tool execution remains a separate policy-enforced boundary.
