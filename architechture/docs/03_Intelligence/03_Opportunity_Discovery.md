# 09 — Opportunity Discovery: từ sự kiện đến đề xuất đáng làm

## 1. Bốn lớp phân tích

1. **Signal:** sự kiện quan sát được, không tự mang phán đoán; ví dụ 12 CI failures.
2. **Pattern:** chuỗi/bất thường được gom nhóm, ví dụ 9 failures có cùng stacktrace trên một commit.
3. **Finding:** giả thuyết về nguyên nhân/tác động, có evidence & competing hypotheses.
4. **Opportunity:** hành động khả thi liên quan Goal, có expected value, downside, cost/risk và điều kiện không nên làm.

Một Finding chưa chắc dẫn đến Opportunity. Một Opportunity có thể chỉ là “thu thập thêm evidence”.

## 2. Candidate generation ba nguồn

**Rule-based:** SLO burn-rate, CI fail >= threshold, dependency published risk, ownership missing. **Statistical:** changepoint, trend deviation, burst detection có kiểm soát seasonality. **LLM-assisted:** đọc cụm log/PR/test report và đề xuất hypothesis, nhưng phải trích evidence đã có id và timestamp. Kết quả model được coi là candidate chưa xác minh.

## 3. Hypothesis ledger

```yaml
finding:
  id: f_102
  observation_ids: [evt_01, evt_05, evt_08]
  hypothesis: 'CI failure có thể do dependency drift'
  alternatives:
    - 'flaky integration test'
    - 'CI worker image thay đổi'
  confidence_band: low
  disconfirming_tests:
    - 'rerun pinned image on same commit'
    - 'compare lockfile hash and artifacts'
  state: INVESTIGATING
```

Không cần xác suất chính xác giả tạo. Giai đoạn đầu dùng ordinal `low/medium/high` và evidence strength rubric; hiệu chỉnh theo reviewer labels.

## 4. Opportunity Contract

Các trường bắt buộc:

- `goal_ids`, `finding_ids`, `asset_scope` và `candidate_action`.
- `expected_outcome`, `negative_outcomes_to_watch`.
- `why_now`, `evidence_refs`, `missing_evidence`.
- `estimated_effect`, `time_cost_band`, `financial_cost_band`, `reversibility`.
- `risk_class`, `proposed_autonomy`, `assumptions`, `review_by`.
- `dedup_key`, `expiry`, `status` (`PROPOSED/NEEDS_EVIDENCE/DEFERRED/ACCEPTED/REJECTED/EXPIRED`).

## 5. Cơ chế phản đề

Cho mỗi candidate vượt ngưỡng impact:

- Liệt kê **ít nhất hai** giả thuyết thay thế có thể giải thích cùng tín hiệu.
- Xem có dữ liệu nào *phủ định* giả thuyết chính.
- Xác định quan hệ tương quan vs tác động nhân quả.
- Kiểm tra nếu nguyên nhân nằm ngoài code (dependency provider outage, cloud env, data quality).
- Nếu uncertainty cao, chỉ tạo `investigation mission` read-only.

LLM tự phản biện có thể hữu ích nhưng không thay thế test độc lập hay telemetry.

## 6. Dedup, cooldown, hysteresis

Hệ thống chủ động phải biết **không tự phản ứng liên tục**. Thiết kế:

- **Dedup:** cùng nguồn, cùng root-cause candidate, cùng asset và time bucket.
- **Cooldown:** sau mission thất bại, tạm ngừng tái kích hoạt theo threshold.
- **Hysteresis:** ngưỡng bật/tắt khác nhau để tránh trạng thái dao động.
- **Suppression:** maintenance window, test rerun, known incident.
- **Reopen:** khi có bằng chứng mới đủ mạnh hoặc owner override.

## 7. Đo chất lượng phát hiện

`Precision@k` của danh sách candidates review, `false positive / asset-week`, `missed critical opportunities`, `time_to_detection`, `time_to_worthy_opportunity`, `discovery_cost`, `human triage minutes`. Dùng blind reviewer với nhãn `worth acting`, `worth investigating`, `not worth acting`, `not enough evidence`; đo inter-rater agreement.

Không thể tính recall nếu không có tập gold opportunities. Tạo bộ incident lịch sử + synthetic fault injection có giới hạn; luôn tách train/dev/held-out.

## 8. Ví dụ phân tích lỗi checkout

- **Observation:** p95 > 400ms trong 30 phút, error rate không đổi.
- **Hypotheses:** database lock; inventory external timeout; load spike; trace sampling artifact.
- **Evidence:** 43 traces cho thấy stock lookup có duration cao; deployment inventory 20 phút trước.
- **Decision trước mắt:** điều tra bằng query và so sánh trace trước/sau deploy; **không** triển khai sửa code trực tiếp.
- **Opportunity sau điều tra:** xác minh một index query không được dùng do plan thay đổi; tạo mission benchmark trên staging.

Mọi con số trong ví dụ là **[EXAMPLE]**; không kết luận root cause nếu không có phép thử.

## 9. Các failure mode đặc biệt

**Alert-driven busywork:** AEO xử lý mọi cảnh báo thay vì mục tiêu. **Overdiagnosis:** suy diễn nguyên nhân từ correlation. **Severity inflation:** tự gắn high để giành tài nguyên. **Duplicate cascades:** một dependency lỗi tạo nhiều missions. **Fix oscillation:** hai agents liên tiếp sửa theo hướng ngược. **Evidence poisoning:** log giả do đối tượng ngoài. Mỗi mode cần metric/guardrail và test riêng.
