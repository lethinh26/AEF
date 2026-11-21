# 20B — Counterfactual learning: học từ những việc không làm, không chỉ từ thắng lợi

## 1. Ba thiên lệch cơ bản

**Selection bias:** AEO ưu tiên job dễ, rồi kết luận completion rate cao. **Survivorship bias:** chỉ lưu missions thành công, mất bài học từ thất bại. **Feedback leakage:** model học từ hidden test hoặc sản phẩm output rồi bị đánh giá trên chính trường hợp đó.

Một Evolution Engine không chống ba điều này có thể làm tổ chức ngày càng tự tin nhưng thực chất kém đi.

## 2. Decision counterfactuals

Mỗi quyết định phải lưu alternatives. Ví dụ chọn sửa CI flake thay vì tối ưu latency. Sau 7 ngày, AEO xem outcome của lựa chọn đã làm, đồng thời thu observed changes của latency. Nhưng **không thể biết chắc** kết quả nếu đã chọn task khác: counterfactual chỉ ước lượng theo proxy/mô phỏng. Khi báo cáo cần gắn `estimated_not_observed`.

## 3. Learning from non-actions

Chọn `DO_NOTHING` cũng nên được follow-up: vấn đề có tự hết, trở nặng, hay đã bị xử lý bởi người khác? Nếu trầm trọng, xem prior evidence và cost-of-delay calibration. Nhưng không gắn nhãn “quyết định sai” chỉ dựa outcome tệ nếu evidence lúc đó thiếu và policy không cho phép hành động.

## 4. Replay without future leakage

Dựng lịch sử sự kiện theo thời gian. At decision time t, model chỉ được đọc world snapshot/evidence có `observed_at <= t`; không cho đọc postmortem kết luận root cause viết ở t+3 ngày. Nếu không, replay chứng minh model biết tương lai chứ không chứng minh decision intelligence.

## 5. Transfer evaluation

Một capability lấy từ repo CRM A và test ở e-commerce B cần:

- Domain invariants tương đồng, code implementation không copy.
- Disjoint task fixtures và project-level splits.
- Same model version và token/time budgets.
- Hidden tests đảm bảo regression/edge cases.
- Report negative transfer with failure modes, not just average uplift.

Nếu uplift chỉ ở job có tên giống nhau nhưng context khác, xem evidence of spurious matching; thêm applicability constraints hoặc retire.

## 6. Learning from incidents

Sau incident: capture root cause được owner xác minh, causal chain, what-if alternatives, policy gaps, runbook gaps, cost, blast radius. LLM có thể đề xuất capability candidate hoặc new oracle. Tuy nhiên remediation of policy chỉ đi qua separate human governance path; chưa bao giờ auto apply.

## 7. Causal evaluation options

Nếu có lượng job đủ, randomize `capability enabled/disabled` trên low-risk tasks. Nếu ít data, paired sandbox eval, giữ cùng environmental snapshot; không dùng live customers làm đối tượng thử nghiệm không được cấp phép. Outcome production attribution cần xác minh bằng canary/control cohort hoặc công cụ causal phù hợp; nếu không, ghi inconclusive.

## 8. Learning budget and entropy

Learning cũng có chi phí: extraction, eval, registry curation, knowledge expiry, incident risk. Đừng extract mọi completion. Chỉ tạo candidate nếu pattern lặp đủ, có impact hoặc reusable invariant có giá trị; budget riêng cho Evolution Lab và giới hạn số experiments đồng thời.

## 9. Falsification gate

Nếu `capability_v2` có 15% success giảm trên nhóm low-resource repos, không promote đại trà dù average cost giảm. Có thể giới hạn applicability, thêm negative example, hoặc quarantine. Mỗi lần promotion ghi rõ **where it helps, where it hurts, where unknown**.
