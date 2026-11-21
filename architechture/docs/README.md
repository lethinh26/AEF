# AEO — Autonomous Engineering Organization

**Bộ hồ sơ kiến trúc nghiên cứu & triển khai | phiên bản 1.0 | 2026-11-21**  
**Ngôn ngữ:** Tiếng Việt. **Độc giả:** nhà sáng lập, kiến trúc sư, lead kỹ thuật, SRE, AI engineer, QA, security và người quản trị vận hành.

> **Luận đề:** AEO không phải “multi-agent coding platform”. AEO là một hệ thống chịu trách nhiệm có giới hạn đối với các **mục tiêu kỹ thuật tồn tại dài hạn**, duy trì nhận thức về các hệ thống được giao, chủ động chọn việc đáng làm, tổ chức thực thi, thu bằng chứng kết quả và thử nghiệm cải tiến năng lực. AI là bộ phận suy luận/thi hành có thể thay thế; quản trị, trạng thái và bằng chứng thuộc về hệ thống.

## Đọc thế nào?

- **15 phút:** `01_Foundation/01_Executive_Thesis.md`, `01_Foundation/02_First_Principles.md`, `10_Implementation/01_Research_Program.md`.
- **2–3 giờ:** đọc các hồ sơ 02–08 theo thứ tự.
- **Xây V0:** `10_Implementation/02_MVP_Architecture.md`, `10_Implementation/03_Roadmap_and_Team.md`, `10_Implementation/04_Acceptance_Test_Matrix.md`, `examples/`.
- **Phản biện thiết kế:** `01_Foundation/03_Open_Questions_ADRs.md`, `08_Governance/03_Threat_Model.md`, `11_Appendices/02_Failure_Atlas.md`.

## Bản đồ tài liệu

| Khu vực | Hồ sơ | Ý nghĩa |
|---|---|---|
| 01 Foundation | Tầm nhìn, nguyên lý, phản biện & ADR | Phân biệt đột phá thực với đóng gói lại coding agent |
| 02 Operating System | Goal OS, Goal economics, organizational constitution | Nhà máy **tại sao** làm và được phép làm gì |
| 03 Intelligence | World Model, ingestion, opportunity discovery | Nhà máy **biết** điều gì, tin đến đâu |
| 04 Decisions | Decision intelligence, portfolio scheduler | Nhà máy **chọn** việc nào và phân bổ tài nguyên |
| 05 Missions | Mission protocol, tổ chức động, long-horizon | Nhà máy **biến quyết định thành hoạt động** |
| 06 Production | Runtime, capability product line, verification | Nhà máy **thực thi** và bàn giao đáng tin cậy |
| 07 Evolution | Memory, capability evolution, experimentation | Nhà máy **tích lũy và cải thiện** bằng chứng |
| 08 Governance | Policies, security, threat model, risk | Nhà máy **không vượt quyền** |
| 09 Platform | Data, events, API, observability, reliability | Các khối kỹ thuật liên kết thành hệ thống thực |
| 10 Implementation | Chương trình nghiên cứu, MVP, roadmap, test matrix | Cách xây và chứng minh giá trị |
| 11 Appendices | Từ điển, failure atlas, nguồn tham khảo | Tra cứu và phản biện |
| examples | Hợp đồng YAML, policy và luồng sự kiện mẫu | Vật liệu cho thiết kế & prototype |

## Phân loại độ chắc chắn

- **[DESIGN]** Lựa chọn thiết kế đề xuất của bộ tài liệu, chưa phải chân lý hay chuẩn công nghiệp.
- **[KNOWN]** Kỹ thuật/khuôn khổ phổ biến được dẫn nguồn; vẫn phải kiểm tra khi triển khai.
- **[HYPOTHESIS]** Giả thuyết giá trị cần thực nghiệm trước khi đầu tư lớn.
- **[EXAMPLE]** Số liệu, ngưỡng, thời lượng và tình huống minh họa, **không phải dự báo**.
- **[OPEN]** Chưa có đủ bằng chứng hoặc phụ thuộc bối cảnh công ty.

## Giả định đầu vào đã biết

- Đội dev 5–15 người, làm nhiều loại hệ thống (CRM, thương mại điện tử, tích hợp, scripts...).
- Đã sử dụng AI coding tools thường xuyên; mong muốn **tự chủ trong ranh giới quyền**, chỉ gọi người khi ngoại lệ.
- Dùng nội bộ trước; muốn mở rộng/thương mại hóa sau.
- AI backend được truy cập qua **OpenAI-compatible `base_url`, `api_key`, `model`**, không phụ thuộc Codex CLI.
- Hướng sản phẩm đồng thời có A: Self-Evolving, B: Self-Driving, C: Generative Production; D: một tổ chức kỹ thuật số vận hành theo Goal/Outcome.

## Những điều tài liệu này KHÔNG cam kết

Không khẳng định rằng: AEO hiện đã tồn tại như sản phẩm hoàn thiện; có thể tự động hóa tất cả loại code; tự học đồng nghĩa tăng chất lượng; kết quả của mô phỏng chứng minh tác động production; các ngưỡng mẫu là mục tiêu chuẩn; thay nhiều nhân viên bằng agent ngay lập tức là hợp lý. Trọng tâm là **kiến trúc có giả thuyết kiểm chứng được**.

## Định nghĩa thành công cốt lõi

Một AEO tốt phải qua **ba phép thử đồng thời**: (1) phát hiện được công việc đáng làm mà không cần ticket; (2) tạo ra kết quả kỹ thuật được chứng minh độc lập và tuân thủ quyền; (3) cải thiện hiệu năng trên công việc *chưa thấy* nhờ năng lực tích lũy mà không làm giảm chất lượng. Nếu chỉ qua (2), đó chủ yếu là coding automation.

## Trình tự làm thật

1. Xây **shadow observer** trên 2–3 repo và pipeline CI, không quyền write.
2. Kiểm tra chất lượng cơ hội/độ chính xác thế giới và khả năng *không hành động*.
3. Tạo mission read-only → branch-only, có sandbox và independent verification.
4. Tạo thử nghiệm tái sử dụng capability qua dự án khác; so với baseline một coding agent cùng model và cùng ngân sách.
5. Chỉ mở rộng khi gate chất lượng, an toàn, economics đạt chuẩn.

**Nguồn và phần đối chiếu với chuẩn ngoài:** xem `11_Appendices/03_References.md`.
