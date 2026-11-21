# 33 — Từ điển thuật ngữ và phân biệt dễ nhầm

| Thuật ngữ | Nghĩa chính xác trong AEO | Không phải |
|---|---|---|
| Goal | Mục tiêu được owner cấp quyền, có metric/guardrail/scope | Prompt dài hạn không giới hạn |
| SLI | Chỉ số quan sát chất lượng dịch vụ | SLO mục tiêu |
| SLO | Mức chỉ số mong đạt trong window | Cam kết SLA pháp lý mặc định |
| World Model | Tập claim có kiểu, thời gian và provenance về hệ thống | Chỉ vector database |
| Observation | Sự kiện/dữ liệu đến từ nguồn | Kết luận nguyên nhân |
| Claim | Mệnh đề có nguồn và trạng thái xác minh | Chân lý vĩnh viễn |
| Finding | Giả thuyết/vấn đề có evidence | Ticket được tự động phê duyệt |
| Opportunity | Hành động có thể tạo giá trị với lý do rõ | Bất kỳ alert nào |
| Decision | Lựa chọn có alternatives, policy và budget | Văn bản LLM “nên làm” |
| Mission | Nhiệm vụ có hợp đồng, quyền, ngân sách, oracle | Chat session |
| Warrant | Quyền có ranh giới để chạy một mission | Quyền root của agent |
| Tool Permit | Cho phép cụ thể cho một action có thời hạn | Tool schema mà model nhìn thấy |
| Capability | Quy trình/năng lực reusable có tests và applicability | Prompt template không đánh giá |
| Applicability Envelope | Điều kiện một capability được phép/đã chứng minh áp dụng | Từ khóa tương tự |
| Evidence | Artifact/record nguồn và verifier có thể kiểm tra | Lời tuyên bố của executor |
| Provenance | Dấu vết nguồn, phiên bản, công cụ và điều kiện tạo | Bằng chứng nội dung đúng |
| Verification | Kiểm tra tiêu chí kỹ thuật theo oracle | Đo giá trị sau triển khai |
| Outcome | Tác động quan sát theo Goal | PR merge thành công |
| Trust Tier | Phân loại mức đánh giá của capability | Quyền tự động cấp rộng |
| Shadow Mode | Chỉ quan sát và đề xuất, không sửa repo | Chạy ngầm có quyền write |
| Counterfactual | Giả định về kết quả nếu quyết định khác | Thực tế đã quan sát |
| Baseline | Phương án đơn giản hơn dùng để so sánh | Kết quả mục tiêu mong muốn |
| Kill Switch | Cơ chế dừng/thu hồi quyền | Lệnh prompt “please stop” |
| Hysteresis | Hai ngưỡng bật/tắt tránh dao động | Retry nhiều lần |
| Idempotency | Lặp cùng hành động không tạo tác dụng phụ mới | Exactly-once toàn hệ thống |
| Policy Plane | Hệ thống cấp/deny quyền độc lập | Safety paragraph trong system prompt |
| OPA | Policy-as-code engine tùy chọn | Phần bắt buộc của AEO |
| MCP | Giao thức tích hợp tool/resource | Cơ chế tự bảo đảm an toàn |
| DORA | Bộ metrics delivery performance | KPI duy nhất của AEO |

## Phân biệt quan trọng

- **Knowledge vs Capability:** biết một kỹ thuật khác với có quy trình tái sử dụng và test đáng tin.
- **Success vs Verified Success:** có output khác với output qua kiểm chứng độc lập.
- **Verified Success vs Outcome:** PR pass khác với khách hàng nhận lợi ích.
- **Autonomy vs Authority:** agent có thể tự lập kế hoạch nhưng không đồng nghĩa có quyền sản xuất tác động ngoài.
- **Learning vs Training:** organizational learning có thể bằng eval/skills/routing mà không fine-tune trọng số.
- **Accuracy vs Calibration:** có bao nhiêu dự đoán đúng khác với confidence có phản ánh tỷ lệ đúng không.
- **Reliability vs Availability:** hệ thống luôn online chưa chắc kết quả của nó an toàn.
