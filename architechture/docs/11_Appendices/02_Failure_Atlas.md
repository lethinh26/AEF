# 34 — Failure Atlas: lỗi nhỏ, lỗi liên kết, lỗi tổ chức

## 1. Epistemic errors — nhận thức sai

1. **Hallucinated dependency:** LLM suy ra service gọi hệ khác vì tên giống. Phòng ngừa: provenance và impact evidence.
2. **Stale repo context:** branch đã đổi sau khi phân tích. Phòng ngừa: base commit pin và invalidation.
3. **Correlation-to-causation:** cứ deployment gần lỗi là root cause. Phòng ngừa: alternative hypothesis, canary, trace evidence.
4. **Missing negative evidence:** không thấy test fail nên cho là pass. Phòng ngừa: test count, oracle.
5. **False certainty:** output “98% sure” không calibration. Phòng ngừa: empirical confidence bands và risk gates.

## 2. Decision failures — chọn sai việc

6. **Alert spam:** nhiều findings cho cùng root cause. Dedup, cooldown, event clustering.
7. **Busywork optimization:** chọn task dễ để tăng completion. Goal-linked outcomes và opportunity audit.
8. **Goal conflict:** giảm latency bằng bỏ fraud check. Hard constraints và owner arbitration.
9. **Hidden opportunity cost:** tốn toàn bộ sandbox vào refactor nhỏ khi có incident. Portfolio emergency reserve.
10. **Escalation flood:** quá nhiều câu hỏi vụn vặt. Aggregate contexts, review budget và severity routing.

## 3. Execution failures — hành động sai

11. **Tool schema drift:** provider thay response tool format. Capability probe/contract tests.
12. **Unbounded loop:** model lặp sửa cùng test. Step/time/retry caps và no-progress detector.
13. **Host escape:** tool chạy command trên host. Sandbox isolation, policy tool gateway.
14. **Duplicate side effect:** 2 PR do retry timeout. External id reconciliation.
15. **Merge conflict:** 2 missions sửa cùng file. Scheduler repo/file locks và integration queue.
16. **Partial cancellation:** worker bị kill khi chưa lưu artifact. Checkpoint and compensation.

## 4. Verification failures

17. **Test deletion to pass:** acceptance oracle độc lập + baseline diff.
18. **Passing empty suite:** check test count và required test IDs.
19. **Unrepresentative benchmark:** tạo improvement giả. Representative load và multiple samples.
20. **Self-approved production:** approval binding qua service authenticated.
21. **Outcome confounding:** traffic thấp làm latency giảm. Canary/control hoặc inconclusive.

## 5. Organizational learning failures

22. **Prompt-only reuse:** tạo skill không có applicability. Capability contract + eval.
23. **Overfit to training tasks:** reuse chỉ tốt trên cùng repo. Held-out by project/root cause.
24. **Negative transfer:** method từ CRM gây lỗi ecommerce. Exclusions và trust downgrade.
25. **Knowledge contamination:** false postmortem được học thành truth. Claim provenance/owner review.
26. **Capability explosion:** registry quá nhiều, stale. Dedup/versioning/retirement.
27. **Survivorship bias:** chỉ lưu successful missions. Ledger đầy đủ cả rejected/failed.

## 6. Security and business failures

28. **Cross-tenant leakage:** shared memory cho khách hàng khác. ACL-first per source/project.
29. **Secret egress through model:** tokens đưa vào prompt/log. Secret broker/redaction/egress.
30. **Self-escalation:** model giả mạo policy/approval. Authorization outside model.
31. **Cost explosion:** retry/provider bill vượt dự báo. Budget reservation and hard caps.
32. **Metrics gaming:** agents sửa instrumentation để đạt KPI. Independent monitoring owner và protected paths.
33. **Regulatory/IP issue:** copy proprietary code sang reusable module. rights ledger, legal review.
34. **Trust collapse:** liên tục PR sai khiến dev bỏ dashboard. Calibration, human feedback, graduated autonomy.

## 7. Cách sử dụng Failure Atlas

Mỗi failure phải có ít nhất một regression fixture/chaos test và owner. Khi sự cố xảy ra, liên kết incident→failure category→mitigation→test→capability/version nếu có. Không thêm checklist chỉ để cho đủ số: kiểm tra định kỳ rằng guardrail thực sự được enforce.
