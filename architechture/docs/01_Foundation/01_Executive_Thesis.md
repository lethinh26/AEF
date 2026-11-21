# 01 — Luận đề kiến trúc, giá trị và logic khác biệt

## 1. Vấn đề gốc

Tự động hóa coding chuyển nút thắt từ **năng lực tạo code** sang các năng lực: (a) biết chọn việc gì, (b) xác định đúng phạm vi và ràng buộc, (c) phối hợp thay đổi trên nhiều hệ thống, (d) tin được vào kết quả, (e) học xuyên thời gian. Một coding agent xuất sắc trong (c) đối với một nhiệm vụ cụ thể vẫn có thể làm cả tổ chức kém đi nếu chọn sai việc, tạo ra lỗi bảo trì hoặc không thấy tác động vận hành.

AEO chuyển đơn vị quản lý từ `prompt/task/session` sang `goal/service/outcome/capability`, và từ `completion report` sang `evidence-backed accountability`.

## 2. Định nghĩa có thể kiểm chứng

**AEO** = cơ chế tiếp nhận **goal charter** do người có thẩm quyền cấp, quan sát các tài sản được giao trong thời gian dài, giữ một **world model có nguồn gốc**, đưa ra quyết định về **opportunity portfolio**, cấp các **mission có ranh giới**, thi hành qua các năng lực phù hợp, kiểm chứng độc lập trước/sau thay đổi, cập nhật tri thức bằng thực nghiệm, và cung cấp cho con người **quyền giám sát, thu hồi, đình chỉ và phủ quyết**.

AEO không có quyền tự đặt mục tiêu tối hậu, tự tăng ngân sách, hay thay đổi hiến chương quyền hạn. Mọi phạm vi trách nhiệm đều do chủ sở hữu con người xác lập.

## 3. Năng lực A–B–C–D

| Chiều | Câu hỏi gốc | Output bền vững | Failure điển hình |
|---|---|---|---|
| B — Self-Driving | Việc nào đáng làm tiếp theo? | Findings, opportunities, justified missions | Alert spam, ticket factory, sửa không cần thiết |
| A — Self-Evolving | Sau kết quả này, tổ chức thực sự học được gì? | Versioned, evaluated capabilities | Ghi nhớ lỗi sai; overfit benchmark |
| C — Generative Production | Làm sao tạo/biến đổi artifact được kiểm chứng? | Code, modules, scripts, deployed changes, proofs | Code chạy nhưng không đáp ứng mục tiêu |
| D — Organization | Phân bổ quyền, ngân sách, sự chú ý và trách nhiệm thế nào? | Goal charter, portfolio, governance, accountability ledger | Agent tự đặt mục tiêu; mất kiểm soát chi phí |

B vận hành theo tín hiệu và mục tiêu; C là năng lực tạo tác; A cải thiện quy trình; D đảm bảo cả ba tạo ra **một tổ chức liên tục** chứ không phải ba ứng dụng ghép.

## 4. Nguyên lý đột phá được đề xuất

### 4.1. Outcome-first, not task-first

Mỗi mission phải có đường liên kết: `human-authorized goal → evidence-backed opportunity → expected outcome → mission → verification → post-deployment observation`. Mission “sửa code cho sạch” không đủ nếu không chứng minh một mục tiêu cụ thể. Các nhiệm vụ phục hồi có thể ưu tiên giảm rủi ro ngay khi chưa đo được hiệu quả cuối cùng; hồ sơ phải thể hiện độ bất định.

### 4.2. World model có độ tin cậy, không phải truth database

Độ tin cậy và độ mới của tri thức luôn thay đổi. AEO phải biết `unknown`, `stale`, `disputed`, `inferred`, `verified` thay vì coi mọi mối quan hệ đều đúng. Một thiếu sót trong observability cũng là tín hiệu cần xử lý.

### 4.3. Decision có thể bị phản biện

Mỗi quyết định lưu: lựa chọn, lựa chọn đã bỏ qua, bằng chứng, chính sách, mức tự tin, chi phí dự kiến, chính sách thẩm quyền và lý do dừng. Audit sau này phải tái dựng được quyết định từ các đầu vào đã đóng dấu phiên bản.

### 4.4. Năng lực tái sử dụng mang theo điều kiện và bằng chứng

Capability gồm `applicability envelope`, các thao tác/asset, negative examples, test oracle, provenance, quyền chia sẻ và phiên bản. Không được đánh đồng “prompt thành công một lần” với capability có tính chuyển giao.

### 4.5. Autonomy có thể thu hồi ngay

Mỗi quyền tự chủ phải có vùng áp dụng, thời hạn, giới hạn số lần, ngân sách và điều kiện rút quyền. Các approval còn hạn phải ràng buộc với đúng phiên bản plan/diff/policy; khi đối tượng thay đổi approval hết hiệu lực.

## 5. Giá trị cạnh tranh có thể chứng minh

- **Opportunity precision:** tỷ lệ đề xuất thật sự đáng làm khi được chuyên gia đánh giá mù, bao gồm chất lượng của quyết định không hành động.
- **Outcome uplift:** thay đổi đáng kể, đã hiệu chỉnh biến gây nhiễu, đối với SLO, defect escape, toil hoặc kinh tế đơn vị.
- **Cross-project transfer:** cùng model, cùng thời gian/budget, capability registry cải thiện job chưa thấy ở project khác.
- **Reliability of autonomy:** tỷ lệ mission hoàn tất không can thiệp *và* không vi phạm policy *và* được verifier độc lập chấp nhận.
- **Human attention efficiency:** số phút giám sát hữu ích trên mỗi outcome, không chỉ số token hoặc PR.

## 6. Điều có thể thất bại

AEO có thể tạo ra vòng xoáy tự khuếch đại sai lầm: alert → chẩn đoán yếu → tạo mission → thay đổi → tín hiệu mới → thêm mission. Cần chốt quyền ở mọi vòng, deduplicate, nghiệm thu dựa trên test oracle độc lập, monitor hậu triển khai, rollback và circuit breaker. Không biến autonomy thành mục tiêu tự thân.

## 7. Ranh giới V0

**Đề xuất:** chọn `CI reliability + low-risk maintenance` trên 2–3 repo được cấp phép. Chưa nhắm production, dữ liệu khách hàng thật hay “tự sinh ứng dụng hoàn chỉnh”. Nên tạo một vòng kín có đánh giá: tín hiệu CI → finding → chọn opportunity → mission → branch/PR → test → kết quả → capability candidate. Đây là nền tảng mở rộng ra A–B–C.
