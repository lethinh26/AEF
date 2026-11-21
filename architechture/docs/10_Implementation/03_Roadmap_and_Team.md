# 30 — Lộ trình có gate, phân công 5–15 người và ngân sách

## 1. Không cố đoán deadline chính xác

Những giai đoạn sau là **khung ưu tiên** cho một team có sẵn dev mạnh và hạ tầng CI/Git; thời lượng thực tế phụ thuộc repo complexity, testability, API access và số lỗi security/agent. Tránh cam kết 12 tuần có Autonomous Organization hoàn chỉnh.

## 2. Phase 0 — Discovery & contracts (gợi ý 2–3 tuần)

**Deliverables:** threat model v0, Goal schema, 2–3 project scopes, 30–50 benchmarks, provider probe, success metrics, ownership. **Go criteria:** repo rights rõ, baseline measurable, seeded known incidents, CI signal có thể ingest. **No-go:** không có quyền đọc logs/code, không có acceptance oracles.

## 3. Phase 1 — Shadow Awareness (gợi ý 3–5 tuần)

**Deliverables:** connectors, World Model v0, evidence links, signal clustering, opportunity inbox, blind review pipeline. **Go criteria:** evidence-backed opportunities đủ chính xác so với simple rules/human triage; không cross-project leaks; ingestion recoverable. **Kill criteria:** noisy proposals, source data unreliable, unable to reproduce world state.

## 4. Phase 2 — Bounded Autonomy (gợi ý 4–8 tuần)

**Deliverables:** mission contract/state, provider tool-loop, sandbox, branch-only, CI verification, cost quotas, policy gateway, approval, ledger, kill switch. **Go criteria:** known bugfix fixture end-to-end với real endpoint; hidden tests; chaos tests; no policy violations. **No-go:** agent không hỗ trợ tool-calling hoặc sandbox không cô lập.

## 5. Phase 3 — Capability Transfer Lab (gợi ý 4–8 tuần)

**Deliverables:** capability manifests, extraction/promotion states, held-out benchmark, A/B baseline, negative transfer report. **Go criteria:** uplift lặp lại trên project khác; không giảm quality. **No-go:** chỉ cải thiện trên chính repo extraction hoặc model thay đổi.

## 6. Phase 4 — Outcome Autopilot (sau khi đủ chứng cứ)

Mở rộng telemetry, canary monitoring, production outcome attribution, risk-aware operations; nâng quyền chỉ theo loại nhiệm vụ đã kiểm chứng và owner phê duyệt. Không thay quyền production bằng mục tiêu tăng tốc.

## 7. Phân công đội nòng cốt

| Vai trò | Người mẫu | Trọng trách | Có thể kiêm? |
|---|---|---|---|
| Chief Architect/Tech lead | 1 | invariants, ADR, modular boundaries | goal owner liaison |
| Platform/backend | 2 | state, connectors, API, data | worker infrastructure |
| Agent/tool engineer | 1–2 | provider, tools, sandbox integration | evaluation |
| Quality/evaluation engineer | 1 | benchmarks, hidden oracles, CI, evidence | SRE hỗ trợ |
| SRE/Security | 1 | policies, isolation, incident, observability | part-time trên V0 nếu sẵn năng lực |
| Product/Engineering owner | 1 | goals, triage, acceptance, UX | part-time từ leadership |

Một nhóm khoảng 5–7 core, bổ sung QA/domain experts theo job. Tuyệt đối cần người chịu trách nhiệm independent review với hoạt động rủi ro.

## 8. Priority order nếu thiếu nhân lực

1. Lấy dữ liệu thật và baseline.
2. World claims/evidence + Opportunity review.
3. Policy + sandbox trước khi agent được write.
4. Mission vertical slice + independent verification.
5. Capability extraction/eval.
6. Scale/performance/market features sau.

**Không** ưu tiên dashboard hoành tráng, agent roleplay hoặc microservices trước core evidence.

## 9. Operational costs cần dự toán

Direct: model requests, sandbox CPU/storage, CI, object store, logging, hosted Git/telemetry. Indirect: maintenance adapters, test fixture updates, reviewer attention, security/incident response, provider incompatibility, compliance and data processing. Ước lượng theo workload thực, không lấy token price làm tổng giá thành.

## 10. Gate review template

Tại mỗi milestone báo cáo: hypothesis, evidence dataset, baseline, intervention, quality delta, safety tests, cost delta, user impact, failure analysis, residual risks, decision `GO/ITERATE/STOP`. Không chuyển phase chỉ vì “đã code xong”.
