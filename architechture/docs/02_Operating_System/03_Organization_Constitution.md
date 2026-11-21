# 06 — Hiến chương vận hành: quyền lực, trách nhiệm, chủ quyền con người

## 1. Vì sao cần “hiến chương”?

Một AEO có thể tự tìm việc sẽ tự tạo *đường cấp quyền* từ tín hiệu đến công cụ. Nếu không có hiến chương, hệ thống dễ hợp thức hóa hành vi bằng chuỗi suy luận tự tạo. Hiến chương là tập quy tắc pháp lý/kỹ thuật/đạo đức vận hành **ngoài model**, được ký phiên bản và không sửa bởi runtime agents.

## 2. Cấp quyền theo tầng

1. **Organization Charter:** đội ngũ/đơn vị sở hữu AEO, phạm vi, dữ liệu được phép, yêu cầu tuân thủ, mức rủi ro.
2. **Goal Charter:** mục tiêu do owner duyệt, assets, đo lường, budget, autonomy ceiling.
3. **Mission Warrant:** nhiệm vụ cụ thể với scope/repo/branch, tool allowlist, expiry, spending, review.
4. **Action Permit:** quyền nhất thời cho từng tool call, ràng buộc với command/resource/args hash, có thể thu hồi.

Quyền càng xuống thấp càng hẹp, **không được tăng** (monotonic narrowing). Nếu cần mở rộng, quay lại người có thẩm quyền.

## 3. RACI tối thiểu

| Quyết định | Goal owner | Security/Platform | AEO Planner | Executor | Verifier |
|---|---|---|---|---|---|
| Đặt SLO/budget | A/R | C | I | I | I |
| Kích hoạt goal | A | C | R chuẩn bị | I | C |
| Chọn mission low-risk | I | Policy gate | R | I | C |
| Cấp quyền production | A | A/C theo loại | Không | Không | C |
| Chỉnh policy an toàn | C | A/R | Không | Không | Không |
| Đánh giá output | I | C | I | C | R độc lập |
| Promote capability | A hoặc delegated | Security gate | Propose | C | R evidence |

R=Responsible, A=Accountable, C=Consulted, I=Informed. Không để LLM tự đóng cả hai vai trò A và R cho hành động rủi ro cao.

## 4. Rights and tenancy

Dù nội bộ, **project boundaries** phải có từ V0. Mỗi repository được gắn legal owner, dữ liệu phân loại (public/internal/confidential/restricted), region retention và policy sử dụng dữ liệu với model provider. Capability không được chứa code/snippet/ticket của khách hàng khác trừ khi quyền cho phép. Tách `generalized pattern` khỏi `proprietary example` và yêu cầu review trước publish cross-project.

## 5. Approval semantics

Approval phải có:

```yaml
approval:
  subject: mission/m_123
  action: merge_pr
  resource: repo/shop-api/main
  diff_sha256: '<sha256>'
  plan_version: 4
  policy_version: 9
  requested_by: aeo
  approved_by: '<human_principal>'
  expires_at: '<timestamp>'
  single_use: true
```

Phê duyệt mất hiệu lực nếu `diff`, target branch, environment, impact class hoặc policy đổi. Approval không phải token vĩnh viễn.

## 6. Quyền từ chối và giám sát

- **Stop**: chặn tạo mission mới, hủy pending tool permits, yêu cầu sandbox dừng.
- **Quarantine**: cách ly provider, capability, tool connector hoặc repo đang bị xâm nhập.
- **Freeze**: tiếp tục quan sát read-only nhưng không sửa/triển khai.
- **Emergency rollback**: chính sách và quyền đã được phân loại; không được tự xóa dữ liệu để “rollback”.
- **Appeal**: human có thể điều chỉnh kết quả policy bằng quy trình ngoại lệ có audit, không bằng prompt.

## 7. Mục tiêu tự cải tiến nhưng không tự mở quyền

AEO có thể đề xuất `new capability`, `new policy candidate`, `new routing heuristic`, nhưng candidate về policy phải được test và duyệt bởi owner độc lập. Evolution Lab không được có credential production. Promotion cần evidence gate, rollback và thời gian giám sát.

## 8. Chu kỳ trách nhiệm

- Hàng ngày: review exceptions, SLO data freshness, anomalous spending.
- Hàng tuần: quality calibration, review autonomous misfires, unresolved findings.
- Hàng tháng: goal owner review, risk audit, capability retirement, retention requests.
- Hàng quý: red-team/chaos exercises, rights audit, threat model & value hypothesis review.

Đây là tần suất tham khảo, không phải chuẩn bắt buộc; scale theo mức rủi ro thực tế.
