# 09B — Phân tích nguyên nhân, tác động và độ bất định trong World Model

## 1. “Biết có liên quan” khác “biết là nguyên nhân”

World Model có thể biết `service A CALLS service B`; telemetry có thể thấy lỗi tăng cùng thời điểm. Không có mệnh đề nào tự chứng minh `B CAUSED A_failure`. Mô hình nhân quả (causal model) là tập giả thuyết cần kiểm tra, không phải graph dependencies đơn thuần. Sai lầm này đặc biệt nguy hiểm khi AEO được phép chủ động sửa code.

## 2. Causal hypothesis schema

```yaml
hypothesis:
  id: hyp_22
  target_effect: 'checkout_timeouts'
  candidate_cause: 'inventory_query_latency'
  evidence:
    - kind: temporal_correspondence
      ref: trace_cluster_01
    - kind: deployment_change
      ref: deploy_37
  counter_evidence:
    - ref: sample_42
      description: 'Một số checkout timeout không qua inventory service'
  confounders:
    - 'peak traffic'
    - 'shared database load'
    - 'trace sampling'
  falsification_plan:
    - 'compare before-after under matched traffic'
    - 'rerun representative query in staging'
  classification: 'PLAUSIBLE_NOT_CONFIRMED'
```

Một claim có confidence cao về sự tồn tại không đồng nghĩa confidence cao về nguyên nhân. Gắn riêng `observational certainty`, `causal confidence` và `intervention confidence`.

## 3. Impact analysis hai chiều

**Forward:** Nếu sửa `DB schema X`, các consumers, reports và APIs nào có thể bị ảnh hưởng? **Backward:** Một lỗi checkout liên quan tới các dependencies nào theo runtime traces + deployments + feature flags?

Bộ phân tích tác động trả:

1. Confirmed impact paths (runtime traces/contracts).
2. Inferred paths (static refs/dependency graph).
3. Missing telemetry / unknown effects.
4. Suggested validation tests and owners.
5. Worst-case blast radius trong scope.

Các đường ảnh hưởng phải giới hạn depth và score theo provenance, tránh graph explosion. Không dùng similarity embedding làm bằng chứng trực tiếp về dependency.

## 4. Intervention readiness checklist

- Có lỗi tái lập? Nếu chưa có, cần thêm observation hoặc canary.
- Có test oracle để xác nhận sửa thành công? Nếu không, đề xuất tạo oracle trước.
- Có alternative explanations quan trọng chưa loại trừ?
- Có nắm được config của runtime đang lỗi (commit, env, feature flags, data shape)?
- Hành động có reversible hoặc canary không?
- Có nguồn đo outcome đủ tin cậy trong cửa sổ hợp lý?

Nếu không đủ, Mission nên `INVESTIGATE` thay vì `REPAIR`.

## 5. Change impact replay

Sau một change, cập nhật world snapshot: invalidated code symbol edges, re-link deployment revision, refresh service contract tests. Nếu PR sửa API nhưng compatibility claims cũ chưa cập nhật, system phải đánh dấu outdated trước khi tạo mission mới liên quan.

## 6. Hành vi khi source mâu thuẫn

Một AST parser cho thấy API gọi service cũ; traces cho thấy không hề có call. Có thể vì code path chưa chạy, feature flag tắt hoặc telemetry sampling. Phân loại:

- Static dependency: MAY_CALL.
- Runtime dependency: OBSERVED_CALL.
- Confirmed absence: hiếm, cần coverage chứng minh.

Đừng suy ra từ `no traces` sang `no dependency`. “Không có bằng chứng” và “bằng chứng không có” là khác nhau.

## 7. Tái kiểm chứng qua thời gian

Mỗi causal finding có expiry theo loại sự kiện. Khi traffic pattern/commit/model thay, confidence về giải pháp cũ giảm; cần revalidate. Khi canary không cải thiện chỉ số, tạo `OutcomeNegative` và ghi bài học chống áp dụng capability tương tự. Không cứ tăng max retry để tìm “fix” khác.

## 8. KPI cho causal analysis

- Root cause hypothesis top-k accuracy so với postmortem xác minh.
- Percentage of proposed fixes with reproduction test.
- Incidence of harmful changes due to wrong causal attribution.
- Ratio of `investigation first` decisions đúng theo blind reviewers.
- Time/cost from finding to verified cause.
- Negative outcome detection time.

Khi không có ground truth, chỉ báo evidence strength và unknown rate; không công bố “AI RCA accuracy 95%” tùy tiện.
