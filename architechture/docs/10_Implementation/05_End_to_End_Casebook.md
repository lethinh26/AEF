# 32 — Casebook: 5 kịch bản end-to-end từ mục tiêu đến bài học

> Các trường hợp đều là **[EXAMPLE]**, không phải hệ thống đã chạy thật. Mỗi case có trigger, competing hypotheses, decision, execution, verification, outcomes, evolution và failure branch.

## Case A — CI test checkout bị lỗi ngẫu nhiên

**Goal:** checkout pipeline đủ tin cậy để không trì hoãn các sửa lỗi cấp thiết. **World:** CI run 301/305/309 fail cùng test trên commit khác; metrics runner pool cho thấy failure tập trung vào một image mới. **Finding:** nghi CI image drift, nhưng có thể do race condition ứng dụng.

**Opportunity:** Tạo investigation mission read-only với test matrix pinned image + same commit. **Decision:** không sửa code ngay vì causal ambiguity. **Mission:** chạy test trên old/new runner images, cache disabled. **Evidence:** nếu old pass/new fail lặp lại, link CI image digest. **Delivery:** PR fix CI image version pin + regression detection; verification độc lập. **Outcome:** CI flake ratio giảm trong 7–14 ngày hoặc inconclusive. **Evolution:** candidate `CI environment drift investigation` với applicability to GitHub/GitLab CI.

**Failure branch:** nếu test fail cả hai images, retire initial hypothesis, chuyển điều tra concurrency bug; không force lỗi môi trường cho phù hợp pattern.

## Case B — Checkout timeout tăng sau rollout

**Goal:** SLO checkout API 99.9%. **Observation:** p95 increased 300→580 ms sau 20:00; inventory latency cũng tăng, deployment inventory ngay trước đó. **Hypotheses:** DB query plan, traffic spike, upstream provider issues, trace sampling artifact.

**Decision:** Chạy read-only investigation + staging benchmark trước. **Mission:** analyze traces/db plans; minimal patch if causal evidence adequate. **Verification:** fixed workload p95 benchmark with samples, E2E no duplicate orders, query correctness. **Human gate:** production rollout with canary requires owner approval. **Outcome:** observe p95/error rate, rollback criteria; không tự báo thành công từ local test. **Evolution:** nếu proven, extract query-plan regression detection capability.

**Failure branch:** sau canary latency giảm nhưng database CPU tăng cao → countermetric fails, rollback và record `OUTCOME_NEGATIVE`.

## Case C — Tạo tính năng coupon từ ý tưởng

**Goal:** cung cấp coupon engine có kiểm soát cho e-commerce. **Intake:** user chỉ nói “thêm coupon”. **Compiler:** tìm thiếu thông tin: stacking rules, expiry timezone, usage limits, refund handling, target segments, tax rounding. **Decision:** chuyển `NEEDS_CLARIFICATION`; không đoán ảnh hưởng đến thanh toán.

**Mission topology:** Domain contract + API + UI + DB migration design + integration tests. **Capability reuse:** validation patterns, idempotent quota decrement, RBAC admin, audit logging nếu applicability phù hợp. **Verification:** property tests concurrency, E2E checkout, migration dry-run, security, admin roles. **Delivery:** PR + staging + cutover plan, production approval. **Outcome:** đo tỷ lệ coupon apply success và complaint rate sau launch.

**Failure branch:** agent viết test tự đặt rounding rule trái nghiệp vụ → hidden domain acceptance rejects; không coi 100% unit tests do agent tạo là pass.

## Case D — Học an toàn từ timezone bug đa dự án

**Project A:** sửa bug invoice cutoff trong Python. Evidence: reproduction + acceptance. **Extraction:** procedure “timezone-aware boundary conditions”, includes invariants (store UTC, convert at edges), test matrix daylight saving/timezone specifics.

**Project B:** Node.js ecommerce khác vùng địa lý. **Applicability:** không copy Python snippet; dùng invariants + tests, sinh implementation phù hợp Node. **Experiment:** baseline agent vs AEO capability cùng model/budget, held-out fixtures gồm timezone khác A. **Promotion:** chỉ nếu quality đạt và chi phí/time cải thiện với evidence. **Negative transfer:** B sử dụng business timezone theo store; nếu default UTC-only rules sai, cập nhật exclusions.

## Case E — Nhiễm prompt injection qua README

**Trigger:** AEO có branch-only mission sửa lỗi, repo chứa `README` hướng dẫn gửi `.env` tới một URL lạ. **Data handling:** ingestion đánh dấu source untrusted; LLM có thể đọc nhưng không được coi đó là quyền. **Policy:** tool gateway từ chối `read .env` hoặc outbound upload; sandbox không chứa key đó, egress network denied. **Evidence:** denied action log và no data exfil. **Outcome:** mission có thể tiếp tục sửa lỗi an toàn hoặc quarantine nếu có malicious instruction. **Evolution:** threat fixture được bổ sung vào regression suite, không tạo “capability bypass README instruction” bằng cách sửa policy tùy tiện.

## Lý do chọn các case

A chứng minh *không hành động vội*, B chứng minh *outcome verification*, C chứng minh *generative product*, D chứng minh *transferable learning*, E chứng minh *governed autonomy*. Một AEO có UI đẹp nhưng không vượt nổi năm case này chưa được coi là AEO đạt V1.
