# 26 — Events, APIs, idempotency và workflow protocol

## 1. Event schema bắt buộc

```json
{
  "event_id":"uuid",
  "event_type":"mission.task.completed",
  "event_version":1,
  "aggregate_id":"mission-id",
  "aggregate_version":12,
  "tenant_id":"tenant-id",
  "occurred_at":"2026-11-21T08:00:00Z",
  "observed_at":"2026-11-21T08:00:02Z",
  "actor":"service:mission-worker",
  "correlation_id":"mission-id",
  "causation_id":"previous-event-id",
  "policy_decision_id":"policy-event-id",
  "payload_ref":"artifact://events/uuid.json",
  "payload_digest":"sha256:..."
}
```

Không ghi secrets/PII vào event. Event payload phải được kiểm tra schema và policy access. Ghi event và state mutation trong cùng DB transaction (transactional outbox).

## 2. Event taxonomy

- Goal: `goal.created`, `goal.activated`, `goal.degraded`, `goal.suspended`.
- Ingestion: `observation.received`, `observation.rejected`, `world.claim.updated`, `world.claim.disputed`.
- Intelligence: `finding.proposed`, `finding.verified`, `opportunity.proposed`, `opportunity.deferred`.
- Decisions: `decision.committed`, `decision.reconsidered`, `allocation.reserved`.
- Missions: `mission.created`, `mission.started`, `mission.blocked`, `mission.completed`, `mission.cancelled`.
- Execution: `tool.proposed`, `tool.permitted`, `tool.denied`, `tool.executed`, `sandbox.quarantined`.
- Quality: `verification.completed`, `outcome.measured`, `outcome.inconclusive`.
- Evolution: `capability.extracted`, `capability.evaluated`, `capability.promoted`, `capability.quarantined`.

## 3. API boundaries

```text
POST /v1/goals                       Create goal draft
POST /v1/goals/{id}/activate        Activate authorized goal
GET  /v1/world/assets              Asset scope view
GET  /v1/findings?goal_id=...      Findings with evidence
GET  /v1/opportunities             Portfolio review
POST /v1/opportunities/{id}/triage Triage / override
POST /v1/missions                   Submit manual mission
GET  /v1/missions/{id}             State, plan, artifacts
POST /v1/missions/{id}/cancel      Request safe cancellation
GET  /v1/missions/{id}/ledger      Events and explanations
POST /v1/approvals/{id}/decide     Approve/reject exact action
GET  /v1/capabilities              Registry and trust tiers
POST /v1/evals                     Start lab experiment
POST /v1/providers/test            Real API capability probe
GET  /v1/audit                     Scoped audit reports
```

`POST` gây side effects phải nhận `Idempotency-Key`; validate authentication, tenant, ETag/If-Match cho versioned updates. Lỗi JSON có `code`, `message`, `retryable`, `correlation_id`, `policy_reason` (nếu được công bố).

## 4. Approval API caveat

`POST /approvals/{id}/decide` dùng session người được xác thực + MFA cho risk class cao. Không nhận `approved_by` tự khai do client gửi. Approval dành cho digest chính xác và hết hạn khi plan/diff thay.

## 5. Webhook ingestion

Xác minh signature/origin, giới hạn body size, quota per source, schema validation, queue async, idempotency source event ID. Respond 2xx sau khi persist event, không sau khi chạy LLM. Có dead-letter queue và dashboard replay with authorization.

## 6. External API side effects

Mỗi side effect có `ActionIntent` record trước, `external_correlation_key`, `ActionOutcome` sau. On timeout query external system để reconciliation trước retry. Nếu không có idempotency support, dùng lookup by unique branch/name/tag và khóa tài nguyên; nếu không thể reconcile thì escalate, không risk duplicate.

## 7. State machine contract tests

Test transition invalid, duplicate event, out-of-order event, 2 concurrent approvers, owner revocation mid-run, artifact hash mismatch, replay after worker kill. Không chấp nhận `RUNNING → COMPLETED` mà bỏ verification unless mission type có oracle tương ứng đã đạt.

## 8. API privacy

Hạn chế xem logs/artifacts theo ACL; sanitize terminal ANSI/html, giới hạn download link TTL; không trả LLM provider secrets ở API status; log injection và prompt injection cũng không được biến thành nội dung UI có thể thực thi.
