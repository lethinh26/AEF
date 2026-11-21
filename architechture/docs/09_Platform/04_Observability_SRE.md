# 27 — Observability, SRE, SLO và vận hành chính AEO

## 1. AEO tự nó là hệ thống cần được quan sát

Không chỉ monitor các repo AEO quản lý. Chính AEO phải có SLI/SLO: mission state consistency, event ingestion lag, policy availability, task success verified, tool error rate, sandbox cleanup, provider latency, artifact integrity, security decisions.

## 2. Bốn lớp metrics

**Business/Outcome:** customer/user outcome, SLO target achievement. **Engineering Delivery:** change lead time, change failure rate, failed deployment recovery time, throughput; dựa logic DORA [R10]. **Agent Quality:** verified completions, false fixes, repair cycles, hallucinated tool calls. **Governance:** budget adherence, forbidden-action attempts, approval latency, escalation load.

Không gộp “thành công” của một level với level khác. Mission pass không nhất thiết có customer outcome.

## 3. Tracing

Một trace root cho mỗi Opportunity-to-Mission process, propagated qua ingestion, decision, mission, provider call, sandbox, CI, verification, outcome. Span tags nên có `tenant_id` an toàn, `mission_id`, `model_profile`, `tool_name`, `decision_id`, `policy_result` nhưng không chứa prompts/secrets mặc định. OpenTelemetry hỗ trợ traces, metrics và logs [R2].

## 4. SLO ví dụ [EXAMPLE]

- 99.9% of **policy decisions** return within defined latency or fail-closed.
- 99% **goal observations** fresh within configured source lag.
- 99.5% **tool events** reconciled to known terminal outcome within one hour.
- 100% production write actions have valid approval record and exact artifact digest (hard invariant).
- 99% sandbox resources cleaned up within defined TTL.

Đây là yêu cầu mẫu cần chỉnh theo deployment; không có số liệu baseline thật.

## 5. Error budgets

Nếu AEO chính nó vượt error budget ở security/permission plane, tự động freeze write-side, vẫn cho phép read-only monitoring. Nếu một service của khách hàng hết error budget, AEO không tự xác định bỏ mọi release; áp goal owner policy, kiểm tra tác động/tính khẩn cấp. Tư duy SLO/error budget xem [Google SRE workbook](https://sre.google/workbook/error-budget-policy/).

## 6. Runbooks

- Model provider outage: freeze agent execution, giữ ingest, queue/backpressure, thông báo owner.
- Policy service outage: deny side-effect, alert high priority, manual investigation.
- Event outbox stuck: kiểm tra lag, replay idempotent, tránh double PR.
- Evidence store corrupt: mark impacted missions unverified, block promotion, restore/rehash.
- Sandbox leak: terminate/revoke and forensic snapshot theo policy.
- Cost runaway: global and per-goal kill switch, record budget overrun, audit model/tool.
- Capability poisoning: quarantine version, identify affected missions, reevaluate downstream outputs.

## 7. Dashboards

**Operations:** active goals, finding backlog, mission states, CI errors, queue lag. **Decision:** selected/deferred opportunities, rationale, goal conflicts. **Quality:** pass/fail by risk and task type, false positives, post-deploy outcomes. **Economics:** total cost, human attention, ROI estimate, budget forecast. **Security:** denied tools, approvals, new egress, secret detection, incidents.

## 8. Human factors

Một AEO “tự chủ” thất bại nếu ping 50 lần/ngày. Nhóm theo incident/mission, severity triage, quiet hours (trừ critical), actionable summaries, SLA response. Đo alert fatigue bằng suppressions và human triage time. Owner có quyền thay đổi notification policy.

## 9. Capacity planning

Model concurrency, sandbox pools, CI queues, artifact storage, Postgres growth, logs retention; stress test peak webhook burst và 10 parallel missions. Dùng SLO data để quyết định thêm worker chứ không mặc định scale out mọi service.
