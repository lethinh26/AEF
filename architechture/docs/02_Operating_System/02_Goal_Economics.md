# 05 — Goal economics: đơn vị giá trị, rủi ro và giới hạn nguồn lực

## 1. Chi phí của một tổ chức không chỉ là tokens

`Total Mission Cost = model + compute + storage + CI + external APIs + human review + expected incident cost + maintenance`. Chi phí opportunity phát hiện nhưng không chọn cũng tồn tại (monitoring, analysis). Việc tận dụng capability có thể giảm model cost nhưng phát sinh verification cost.

Chia ba ngân sách:

- **Compute budget:** LLM requests, tokens, sandbox hours, CI minutes, network calls.
- **Risk budget:** loại tác động được chấp nhận, giới hạn blast radius, exposure data, rollback risk.
- **Attention budget:** phút review và số escalation mỗi đội có thể xử lý mỗi ngày.

Không quy đổi tất cả thành USD rồi dùng một score. Policy không thể mua bằng chi phí rẻ.

## 2. Lợi ích kỳ vọng và uncertainty

Đối với opportunity `i`, ước tính:

- `P_i(success)` có calibration từ dữ liệu nhiệm vụ tương tự; không dùng LLM confidence thô.
- `Benefit_i` theo outcome metric, khoảng dưới/trên.
- `Cost_i` dự báo p50/p90, gồm chi phí review và repair.
- `Harm_i` tình huống xấu nhất hợp lý, dựa threat model.
- `Delay_i` hậu quả nếu không làm ngay.

**Heuristic** xếp hạng *sau khi pass hard constraints*:

`priority_i = w1*ExpectedImpact + w2*Urgency + w3*TransferValue - w4*ExpectedCost - w5*RiskPenalty - w6*UncertaintyPenalty`.

Không lấy con số này làm truth. Weight do người cấp có version. Với dữ liệu thưa, chạy chế độ recommendation + human ranking; chỉ học trọng số sau khi đủ dữ liệu.

## 3. Phân bổ portfolio

Bài toán thực tế là tối ưu một danh mục dưới constraint:

`maximize Σ accepted_value_i` với điều kiện `Σ spend_i <= monthly_cap`, `Σ resource_i <= concurrency`, `risk_class_i ∈ allowed`, `no conflicting migrations`, `review_slots <= team_capacity`.

Bổ sung quan hệ nhiệm vụ: `depends_on`, `mutually_exclusive`, `blocks`, `same_service_lock`, `duplicate`. Có thể bắt đầu bằng greedy + rules; dùng solver nếu complexity và data justify.

## 4. Giá trị của không hành động

AEO phải biết khi nào `DEFER`, `OBSERVE`, `INVESTIGATE_ONLY`, `REJECT`, `EXECUTE`. `REJECT` cũng có lý do có thể kiểm toán. Tối ưu thanh toán khi p95 chưa thay đổi đáng kể nhưng traffic nhiễu có thể là công việc không đáng làm; quyết định đúng là lấy thêm evidence.

**Decision ledger** phải lưu candidate bị loại để tránh chỉ học từ người sống sót (*survivorship bias*).

## 5. Guardrails chống Goodhart

- Chỉ số `PR count` không phải outcome. `Tests green` chỉ là intermediate evidence.
- Nếu nâng coverage, kiểm tra mutation testing / test effectiveness trên mẫu, không chỉ dòng mã.
- Nếu giảm latency, theo dõi error rate, cost, data consistency.
- Nếu giảm cloud cost, theo dõi performance, durability, RTO/RPO.
- Nếu tăng autonomy, theo dõi incident, escalation overload và verifier false pass.

## 6. Kiểm toán cost

Record mỗi action: `provider_id, model_id, tokens_in/out, listed_unit_price, actual_billed_cost_if_available, estimation_method, sandbox_seconds, CI_minutes, human_review_minutes`.

Khi provider không cung cấp usage/cost đáng tin, dừng theo **hard request count / time / steps / sandbox CPU**, không giả vờ chi phí USD đã được thực thi chính xác. Cảnh báo budget model khi cost estimate unreliable.

## 7. Trường hợp tranh chấp

Hai goals cùng cần một migration DB khác nhau: scheduler không tự merge. Lock tài nguyên, tạo mission plan với precondition và owner approval. Nếu một mục tiêu bị giảm giá trị do thay đổi bối cảnh, re-evaluate portfolio, nhưng không hủy mission đang có side-effect chưa được an toàn hóa.

## 8. Bộ đo economics

- `cost_per_verified_outcome`, `time_to_verified_outcome`, `human_attention_per_outcome`.
- `unproductive_mission_rate`, `avoidable_opportunity_rate`, `false_alarm_review_minutes`.
- `expected_vs_actual_cost_calibration`, `p90_overrun`, `budget_violation_count`.
- `regression_cost_30d`, `capability_maintenance_cost`, `approval_wait_time`.

Mọi báo cáo phải chia theo loại task/độ khó/project, tránh so sánh sai. Không dùng giá trị kinh tế ước đoán để khẳng định đã tạo ROI thật.
