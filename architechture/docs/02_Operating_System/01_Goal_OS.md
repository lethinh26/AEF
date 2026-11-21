# 04 — Goal Operating System: định nghĩa trách nhiệm dài hạn

## 1. Goal không phải task hoặc OKR text

Goal phải là thực thể **kiểm soát được bằng máy**, có owner, ranh giới, measurement, time horizon, risk appetite, funding, policy và exit criteria. `Tăng chất lượng sản phẩm` là intent chưa thể thực thi; `giảm lỗi checkout làm mất đơn mà không tăng tỷ lệ đặt hàng trùng` là goal có thể refinement.

### Goal contract tối thiểu

```yaml
api_version: aeo/v1alpha1
kind: EngineeringGoal
metadata:
  id: goal_checkout_reliability
  tenant_id: internal
  owner_user_id: head_of_engineering
  version: 7
spec:
  objective: 'Giảm lỗi checkout do nguyên nhân kỹ thuật'
  asset_scope: [svc-checkout, svc-order, svc-inventory]
  horizon: '2027-03-31'
  measures:
    - id: checkout_availability
      sli: 'successful_checkout_api_calls / eligible_checkout_api_calls'
      target: 0.999
      window: 30d
      source: 'otel://metrics/checkout'
      min_sample_size: 10000
  guardrails:
    - 'duplicate_orders_rate <= baseline + 0.0001'
    - 'security_incidents == 0'
    - 'p95_latency_ms <= 450'
  autonomy_profile: branch_only
  spending:
    usd_per_month: 150 # số giả định
    usd_per_mission: 15
  escalation:
    stale_measurement_hours: 24
    impact_threshold: high
  stop_conditions:
    - 'owner_revokes'
    - 'policy_violation'
    - 'budget_exhausted'
status:
  lifecycle: ACTIVE
  last_evaluated_at: null
```

### Các trường khó nhưng phải có

- **Metric definition:** tử/mẫu, population, tỷ lệ lỗi nào bị loại, sampling, delay, timezone.
- **Leading vs lagging indicators:** test failure là leading; customer-impact có thể lagging.
- **Counter-metrics:** tối ưu latency không được phá an toàn dữ liệu, tối ưu build time không được bỏ test.
- **Confidence & freshness:** cảnh báo khi metric nguồn hỏng, thiếu samples, dashboard lệch thời gian.
- **Goal owner:** người quyết định trade-off khi mục tiêu xung đột.
- **Consent/contract boundary:** mục tiêu chỉ bao phủ assets đã được chủ sở hữu cấp quyền.

## 2. Goal graph và xung đột

Goal không độc lập. `Checkout Reliability` phụ thuộc `Payment Idempotency`, `DB Health`, `Deployment Stability`. Có các cạnh `supports`, `conflicts_with`, `depends_on`, `owned_by`, `measured_by` có provenance. Mỗi cạnh có trạng thái verified/inferred/obsolete và thời điểm xác nhận.

**Xung đột ví dụ:** Goal A tăng tốc checkout, Goal B tối thiểu chi phí cloud, Goal C giữ fraud detection. Nếu AEO đề xuất bỏ một bước fraud check để giảm latency, hard policy chặn; chỉ sau đó optimizer mới cân nhắc trade-off hợp lệ. Không được biến chuyện này thành “model chấm điểm chọn mục tiêu”.

### Priority arbitration

1. Hard constraints trước (bảo mật, pháp lý, ownership, approval, ngân sách).
2. Phân loại sự cố tức thời và mức độ nguy hiểm.
3. Ưu tiên theo goal charter do người thiết lập (ví dụ critical customer SLO trước technical debt bình thường).
4. Nếu hai Goal cùng cấp conflict, tạo `GoalConflict` có bằng chứng và lựa chọn, yêu cầu human owner quyết định; không tự đổi SLO.
5. Ghi decision + phiên bản goal + timestamp để audit.

## 3. Goal lifecycle

`DRAFT → VALIDATING → ACTIVE → DEGRADED → SUSPENDED → CLOSED`.

- `DRAFT`: mô tả chưa đạt schema, chưa đủ nguồn đo.
- `VALIDATING`: owner và measurement checks; chạy shadow observation để kiểm tra SLI.
- `ACTIVE`: có quyền phát hiện opportunities trong scope.
- `DEGRADED`: tín hiệu thiếu/stale; chỉ điều tra read-only, không tự tăng quyền.
- `SUSPENDED`: chủ sở hữu tạm dừng, tất cả mission write-side bị tạm dừng/thu hồi token.
- `CLOSED`: đóng theo lý do, lưu bằng chứng và archival. Goal có thể reopen bằng phiên bản mới.

## 4. Goal-to-Mission decomposition

Không biến một goal thành một prompt vô hạn. Loop theo chu kỳ:

1. Load goal, phiên bản policy và snapshot observations.
2. Kiểm tra điều kiện hoạt động, metric freshness, budget/owner.
3. Sinh các candidate opportunities, dedup với mission đang chạy.
4. Ước tính impact/time/cost/risk với khoảng bất định.
5. Qua policy và portfolio scheduler.
6. Cấp mission token có giới hạn; không sửa goal charter từ mission.
7. Sau completion, cập nhật evidence/measurement; nếu chưa thể đo outcome, đánh dấu `PENDING_OUTCOME`.

## 5. Các lỗi thiết kế Goal OS

- **Goal drift:** AI diễn giải “ổn định” thành “không release”. Chống bằng metric + guardrails + change control.
- **Goodhart:** tối ưu chỉ số test coverage bằng test vô nghĩa. Chống bằng independent quality assessment và counter-metrics.
- **Stale objectives:** chiến lược doanh nghiệp đổi nhưng goal không đổi. Cần owner review định kỳ và TTL.
- **Conflicting ownership:** repository có nhiều team. Mọi thay đổi ngoài scope cần quyền mới.
- **Silent metric outage:** không đo được không có nghĩa đạt mục tiêu.
- **Goal starvation:** tối ưu những goal dễ đo, bỏ goal không có telemetry. Cần coverage score và chủ sở hữu xác nhận thiếu dữ liệu.

## 6. Goal OS UI/API

- `POST /goals` (owner-only), `POST /goals/{id}/activate`, `PATCH /goals/{id}` version-check, `POST /goals/{id}/suspend`, `GET /goals/{id}/evidence`, `GET /goals/conflicts`.
- Trang Goal Detail: status, metric actual vs target, uncertainty, asset scope, resource budget, opportunity queue, mission ledger, guardrails, ownership, last reviewed.
- Dashboard không hiển thị “99.9%” nếu mẫu dữ liệu thiếu; luôn hiển thị window và sample count.

## 7. Acceptance criteria

Một goal không được ACTIVE nếu thiếu owner, scope, ít nhất một metric/observable criterion hoặc policy mode. Khi metric bị stale, không mission write-side mới. Khi owner revoke, tất cả tool credentials liên quan bị thu hồi, mission được đưa vào trạng thái an toàn.
