# 11 — Portfolio Scheduler: chọn nhiều mission trong giới hạn nguồn lực

## 1. Scheduler là hệ thống quản trị tài nguyên, không chỉ hàng đợi

Có thể có 100 opportunities hợp lệ nhưng chỉ 3 sandbox slots, $100 ngân sách, 20 phút review và một repo lock. Scheduler phải trả lời: việc nào chạy ngay, việc nào đợi, việc nào gom chung, việc nào nên hủy.

## 2. Resource graph

Tài nguyên bao gồm `LLM provider quotas`, `sandbox CPU/RAM`, `repository write locks`, `CI concurrency`, `human approval windows`, `production change windows`, `data access permissions`, `service error budgets`.

**Mission resource request:** `max_parallel_agents`, `context_tokens_estimate`, `sandbox_spec`, `repo_access`, `expected_ci_minutes`, `human_review_band`, `deadline`, `interruptibility`, `retry_limit`.

## 3. Scheduling algorithm V0

```text
Every schedule tick or relevant event:
  candidates = eligible, non-expired opportunities
  reject unauthorized or missing ownership
  group duplicates and dependent missions
  compute conservative benefit/cost/risk bands
  reserve emergency capacity (e.g. 20%, configurable)
  sort by: critical incident tier, deadline, expected value/risk/cost
  for candidate in order:
      if dependencies unmet -> WAIT
      if repo/environment lock conflict -> WAIT
      if monthly/mission budget insufficient -> DEFER
      if confidence below risk threshold -> INVESTIGATE
      if resources available -> allocate lease, issue mission warrant
  record chosen AND rejected candidates with rationale
```

Heuristic dễ audit hơn tối ưu toán học đầy đủ khi data yếu. Sau khi có dataset, cân nhắc constraint programming/linear optimization. **Không để LLM tự lập lịch cuối cùng**.

## 4. Locking và race conditions

- Một repo có thể cho nhiều read-only missions, nhưng write missions cùng vùng code hoặc migration phải khóa theo resource key.
- Lock có lease/expiry; heartbeat giữ lease; worker chết phải được reconciliation trước khi giải phóng.
- `merge queue` tránh branches vượt nhau gây CI pass giả.
- Cần `base_commit_sha` để phát hiện branch cũ trước PR/merge.
- Khi nhiều missions thay cùng tập files, ưu tiên serialize hoặc coordinate integration, không để agents tranh chấp file trên cùng workspace.

## 5. Fairness và starvation

Mỗi goal/tenant có minimum service band, aging priority, max share. Emergency có thể preempt các job chưa có irreversible side effects. Những job dài ít quan trọng bị bỏ đói thì scheduler ghi `starvation age` và đề xuất người điều chỉnh quota.

## 6. Backpressure & budgets

- Khi provider rate-limits, giảm concurrency, không retry đồng loạt.
- Khi CI queue kéo dài, giữ mission ở pending phase; không lặp lại plan.
- Khi human queue quá tải, chuyển mission high-risk sang `WAITING_APPROVAL` và không phát thêm yêu cầu phê duyệt trùng.
- Khi token/cost ước tính không đáng tin, dừng bằng hard time/step/request cap.
- Khi tài nguyên hết, scheduler giải thích số candidate bị trì hoãn và cost of delay sơ bộ.

## 7. Mission preemption

Chỉ preempt tại **safe checkpoints**. Nếu agent đang thực hiện migration staging, phải chờ bước được ghi nhận/đánh dấu compensating action, không kill mù. Trước preempt, snapshot artifacts/state, release tool tokens, preserve intent và evidence.

## 8. Planner vs Scheduler boundaries

Planner thiết kế DAG và capability requirements. Scheduler cấp tài nguyên và order thực hiện. Planner không được giả rằng có 10 workers; scheduler không tự viết lại nghiệm thu. Replan lớn phải tạo phiên bản mới để kiểm chứng lại budget và permissions.

## 9. Metrics

Queue age p50/p95, mission wait vs execute time, resource utilization, budget adherence, collisions/merge conflicts, human queue length, fairness across goals, delayed critical mission count, cost of scheduling churn.

## 10. Simulator trước khi triển khai

Tạo portfolio replay từ lịch sử CI/ticket: giả lập rate-limit, sandbox failure, review bottleneck và 3 missions chạm cùng repo. Kiểm tra không deadlock, không vượt ngân sách và không cấp quyền ngoài policy. Các điểm ưu tiên phải có giải thích từ thông số đầu vào, không chỉ số random của LLM.
