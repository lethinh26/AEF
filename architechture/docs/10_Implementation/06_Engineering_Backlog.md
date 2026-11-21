# 32B — Implementation Backlog: phân rã công việc tới cấp story/kiểm thử

> Đây là backlog tổ chức theo phụ thuộc và testability, **không phải yêu cầu làm tất cả trong V1**. Mã `P0` = bắt buộc trước mọi write action, `P1` = vertical slice, `P2` = nghiên cứu mở rộng. Mỗi story chỉ hoàn thành khi có test và observability tương ứng.

## Workstream G — Goals / Organization

- `G-01 [P0]` Typed Goal contract, validate owner, scope, SLI và budget; test missing owner/metric.
- `G-02 [P0]` Goal state machine activate/degrade/suspend; test invalid transitions.
- `G-03 [P1]` Goal versioning, optimistic concurrency, audit.
- `G-04 [P1]` Goal dashboard with measurement freshness.
- `G-05 [P1]` Approval UI và conflict owner resolution.
- `G-06 [P2]` Goal graph, conflicts/depends_on edges, hierarchy.
- `G-07 [P2]` Goal charter periodic review và stale objectives alerts.

## Workstream I — Ingestion / World

- `I-01 [P0]` Read-only Git connector, minimal-scope credentials, idempotency.
- `I-02 [P0]` CI run ingest with signature checking and replay cursor.
- `I-03 [P0]` Event envelope và raw evidence object storage.
- `I-04 [P0]` Redaction pipeline and secret-scanning in logs.
- `I-05 [P1]` Asset catalog (repo, service, commit, branch, owner).
- `I-06 [P1]` Claim store (source, valid time, verification state).
- `I-07 [P1]` World snapshot query API and ACL-first.
- `I-08 [P1]` Data source lag/duplicate/schema drift dashboards.
- `I-09 [P2]` Static dependency extraction with provenance.
- `I-10 [P2]` OTel runtime topology and time-window reconciliation.
- `I-11 [P2]` Contradictory claim adjudication workflow.
- `I-12 [P2]` Multi-tenant indexing and erasure tests.

## Workstream O — Opportunities

- `O-01 [P0]` Rule-based CI failure clustering.
- `O-02 [P0]` Finding schema with hypotheses/evidence/alternatives.
- `O-03 [P1]` Opportunity object with Goal alignment, cost/risk bands.
- `O-04 [P1]` Dedup/cooldown/hysteresis suppression.
- `O-05 [P1]` Blind reviewer labeling UI and annotation log.
- `O-06 [P1]` Explicit `DO_NOTHING` recommendation and decision trace.
- `O-07 [P2]` Statistical anomalies and missing-telemetry detection.
- `O-08 [P2]` Causal testing suggestion and impact graph retrieval.

## Workstream D — Decision / Portfolio

- `D-01 [P0]` Eligibility check through policy PDP.
- `D-02 [P1]` Decision record with alternatives/uncertainty/versions.
- `D-03 [P1]` Greedy scheduler under quota, concurrency and repo locks.
- `D-04 [P1]` Atomic resource reservations and lease recovery.
- `D-05 [P1]` Escalation routing and human attention queue.
- `D-06 [P2]` Counterfactual replay, calibrated benefit/cost estimation.
- `D-07 [P2]` Portfolio fairness and starvation controls.

## Workstream M — Missions / Runtime

- `M-01 [P0]` Mission warrant and state machine, Pydantic schemas.
- `M-02 [P0]` Provider config/secret refs, connection/tool-call probe.
- `M-03 [P0]` Native LLM tool-loop with bounds and protocol trace.
- `M-04 [P0]` Tool Gateway policy PEP on every call.
- `M-05 [P0]` Sandbox runner isolation, TTL, resource limits.
- `M-06 [P1]` Read/search/apply_patch/git_diff tools with path validation.
- `M-07 [P1]` Approved test command registry and result parser.
- `M-08 [P1]` Patch/branch artifact and PR creation with idempotency.
- `M-09 [P1]` Checkpoint, retry, cancellation, external reconciliation.
- `M-10 [P1]` Repair attempt scheduler (maximum cycles; no-progress detection).
- `M-11 [P2]` Multi-agent topology choice and artifact handshake.
- `M-12 [P2]` Long-lived workflow migration to Temporal if justified.

## Workstream V — Verification / Outcome

- `V-01 [P0]` Independent test runner; required test count.
- `V-02 [P0]` Protected acceptance oracle outside agent workspace.
- `V-03 [P1]` Evidence artifact hashing and verifier identity.
- `V-04 [P1]` Verification trust tiers and mission state gates.
- `V-05 [P1]` Outcome observer as separate process with window/SLO.
- `V-06 [P2]` Canary/control cohorts and post-deploy measurement analysis.
- `V-07 [P2]` SLSA-inspired provenance/attestation chain.

## Workstream E — Evolution

- `E-01 [P1]` Candidate extraction from verified missions with source rights.
- `E-02 [P1]` Manifest/version/applicability for capabilities.
- `E-03 [P1]` Held-out experiment runner and simple-agent baseline.
- `E-04 [P2]` Negative transfer detection, quarantine and retirement.
- `E-05 [P2]` Model/workflow routing experiments under pinned environment.
- `E-06 [P2]` Rights-aware cross-project generalization.

## Workstream S — Security / Operations

- `S-01 [P0]` OIDC/SSO operator auth and per-repo ACL.
- `S-02 [P0]` Provider/Tool token broker, egress restrictions.
- `S-03 [P0]` Global and scoped kill switch, revocation.
- `S-04 [P0]` SSRF/path traversal/prompt injection regression tests.
- `S-05 [P0]` Budget hard limits and atomic reservation.
- `S-06 [P1]` Policy decision audit and approval digest binding.
- `S-07 [P1]` Outbox/inbox dedup + disaster replay tests.
- `S-08 [P1]` Structured traces/metrics/logs and operator dashboard.
- `S-09 [P2]` Security incident freeze/quarantine runbooks.
- `S-10 [P2]` Cross-project data erasure and IP audit.

## Dependency spine

`G-01 → I-01/I-02 → I-03/I-06 → O-01/O-02 → D-01/D-02 → M-01 → M-02/M-03 → M-04/M-05 → V-01/V-02 → M-08 → V-05 → E-01/E-03`.

**Security path chạy song song nhưng phải hoàn tất trước write:** `S-01/S-02/S-03/S-04/S-05`, không postpone dưới danh nghĩa MVP.

## Definition of Done áp cho từng story

- Code + migration + typed contract (nếu áp dụng).
- Unit/integration test có negative path.
- Log/metric hoặc audit event.
- Policy/threat model impacts được xem xét.
- README/runbook/ADR cập nhật.
- Repro command và evidence link từ CI.

## Cách phân sprint

- Sprint 1: source/goal/evidence skeleton và fixtures.
- Sprint 2: world/opportunity/shadow reviewer.
- Sprint 3: policy + sandbox + provider probe.
- Sprint 4: mission loop + verifier + PR delivery.
- Sprint 5: chaos, security, budget, manual operation.
- Sprint 6+: evolution held-out tests, outcome analysis và mở rộng có điều kiện.

Không đồng nhất 1 sprint với 1 tuần; lượng việc thực cần ước lượng qua codebase/experience thực tế.
