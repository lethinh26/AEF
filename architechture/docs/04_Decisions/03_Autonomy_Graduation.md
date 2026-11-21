# 11B — Autonomy Graduation: tăng quyền theo độ chín đã chứng minh

## 1. Một tổ chức không có mức tự chủ cố định cho mọi nhiệm vụ

Một repository có thể an toàn cho `docs auto-PR` nhưng không an toàn cho `database migration`. Do đó autonomy profile phải tính theo tổ hợp: `tenant + asset + mission_type + risk + capability_version + verifier_level + recent incident history`.

## 2. Autonomy ladder [DESIGN]

- **A0 Observer:** không có side effect, chỉ thu tín hiệu.
- **A1 Recommender:** tạo findings/opportunities/missions đề xuất, chờ người khởi chạy.
- **A2 Branch Producer:** tự tạo branch, patch, tests, PR; không merge.
- **A3 Staging Operator:** deploy staging/canary sau kiểm chứng theo policy và owner approval nếu cần.
- **A4 Limited Production Operator:** chỉ tác vụ đã pre-approve có giới hạn blast radius, canary, rollback, strong verifier.
- **A5 High-trust Autonomous Operations:** tầm nhìn dài hạn, **không mặc định là mục tiêu cần đạt**; mỗi loại hành động vẫn có giới hạn riêng.

Đừng “gamify” thành thang level buộc phải tăng. A2 có thể là cấu hình tối ưu cho hầu hết hệ thống với rủi ro cao.

## 3. Graduation criteria

Một profile muốn từ A1→A2:

1. Phải có fixtures held-out có chất lượng và đa dạng task.
2. `Unauthorized action count = 0` trong security suite.
3. Independent tests phát hiện được lỗi giả lập quan trọng.
4. Chi phí bounded; không runaway loop.
5. Có owner nhận trách nhiệm và procedure revoke.
6. Có đủ dữ liệu actual outcomes trong phạm vi cấp quyền.

A2→A3 cần staged deployments, rollback rehearsals, deployment identity separation. A3→A4 chỉ khi owner thống nhất rõ nghiệp vụ/rủi ro, và không với destructive operations.

## 4. Autonomy decay / revocation

Một capability đang A2 nhưng xảy ra false success nghiêm trọng → hạ A1; tool connector bị nghi compromised → A0; metrics stale → A0/A1. Quyền tự chủ phải **giảm nhanh** khi có tín hiệu rủi ro, **tăng chậm** khi đủ bằng chứng. Có cooldown, owner signoff và re-certification.

## 5. Trust score vs authority

Trust score có thể hỗ trợ routing/ưu tiên review, nhưng không thay policy. Một score trung bình 0.99 không cho phép xóa production DB. Autonomy authority phải là discrete policy decision với explicit constraints.

## 6. Blast-radius budget

Đề xuất `max_changed_services`, `max_files_changed`, `max_user_cohort`, `max_deploy_regions`, `allowed_data_classes`, `max_rollback_delay`; giới hạn phù hợp loại Mission. Với codebase có kiến trúc monolith, số file đổi không phản ánh impact hoàn toàn, cần kết hợp dependency/contract tests.

## 7. Ví dụ nguy hiểm khi không có graduation

AEO xử lý thành công 50 typo fixes và tự cho phép merge payment code. Đây là sai vì evidence không chuyển giao giữa risk classes. Một benchmark để tăng quyền phải gần với hành động được cấp, với negative tests và owner approval.

## 8. Metrics

`autonomous_verified_success_by_tier`, `safety incident by tier`, `review load by tier`, `time-to-revoke`, `false graduation decisions`, `post-promotion regressions`, `effective blast radius`.
