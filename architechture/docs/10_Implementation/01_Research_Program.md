# 28 — Chương trình nghiên cứu AEO: chứng minh đột phá trước khi xây platform

## 1. Câu hỏi nghiên cứu lớn

- **RQ1 Awareness:** AEO có phát hiện được opportunities quan trọng mà không cần ticket, với tỷ lệ nhiễu chấp nhận được không?
- **RQ2 Decision:** Khi có nhiều opportunities, decision system chọn việc tốt hơn baseline triage rule/lead engineer không?
- **RQ3 Autonomy:** AEO có xử lý low-risk work đáng tin, có evidence, trong ngân sách và quyền hạn?
- **RQ4 Evolution:** Capability học từ repo A có tạo uplift *trên repo B chưa thấy* sau khi kiểm soát model/version/token cost?
- **RQ5 Organization:** Giá trị tạo ra có vượt overhead governance, ingestion, monitoring và human review?

Không có lý do tự tin RQ4 đúng trước thí nghiệm. Nếu RQ1–3 thành công mà RQ4 thất bại, vẫn có thể sản xuất một useful Operations Automation product; chỉ không gọi nó là self-evolving với bằng chứng.

## 2. Benchmark data program

Lấy 2–3 repo được cấp phép: một CRM backend, một e-commerce, một scripts/integration repo. Tập dữ liệu:

- 30–50 historical tasks, cân bằng bugfix/features/integration, có pre-change snapshots.
- 15–25 CI failure/incident cases, cả false positive và root cause known.
- 10–20 transfer cases khác stack nhưng cùng invariants (e.g. validation, retry, timezone).
- 10–15 malicious or degraded cases: prompt injection, stale data, missing ownership, unknown oracle, provider 429.

Số liệu là **[EXAMPLE]** phụ thuộc khả năng thu thập. Chú ý không đưa nhiệm vụ bị test vào bài học của Evolution Lab. Chia by repo/time/root cause để giảm contamination.

## 3. Experiments theo giai đoạn

### E1 — Shadow Awareness

**Baseline:** CI rules + con người chọn vấn đề từ log/ticket. **AEO:** source ingestion + world claims + hypothesis/opportunity engine. **Oracle:** chuyên gia đánh giá blind, có evidence links và check source correctness. **Metrics:** precision@10, missed critical, review minutes, novelty. **Failure gate:** tạo quá nhiều false alerts, claims không có nguồn, cross-project leak.

### E2 — Decision Quality

**Baseline:** FIFO tickets hoặc rule severity. **AEO:** eligibility + portfolio scheduler. **Design:** replay timestamp historical events, ngăn leakage từ tương lai. **Metrics:** utility estimated conservatively, severe missed incidents, policy conformance, human override. **Gate:** không có rủi ro cao bị tự chọn ngoài policy.

### E3 — Bounded Self-Driving

**Baseline:** single OpenAI-compatible coding agent nhận ticket, sandbox + tests. **AEO:** tự tạo mission sau opportunity và xử lý cùng agent. **Oracle:** hidden tests, diff review, security gate. **Metrics:** autonomous verified completion, risk, cost, latency, extraneous changes. **Gate:** không policy violations và performance không kém baseline đáng kể.

### E4 — Capability Transfer

**Baseline:** same agent without capability library. **Treatment:** capability candidate distilled từ repo A. **Held-out:** repo B khác stack/version, no leaked fixtures. **Metrics:** acceptance, cost, time, repair cycles, negative transfer. **Gate:** cần uplift có ý nghĩa và reproducible; nếu không, retire candidate.

### E5 — Closed-loop Outcome

**Baseline:** human-triggered maintenance, cùng monitoring. **Treatment:** observer chooses and executes branch-only missions, human deploy. **Metrics:** outcome reliability, rollback, incident rates, attention cost. **Caveat:** số incident nhỏ; dùng canary/synthetic signals, không kết luận causality bừa.

## 4. Evaluation protocol

1. Freeze repository snapshots, datasets, hidden tests, acceptance definitions.
2. Pin model ID, provider profile, tool versions, container images, budgets.
3. Randomize experiment order; isolate workspaces and memory state.
4. Run repeated trials cho stochastic outputs; ghi tất cả failures.
5. Blind human evaluation cho opportunitites/reviews.
6. Report effect size + uncertainty, not cherry-picked demos.
7. Separate technical success from post-deployment outcome.
8. Publish internal failure analysis trước quyết định mở rộng.

## 5. Pre-registered kill criteria [EXAMPLE]

- Một privilege escalation thành công trong test set → stop write-side release.
- Một cross-tenant data disclosure → stop promotion/ingestion across boundaries.
- Opportunity precision thấp hơn rule baseline trên held-out → không mở autonomous triage.
- Capability transfer không có uplift sau đủ fixtures → không đầu tư Foundry lớn.
- Cost+human attention cao hơn baseline mà quality tương đương → xem xét đơn giản hóa.

## 6. Kết quả nghiên cứu cần bàn giao

`dataset manifest`, `benchmark runner`, `baseline metrics`, `experiment traces`, `negative cases`, `policy test results`, `opportunity review labels`, `artifact packages`, `decision memo`, `go/no-go recommendation`. Có thể viết bài nghiên cứu nội bộ mỗi tháng; mục tiêu là bằng chứng, không phải demo đẹp.
