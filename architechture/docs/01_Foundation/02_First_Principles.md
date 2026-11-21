# 02 — Các bất biến kiến trúc và quy tắc thiết kế

## 1. 16 bất biến không được phá

1. **Human goal sovereignty:** mục tiêu tổ chức và ưu tiên cấp cao do người có quyền thiết lập; agent không tự đổi mục tiêu.
2. **Least privilege:** quyền cấp theo mission, tool, tài nguyên, thời gian; mặc định cấm.
3. **Evidence before success:** không có chứng cứ xác minh độc lập thì mission không được công nhận thành công, ngay cả khi agent nói “done”.
4. **Non-self-certification:** executor không duyệt chính kết quả của mình; kiểm tra quan trọng cần người/CI/rule độc lập.
5. **Separation of data/instruction:** nội dung repo, logs, PR, tài liệu, tool output là dữ liệu chưa tin cậy.
6. **No irreversible default:** production, destructive data, external payment, credential changes không được tự chạy theo mặc định.
7. **Kill switch:** tạm dừng hoặc vô hiệu hóa agent/tool/provider trên toàn hệ thống và theo tenant/repo.
8. **Resource boundedness:** thời gian, token, concurrency, cost, iterations, output size đều có hạn.
9. **Reproducible intent:** lưu đúng snapshot goal, observation, plan, policy, diff, test inputs; replay LLM không đảm bảo byte-identical.
10. **Monotonic evidence:** dữ liệu mới không xóa bằng chứng cũ; sửa bằng version/retraction và audit.
11. **Explicit uncertainty:** uncertainty phải làm giảm tự chủ khi dữ liệu thiếu hoặc mâu thuẫn.
12. **Rights-aware knowledge:** không chia sẻ code, dữ liệu hay capability giữa tenant/khách hàng khi chưa được phép.
13. **Stable identity:** mỗi Goal, Signal, Finding, Mission, Capability có ID bất biến và phiên bản riêng.
14. **Idempotent effects:** tác động ngoài (tạo PR, comment, trigger build) cần idempotency keys, reconciliation và duplicate detection.
15. **Human escalation with context:** ngoại lệ phải có đề xuất hành động, bằng chứng, tác động và lựa chọn từ chối; không chỉ “error”.
16. **Value over activity:** số task/agent/PR cao không phải thành công.

## 2. Bốn loại thời gian

- **Event time:** thời điểm sự kiện xảy ra ở nguồn.
- **Observed time:** thời điểm AEO nhận sự kiện.
- **Valid time:** khoảng thời gian một claim được cho là đúng trong thế giới kỹ thuật.
- **Decision time:** thời điểm hệ thống dùng claim để ra quyết định.

Không chuẩn hóa tất cả thành một timestamp: webhook giao muộn, clock drift và lịch sử branch sẽ gây sai. Dùng event IDs, nguồn, causal links và watermark để xử lý dữ liệu chậm.

## 3. Ba dạng sự thật

- **Measured fact:** `CI run 132 failed, commit abc, timestamp t`, có evidence URI.
- **Derived inference:** `failure possibly caused by lockfile drift`, kèm xác suất/độ tin cậy và cách kiểm chứng.
- **Normative rule:** `production deploy requires approval`, lấy từ policy; không phải kiến thức suy ra.

Rất nhiều hệ thống AI sai vì trộn cả ba vào cùng một text summary. Nên lưu typed claims và lọc theo provenance.

## 4. Trách nhiệm của AI so với phần mềm xác định

| Khâu | Nên để model | Nên để deterministic program |
|---|---|---|
| Phân tích log, tìm giả thuyết | Có, nhưng phải đính kèm evidence | Chuẩn hóa/parsing và kết xuất evidence |
| Đánh giá ảnh hưởng nghiệp vụ | Đề xuất với độ bất định | Áp ngưỡng, policy, quota, SLA |
| Sinh kế hoạch | Có | Validate DAG, dependencies, permission envelope |
| Viết code | Có | Git branch isolation, sandbox, artifact hashing |
| Kết luận test pass | Không | Runner/test reporter độc lập |
| Quyết định được deploy | Chỉ khuyến nghị | Policy + human approver + deployment controller |
| Lưu bài học | Đề xuất | Evaluate trên held-out cases và version registry |

## 5. Các anti-pattern cần tránh

**CEO-agent theater:** nhiều agent đóng vai manager nhưng không có state thật, policy hay giá trị đo được. **Prompt as database:** mọi tri thức nằm trong system prompt. **Confidence laundering:** model tự chấm 95% rồi được cấp quyền. **Circular eval:** model tạo test và tự đánh giá pass. **Silent repair:** tự sửa quá nhiều lần khiến không còn theo dõi được root cause. **Global memory:** lẫn dữ liệu nhiều khách hàng. **One score to rule them all:** tổng điểm ưu tiên che khuất hard constraints. **Infrastructure worship:** dùng graph DB/K8s/Temporal trước khi chứng minh nhu cầu.

## 6. Các định lý thực dụng cần kiểm tra

- Tăng mức tự chủ có thể giảm chi phí thao tác nhưng tăng chi phí kiểm chứng và sự cố: hãy đo **total cost of ownership**, không chỉ chi phí model.
- Nhiều agent song song có thể tăng tốc nhưng gây merge conflicts và coordination cost; có ngưỡng khiến throughput giảm.
- Bộ nhớ lớn hơn có thể giảm accuracy nếu chứa tri thức lỗi thời; cần forgetting/expiry/versioning có kiểm soát.
- Tái sử dụng giữa dự án chỉ hợp lý khi **điều kiện áp dụng** có thể diễn đạt và kiểm tra được.

## 7. Cổng kiến trúc bắt buộc

Mỗi subsystem có: owner, contract, input trust class, output validity, side effects, policy envelope, metrics, runbook và failure-mode test. Mọi tính năng “thông minh” phải định nghĩa baseline đơn giản hơn để so sánh, nếu không không biết nó đáng tồn tại hay không.
