# ADR 0008: Seed the first Opportunity Inbox with deterministic CI signals

- Status: Accepted
- Date: 2026-11-22

## Context

The first GitHub observer slice now stores real workflow-run metadata and evidence. Before adding an LLM-based discovery loop, AEO needs a reproducible baseline for clustering repeated engineering signals and presenting them for human triage.

## Decision

- Generate a `recurring_ci_failure` finding when one repository has at least three failed runs for the same workflow within a rolling seven-day window.
- Group by repository and workflow, not branch, while retaining the set of affected branches and every supporting observation.
- Create one deterministic opportunity per repository/workflow fingerprint. Re-running analysis updates the finding and opportunity description without creating duplicate evidence or resetting a human triage status.
- Expire a still-proposed finding/opportunity when its workflow no longer meets the threshold in the rolling seven-day window. Keep all historical evidence; reopen an expired candidate if the signal returns, but never reset `accepted`, `deferred` or `rejected` human triage.
- Serialize source job scheduling with a source-row lock and skip enqueue when an active (`queued`, `running` or `retrying`) job of the same type already exists for that source.
- Use severity `high` at ten or more failures, otherwise `medium`. The current heuristic score is `min(100, 40 + 5 × failure_count)`; confidence `0.65` is a rule confidence placeholder, **not a calibrated probability**.
- Classify the suggested next step as `R0`: read-only investigation. The opportunity must explicitly state that repeated failures do not establish root cause and list competing hypotheses.
- Human triage supports `accepted`, `deferred` and `rejected`, with an audit record. Acceptance does not authorize code changes, branch creation or mission execution.

## Consequences

- This is a deterministic baseline, not AI diagnosis or proof of root cause.
- Workflow logs, test reports and source diffs remain out of scope until a separate redaction, retention and access-control design is approved.
- The same rule can be compared against human triage before adding model-driven opportunity discovery.
